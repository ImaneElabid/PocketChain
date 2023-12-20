from InputsConfig import InputsConfig as Param
from Transaction import Transaction as TX
from Statistics import Statistics as ST


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
                 block_state=None,edited_tx=None): #block_state=compute_hash(["0", []])
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
        self.edited_tx = edited_tx

    @staticmethod
    # Generate the Genesis block and append it to the local blockchain for all nodes
    def generate_genesis_block():
        for miner in Param.all_nodes:
            miner.blockchain.append(Block())

    def last_block(self):
        return self.blockchain[len(self.blockchain) - 1]

    def blockchain_length(self):
        return len(self.blockchain)

    def generate_block(self,miner):
        ST.totalBlocks += 1  # count # of total blocks created!
        blockTrans, blockSize = TX.execute_transactions()  # Get the created block (transactions and block size)
        self.transactions = blockTrans
        self.block.size = blockSize
        miner.blockchain.append(self)
        # TX.create_transactions()  # generate new transactions

    def update_local_blockchain(node, miner, depth):
        # the node here is the one that needs to update its blockchain,
        i = 0
        while i < depth:
            if i < len(node.blockchain):  # Compare the old blocks in the local BC to miner BC
                if node.blockchain[i].id != miner.blockchain[i].id:  # and (self.node.blockchain[i-1].id == Miner.blockchain[i].previous) and (i>=1):
                    newBlock = miner.blockchain[i]
                    node.blockchain[i] = newBlock
                    node.update_transactionsPool(node, newBlock)
            else:        # Update the local BC by adding last block from miner BC
                newBlock = miner.blockchain[i]
                node.blockchain.append(newBlock)
                node.update_transactionsPool(node, newBlock)
            i += 1
