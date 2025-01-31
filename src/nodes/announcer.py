import time

import src.common.globals as GLOB
from src.blockchain.block import Block
from src.blockchain.mempool import MemPool
from src.blockchain.transaction import Transaction
from src.common import protocol
from src.common.crypto import sign_text
from src.common.statistics import Statistics
from src.common.utils import log, random_delay
from src.nodes.processor import Processor


class Announcer(Processor):
    def __init__(self, config, pub_key=None):
        super(Announcer, self).__init__(config, pub_key)
        self.role = "Announcer"
        self.balance = GLOB.STAKE_AMOUNT
        self.mempool = MemPool(self)
        self.is_eligible = False
        self.active_endorsement_phase = False
        self.already_did = 0
        self.staking_expiry = GLOB.STAKE_EXPIRY
        self.staked_amount = 0
        self.seen_txs = {}
        self.candidate_blocks = {}
        self.local_blockchain = []
        self.received_blocks = {}
        self.last_block_creation = time.time()
        self.b3 = 0

    def stake(self, amount=GLOB.STAKE_AMOUNT):
        if self.balance >= amount:
            self.balance -= amount
            self.staked_amount += amount
            log('event', f"{self} stacked {self.staked_amount} PCs.")
            return True
        log('error', f"{self} insufficient staking funds.")
        return False

    def verify_stake(self):
        return self.staked_amount >= GLOB.STAKE_AMOUNT  # Staking requirement

    def lose_stake(self):
        if not self.verify_stake():
            self.staked_amount = 0
            log('warning', f"{self} has lost its stake for not meeting requirements.")

    def create_and_announce_candidate_block(self, network_delays=True):
        if Statistics.stop_now:
            return
        txs, size = self.mempool.select_top_transactions(by="tips", top=GLOB.BLOCK_SIZE)
        candidate_block = Block(self.pub_key, txs, size=size, block_state=GLOB.BLOCK_INIT)
        for tx in txs:
            tx.block = candidate_block
        candidate_block.compute_block_hash(self.config.endorse_threshold, confirmed=False)
        signature = sign_text(candidate_block.hash, self.prv_key)
        # endorse my block
        # candidate_block.endorsements[self.pub_key] = signature
        candidate_block.endorsements[self.port] = str(self)
        self.candidate_blocks[candidate_block.bid] = candidate_block
        self.received_blocks[candidate_block.bid] = {}
        Statistics.endorsements_messages[candidate_block.bid] = [True]
        self.active_endorsement_phase = True
        Statistics.endorsement_rate[candidate_block.bid] = {'endorsed': False, 'start': time.time()}
        log('log', f"{self} created candidate block: {candidate_block}.")
        msg = protocol.candidate_block_message(self.pub_key, candidate_block)
        if network_delays:
            random_delay(1)
        for r in self.registry:
            if r.role == "Announcer":
                r.send(msg)
        self.last_block_creation = time.time()

    def handle_receive_transaction(self, data):
        if self.is_valid_transaction(data['tx']):
            self.mempool.add_transaction(data['tx'])
            # Active endorsement phase of my candidate block:
            if self.can_start_new_block() and self.mempool.is_ready():
                log('info', f"{self} received enough transactions: {len(self.mempool.transactions)}")
                self.create_and_announce_candidate_block()
                # not self.active_endorsement_phase

    def can_start_new_block(self, block_window=0.5):
        if self.active_endorsement_phase:
            return False
        if time.time() - self.last_block_creation < block_window:
            return False
        return True

    def handle_candidate_block(self, data, conn):
        candidate_block = data['candidate_block']
        endorse, message = self.endorse_block(candidate_block)

        Statistics.endorsements_messages[candidate_block.bid].append(endorse)
        msg = protocol.endorse_block_message(self.pub_key, candidate_block, endorse, message)
        conn.send(msg)
        # if endorse:
        #     msg = protocol.endorse_block_message(self.pub_key, candidate_block, endorse, message)
        #     conn.send(msg)

    def handle_endorsements(self, data, conn):
        cblock = data['candidate_block']
        cblock = self.update_block_endorsements(cblock)
        if cblock.announcer == self.pub_key:
            self.received_blocks[cblock.bid].update({conn: data['endorse']})
            if len(cblock.endorsements) >= self.config.endorse_threshold and cblock.block_state == GLOB.BLOCK_INIT:
                cblock.block_state = GLOB.BLOCK_CONFIRMED
                self.active_endorsement_phase = False
                self.initiateBRB(cblock)
                self.staking_expiry -= 1
                if not self.active_endorsement_phase and self.mempool.is_ready():
                    self.create_and_announce_candidate_block()
            else:
                num_announcers = int(self.config.perc_announcers * self.config.num_nodes)
                if len(self.received_blocks[cblock.bid]) == num_announcers - 1:
                    self.active_endorsement_phase = False
                    for tx in cblock.transactions:
                        self.mempool.add_transaction(tx)
                    if self.mempool.is_ready():
                        self.create_and_announce_candidate_block()
                # else: I do nothing waiting for others to contact
        else:
            endorse, message = self.endorse_block(cblock)
            Statistics.endorsements_messages[cblock.bid].append(endorse)
            # if endorse:
            #     self.mempool.remove_transactions(cblock.transactions)
            msg = protocol.endorse_block_message(self.pub_key, cblock, endorse, message)
            conn.send(msg)

    def endorse_block(self, cblock: Block):
        endorse = False
        message = ""
        new_cblock, strong_block, seen_txs, strong_txs, conflicting_blocks = self.verify_conflicts(cblock)
        if new_cblock or strong_block:
            if not strong_block:  # block not seen before
                signature = sign_text(cblock.hash, self.prv_key)
                # cblock.endorsements[self.pub_key] = signature
                cblock.endorsements[self.port] = str(self)
                self.candidate_blocks[cblock.bid] = cblock
                extract_txs = {tx.hash: cblock for tx in cblock.transactions}
                self.seen_txs.update(extract_txs)
                message = "strong_block"
            else:
                #  update already seen block
                if self.pub_key in cblock.endorsements.keys():
                    self.candidate_blocks[cblock.bid] = cblock
                    message = "Block with no conflicts: already_seen"
                else:
                    signature = sign_text(cblock.hash, self.prv_key)
                    cblock.endorsements[self.port] = str(self)
                    # cblock.endorsements[self.pub_key] = signature
                    self.candidate_blocks[cblock.bid] = cblock
                    message = "Block with no conflicts: new_cblock"
            endorse = True
        else:
            strongest_block = self.get_strongest_block(conflicting_blocks)
            keep_cblock = len(cblock.endorsements) > len(strongest_block.endorsements) or (
                    len(cblock.endorsements) == len(
                strongest_block.endorsements) and cblock.hash <= strongest_block.hash)
            if keep_cblock:
                for cb in conflicting_blocks:
                    del self.candidate_blocks[cb.bid]
                    to_remove_txs = [tx_hash for tx_hash, b in cb.items() if b.bid == cb.bid]
                    for tx_hash in to_remove_txs:
                        del self.seen_txs[tx_hash]
                if self.pub_key in cblock.endorsements.keys():
                    self.candidate_blocks[cblock.bid] = cblock
                else:
                    signature = sign_text(cblock.hash, self.prv_key)
                    # cblock.endorsements[self.pub_key] = signature
                    cblock.endorsements[self.port] = str(self)
                    self.candidate_blocks[cblock.bid] = cblock
                endorse = True
                message = "Block with conflicts but strong"
            else:
                log('log', f"{self} :: {cblock} have been discarded!")
                message = "Block have been discarded!"

        return endorse, message

    def update_block_endorsements(self, cblock: Block):
        if cblock.bid in self.candidate_blocks:
            block = self.candidate_blocks[cblock.bid]
            endorsements = {**block.endorsements, **cblock.endorsements}
            block.endorsements = endorsements
            self.candidate_blocks[cblock.bid] = block
            return block

    def verify_conflicts(self, cblock):
        new_block = True
        strong_block = False
        seen_txs = [tx.hash for tx in cblock.transactions if tx.hash in self.seen_txs.keys()]
        strong_txs = [tx_hash for tx_hash in seen_txs if
                      len(cblock.endorsements) > len(self.seen_txs[tx_hash].endorsements)]
        # TODO check also hash when equal
        conflicting_set = [self.seen_txs[tx.hash] for tx in cblock.transactions if tx.hash in self.seen_txs.keys()]
        if len(seen_txs) > 0:
            new_block = False
            if len(strong_txs) == len(seen_txs):
                strong_block = True

        return new_block, strong_block, seen_txs, strong_txs, conflicting_set

    def verify_candidate_block(self, cblock: Block):
        # verify if the block has conflicting txs
        # # if so: count the number of endorsements for Bi compared to Bj and endorse Bj only if End(Bj) > End(Bi)
        rejected = {tx.hash: cblock for tx in cblock.transactions if
                    tx.hash in self.seen_txs.keys() and len(self.seen_txs[tx.hash].endorsements) >= len(
                        cblock.endorsements)}

        log('error', f"{self} rejected {rejected}")
        if len(rejected) == 0:
            signature = sign_text(cblock.hash, self.prv_key)
            # cblock.endorsements[self.pub_key] = signature
            cblock.endorsements[self.port] = str(self)
            txs = {tx.hash: cblock for tx in cblock.transactions}
            self.seen_txs.update(txs)
            return True, signature
        else:
            return False, rejected

    @staticmethod
    def get_strongest_block(conflicting_set) -> Block:
        # sorted = sorted(conflicting_blocks, key=lambda block: len(block.endorsements), reverse=True)
        return max(conflicting_set, key=lambda block: len(block.endorsements))

    def is_valid_transaction(self, tx):
        self.terminate = False
        if isinstance(tx, Transaction):
            return True
        else:
            exit("ERROR: invalid transaction type")

    def get_block_issuer(self, block):
        if self.config.mp == 1:
            raise Exception("Getting issuer not implemented yet!")
        for r in self.registry:
            if r.conn.pub_key == block.announcer:
                return r
        return None

    def initiateBRB(self, block: Block):
        log('success', f"{self} :: initiateBRB for {block}")
        Statistics.endorsement_rate[block.bid]['endorsed'] = True
        Statistics.endorsement_rate[block.bid]['end'] = time.time()
        Statistics.pccp_blocks += 1
        channel = self.router.add_channel()
        Statistics.channels[channel.channel_id] = {'start': time.time(), 'delivered': [], 'end': None}
        Statistics.init_delivered(channel.channel_id)
        channel.ready_layer.broadcast(block)
        # self.create_broadcast_channel(block)
        # self.init_broadcast_samples()
        # self.broadcast(Block)

    def consensus_achieved(self, channel, msg):
        log('info', f"{self} :: consensus achieved for {msg.data}")
        super().consensus_achieved(channel, msg)
        log('info', f"{self} validated the block {msg.data}. Receiving rewords ...")
        if len(self.mempool.transactions) > GLOB.BLOCK_SIZE + (GLOB.BLOCK_SIZE * 0.5):
            if self.mempool.is_ready(expiry=0) and not self.active_endorsement_phase:
                self.create_and_announce_candidate_block()
        else:
            log('log', f"{self} Finished with {len(self.mempool.transactions)} transactions left")
