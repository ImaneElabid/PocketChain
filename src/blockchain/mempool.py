import src.common.globals as GLOB
from src.common.utils import log


class MemPool:
    def __init__(self):
        # pending transactions in the pool
        self.total = 0
        self.transactions = []

    def has_enough_transactions(self, mbs=True):
        if mbs:
            return sum(tx.size for tx in self.transactions) >= GLOB.BLOCK_SIZE
        else:
            return len(self.transactions) >= GLOB.BLOCK_SIZE

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.total += 1
        return self

    def get_transactions(self):
        return self.transactions

    def select_top_transactions(self, by="fees", top=GLOB.BLOCK_SIZE):
        sorted_pool = []
        if by == "fees":
            sorted_pool = sorted(self.transactions, key=lambda x: x.tip, reverse=True)
        elif by == "size":
            sorted_pool = sorted(self.transactions, key=lambda x: x.tip, reverse=False)
        elif by == "amount":
            sorted_pool = sorted(self.transactions, key=lambda x: x.tip, reverse=True)
        else:
            log('error', f"wrong value for {by} in <get_top_transactions()>")

        txs = sorted_pool[:top]
        self.transactions = [tx for tx in self.transactions if tx not in txs]
        return txs, len(txs)

    def remove_transaction(self, transaction):
        for _ in transaction:
            if _ in self.transactions:
                self.transactions.remove(_)
        return self.transactions

# import random
# import string
# import threading
#
# import src.common.globals as GLOB
# from src.common.utils import current_timestamp


# class Transaction:
#     TXid = 0
#
#     def __init__(self, amount, sender=None, recipient=None, tip=GLOB.MIN_TIPS):
#         self.hash = None
#         self.timestamp = current_timestamp()
#         self.sender = sender
#         self.recipient = recipient
#         self.amount = amount
#         self.tip = tip
#         self.size = None
#         self.signature = None
#         # program fields
#         Transaction.TXid += 1
#         self.tid = Transaction.TXid
#
#     def create_transaction(self):
#         self.hash = random.randrange(100000000000)
#         self.sender = random.choice(P.all_nodes).id
#         self.recipient = random.choice(P.all_nodes).id
#         self.size = random.expovariate(1 / P.Tsize)
#         self.tip = random.expovariate(1 / P.Tfee)
#         self.amount = ''.join(random.sample(string.ascii_letters, 5))
#         return self
#
#     def create_conflicting_transaction(self, conflict):
#         self.create_transaction()
#         self.amount = 'conflicting tx' + str(conflict)
#         return self
#
#     @staticmethod
#     def prepare_tx():
#         pool_sorted = sorted(P.Shared_pool.get_transactions(), key=lambda x: x.fee,
#                              reverse=False)  # sort pending transactions in the pool based on their fees
#         return pool_sorted[:P.Bsize]
#
#     def __repr__(self):
#         return f'Transaction(sender={self.sender}, receiver={self.recipient}, amount={self.amount})'
#
#     def __str__(self):
#         return f'Transaction(sender={self.sender}, receiver={self.recipient}, amount={self.amount})'
#
#
# class TransactionPool:
#     def __init__(self):
#         self.transactions = []
#         self.lock = threading.Lock()
#
#     def has_enough_transactions(self):
#         with self.lock:
#             return len(self.transactions) >= P.Bsize
#
#     def add_transaction(self, transaction):
#         with self.lock:
#             self.transactions.append(transaction)
#
#     def get_transactions(self):
#         with self.lock:
#             return self.transactions
#
#     def remove_transaction(self, transaction):
#         with self.lock:
#             for _ in transaction:
#                 if _ in self.transactions:
#                     self.transactions.remove(_)
#         return self.transactions
