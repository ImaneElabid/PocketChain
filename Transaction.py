import random
import string
from InputsConfig import InputsConfig as Param

Shared_pool=[]


class Transaction():
    """
    :param int id: the unique id or the hash of the transaction
    :param int timestamp: the time when the transaction is created. In case of Full technique, this will be array of two value (transaction creation time and receiving time)
    :param int sender: the id of the node that created and sent the transaction
    :param int to: the id of the recipient node
    :param int value: the amount of cryptocurrencies to be sent to the recipient node
    :param int size: the transaction size in MB
    :param float fee: the fee of the transaction
    :param str signature: the signature of the transaction
    """

    def __init__(self, id=0, timestamp=0 or [], sender=0, to=0, value=0, size=0.000546, fee=0, signature=None):
        self.id = id
        self.timestamp = timestamp
        self.sender = sender
        self.to = to
        self.value = value
        self.size = size
        self.fee = fee
        self.signature = signature

    @staticmethod
    def generate_transactions():
        pool = []
        for i in range(Param.Default_Psize):
            tx = Transaction()
            tx.id = random.randrange(100000000000)
            tx.sender = random.choice(Param.all_nodes).id
            tx.receiver = random.choice(Param.all_nodes).id
            tx.size = random.expovariate(1 / Param.Tsize)
            tx.fee = random.expovariate(1 / Param.Tfee)
            tx.value = ''.join(random.sample(string.ascii_letters, 5))
            pool.append(tx)
        random.shuffle(pool)
        return pool

    def prepare_tx(pool):
        transactions = []  # prepare a list of transactions to be included in the block
        size = 0  # calculate the total block gaslimit
        count = 0
        blocksize = Param.Bsize

        pool_sorted = sorted(pool, key=lambda x: x.fee,
                             reverse=True)  # sort pending transactions in the pool based on their fees

        while count < len(pool_sorted):
            if blocksize >= pool_sorted[count].size:
                blocksize -= pool_sorted[count].size
                transactions += [pool_sorted[count]]
                size += pool_sorted[count].size
            count += 1
        return transactions, size

    def __repr__(self):
        return f"{self.value}"

    def __str__(self):
        return f"{self.value}"
