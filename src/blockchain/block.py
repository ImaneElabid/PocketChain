import hashlib
from typing import Optional

import src.common.globals as GLOB
from src.blockchain.transaction import Transaction
from src.common.statistics import Statistics
from src.common.utils import current_timestamp, log


class Block:
    BlockId = 0

    def __init__(self, announcer: str, transactions, index=None, size=GLOB.BLOCK_SIZE, block_state=GLOB.BLOCK_INIT):
        # Header fields
        self.timestamp = current_timestamp()
        self.prev_hash = None
        self.size = size
        self.hash = None
        self.merkle_root = None
        # Body fields
        self.transactions = transactions
        # Attachments fields
        self.announcer = announcer
        self.block_state = block_state
        self.endorsements = {}
        # Program fields
        self.index = index  # index in local blockchain
        self.prev_block: Optional[Block] = None  # prev block from local blockchain
        self.block_state = block_state
        Block.BlockId += 1
        self.bid = Block.BlockId
        # Statistics
        Statistics.created_blocks += 1

    def compute_block_hash(self, endorsement_th, confirmed=False):
        if endorsement_th is None:
            endorsement_th = GLOB.MIN_ENDORSE
        # Simplified representation of block content
        data = f'{self.timestamp}-{self.announcer}'
        data += "".join([tx.hash for tx in self.transactions])
        if confirmed:
            if self.prev_hash:
                data += f'{self.prev_hash}{self.merkle_root}{self.size}'
            else:
                log('error', f"The hash of a confirmed block must contain the prev_hash!")
            if len(self.endorsements) >= endorsement_th:
                data += "".join([e for e in self.endorsements.values()])
            else:
                log('error', f"The hash of a confirmed block must contain endorsements!")

        self.hash = hashlib.sha256(data.encode()).hexdigest()

    def generate_block(self, announcer):
        Statistics.confirmed_blocks += 1  # count # of total blocks created!
        self.prev_hash = announcer.last_block().hash
        self.prev_block = announcer.last_block()
        self.index = self.prev_block.index + 1
        self.transactions = Transaction.prepare_tx()  # Get the created block (transactions and block size)
        return self

    def generate_conflicting_block(self, miner):
        pass
        # self.bid = random.randrange(1000)
        # self.miner = miner.id
        # self.previous = miner.last_block().id
        # self.prev_block = miner.last_block()
        # conflicting_txs = []
        # for i in range(P.Bsize):
        #     conflicting_txs.append(TX().create_conflicting_transaction(i))
        # self.transactions = conflicting_txs
        # return self

    def update_local_chain(self, node, miner, depth):
        pass
        # the node here is the one that needs to update its blockchain,
        # i = 0
        # while i < depth:
        #     if i < len(node.blockchain):  # Compare the old blocks in the local BC to miner BC
        #         if node.blockchain[i].id != miner.local_blockchain[i].id:
        #             # and (self.node.blockchain[i-1].id == Miner.blockchain[i].previous) and (i>=1):
        #             newBlock = miner.local_blockchain[i]
        #             node.blockchain[i] = newBlock
        #             node.update_transactionsPool(node, newBlock)
        #     else:  # Update the local BC by adding last block from miner BC
        #         newBlock = miner.local_blockchain[i]
        #         node.blockchain.append(newBlock)
        #         node.update_transactionsPool(node, newBlock)
        #     i += 1

    def __repr__(self):
        return f"Block#{self.bid} ({len(self.transactions)} TXs)"

    def __str__(self):
        return f"Block#{self.bid} ({len(self.transactions)} TXs)"
