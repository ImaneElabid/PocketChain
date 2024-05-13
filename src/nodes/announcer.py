import src.common.globals as GLOB
from src.blockchain.block import Block
from src.blockchain.mempool import MemPool
from src.blockchain.transaction import Transaction
from src.common import protocol
from src.common.crypto import sign_text
from src.common.utils import log, network_delay
from src.nodes.processor import Processor


class Announcer(Processor):
    def __init__(self, config, pub_key=None):
        super(Announcer, self).__init__(config, pub_key)
        self.role = "Announcer"
        self.balance = GLOB.STAKE_AMOUNT
        self.mempool = MemPool()
        self.is_eligible = False
        self.already_did = 0
        self.staking_expiry = GLOB.STAKE_EXPIRY
        self.staked_amount = 0
        self.seen_txs = {}
        self.candidate_blocks = []
        self.local_blockchain = []

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

    def create_and_announce_candidate_block(self, network_delays=False):
        """
        Function that creates and announces the candidate block. It implements a random waiting time
         to simulate real network activities if network_delays is set to True.
        """
        txs, size = self.mempool.select_top_transactions(by="fees", top=GLOB.BLOCK_SIZE)
        candidate_block = Block(self.pub_key, txs, size=size, block_state=GLOB.BLOCK_INIT)
        candidate_block.compute_block_hash(confirmed=False)
        self.candidate_blocks.append(candidate_block)
        msg = protocol.candidate_block_message(self.pub_key, candidate_block)
        if network_delays:
            network_delay()
        for r in self.registry:
            if r.role == "Announcer":
                r.send(msg)

    def handle_receive_transaction(self, data):
        if self.is_valid_transaction(data['tx']):
            self.mempool.add_transaction(data['tx'])
            if self.mempool.has_enough_transactions(mbs=False):
                # log('event', f"{self} received enough transactions: {len(self.mempool.transactions)}")
                self.create_and_announce_candidate_block(network_delays=True)

    def handle_candidate_block(self, data, conn):
        candidate_block = data['candidate_block']
        endorse, message = self.verify_candidate_block(candidate_block)
        msg = protocol.endorse_block_message(self.pub_key, candidate_block, endorse, message)
        conn.send(msg)

    def handle_endorsements(self, data):
        for block in self.candidate_blocks:
            if block.hash == data['candidate_block'].hash:
                if data['endorse']:
                    block.endorsements.append(data['message'])
                    # log('result', f"{self} -- Block {block} has {len(block.endorsements)} endorsements | +1 from ")
                    if len(block.endorsements) >= GLOB.ENDORSE_THRESHOLD and block.block_state == GLOB.BLOCK_INIT:
                        block.block_state = GLOB.BLOCK_CONFIRMED
                        self.initiateBRB(block)
                        self.staking_expiry -= 1
                else:
                    sent = []
                    conflicted_txs = data['message']
                    for tx, b in conflicted_txs.items():
                        if b.bid not in sent:
                            enforce, message = self.verify_candidate_block(b)
                            if enforce:
                                block_issuer = self.get_block_issuer(b)
                                if block_issuer:
                                    msg = protocol.endorse_block_message(self.pub_key, b, True, message)
                                    block_issuer.send(msg)
                            sent.append(b.bid)

    def verify_candidate_block(self, cblock: Block):
        # verify if the block has conflicting txs
        # # if so: count the number of endorsements for Bi compared to Bj and endorse Bj only if End(Bj) > End(Bi)
        rejected = {tx.hash: cblock for tx in cblock.transactions if
                    tx.hash in self.seen_txs.keys() and len(self.seen_txs[tx.hash].endorsements) >= len(cblock.endorsements)}
        if len(rejected) == 0:
            signature = sign_text(cblock.hash, self.prv_key)
            cblock.endorsements.append(signature)
            txs = {tx.hash: cblock for tx in cblock.transactions}
            self.seen_txs.update(txs)
            return True, signature
        else:
            return False, rejected

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
        log('event', f"{self} :: initiateBRB for {block}")
        channel = self.router.add_channel()
        channel.ready_layer.broadcast(block)
        # self.create_broadcast_channel(block)
        # self.init_broadcast_samples()
        # self.broadcast(Block)
