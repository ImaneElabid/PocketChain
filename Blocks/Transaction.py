import random
import string
import threading

from Config.InputsConfig import InputsConfig as P


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

    def create_transaction(self):
        self.id = random.randrange(100000000000)
        self.sender = random.choice(P.all_nodes).id
        self.receiver = random.choice(P.all_nodes).id
        self.size = random.expovariate(1 / P.Tsize)
        self.fee = random.expovariate(1 / P.Tfee)
        self.value = ''.join(random.sample(string.ascii_letters, 5))
        return self

    def create_conflicting_transaction(self, conflict):
        self.create_transaction()
        self.value = 'conflicting tx'+ str(conflict)
        return self

    @staticmethod
    def prepare_tx():
        pool_sorted = sorted(P.Shared_pool.get_transactions(), key=lambda x: x.fee,
                             reverse=False)  # sort pending transactions in the pool based on their fees
        return pool_sorted[:P.Bsize]

    def __repr__(self):
        return f"|{self.value}|"

    def __str__(self):
        return f"|{self.value}|"


class TransactionPool:
    def __init__(self):
        self.transactions = []
        self.lock = threading.Lock()

    def has_enough_transactions(self):
        with self.lock:
            return len(self.transactions) >= P.Bsize

    def add_transaction(self, transaction):
        with self.lock:
            self.transactions.append(transaction)

    def get_transactions(self):
        with self.lock:
            return self.transactions

    def remove_transaction(self, transaction):
        with self.lock:
            for _ in transaction:
                if _ in self.transactions:
                    self.transactions.remove(_)
        return self.transactions
