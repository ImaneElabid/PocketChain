import random
import threading
import time

from Blocks.Transaction import Transaction as TX
from Statistics import Statistics as ST
from Config.InputsConfig import InputsConfig as P


class Block():
    """ Defines the base Block model.

    :param int depth: the index of the block in the local blockchain ledger (0 for genesis block)
    :param int id: the uinque id or the hash of the block
    :param int previous: the uinque id or the hash of the previous block
    :param int timestamp: the time when the block is created
    :param int miner: the id of the miner who created the block
    :param list transactions: a list of transactions included in the block
    :param int size: the block size in MB
    :param int PrevHash: the previous hash << S >>
    :param int state: the initial state of the block << y >>
    :param int r: the randomness value to implement chameleon hash function
    """

    def __init__(self, depth=0, id=0, previous=-1, prev_block=None, timestamp=0, miner=None, transactions=[], size=1.0, prev_hash="0",
                 block_state=None): #block_state=compute_hash(["0", []])
        self.depth = depth
        self.id = id
        self.previous = previous
        self.prev_block = prev_block
        self.timestamp = timestamp
        self.miner = miner
        self.transactions = transactions or []
        self.size = size
        self.prev_hash = prev_hash
        self.block_state = block_state
        # self.lock = threading.Lock()
    def generate_block(self, miner):
        ST.totalBlocks += 1  # count # of total blocks created!
        self.id = random.randrange(100000000000)
        self.timestamp = time.time()
        self.miner = miner.id
        self.previous = miner.last_block().id
        self.prev_block = miner.last_block()
        self.depth= self.prev_block.depth+1
        self.transactions = TX.prepare_tx()  # Get the created block (transactions and block size)
        return self

    def generate_conflicting_block(self, miner):
        # with self.lock:
            self.id = random.randrange(1000)
            self.timestamp = time.time()
            self.miner = miner.id
            self.previous = miner.last_block().id
            self.prev_block = miner.last_block()
            conflicting_txs = []
            for i in range(P.Bsize):
                conflicting_txs.append(TX().create_conflicting_transaction(i))
            self.transactions = conflicting_txs
            return self


    def update_local_blockchain(node, miner, depth):
        # the node here is the one that needs to update its blockchain,
        i = 0
        while i < depth:
            if i < len(node.blockchain):  # Compare the old blocks in the local BC to miner BC
                if node.blockchain[i].id != miner.local_blockchain[i].id:  # and (self.node.blockchain[i-1].id == Miner.blockchain[i].previous) and (i>=1):
                    newBlock = miner.local_blockchain[i]
                    node.blockchain[i] = newBlock
                    node.update_transactionsPool(node, newBlock)
            else:        # Update the local BC by adding last block from miner BC
                newBlock = miner.local_blockchain[i]
                node.blockchain.append(newBlock)
                node.update_transactionsPool(node, newBlock)
            i += 1


    def __repr__(self):
        return f"({self.depth}) --> {self.transactions}"

    def __str__(self):
        return f"({self.depth}): ({self.id})-->{self.transactions}"