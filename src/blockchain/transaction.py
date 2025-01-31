import random
import threading

import src.common.globals as GLOB
from src.common.crypto import calculate_hash, sign_text
from src.common.utils import current_timestamp


class Transaction:
    TXid = 0

    def __init__(self, amount: float, sender: str = None, recipient: str = None, tip: int = GLOB.MIN_TIPS):
        self.hash = None
        self.timestamp = current_timestamp()
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.tip = tip
        self.size = None
        self.signature = None
        # program fields
        Transaction.TXid += 1
        self.tid = Transaction.TXid
        self.block = None

    def build(self):
        self.size = random.expovariate(1 / GLOB.TX_SIZE)
        self.hash = calculate_hash(self.tid)
        return self

    def sign(self, prv_key):
        tx_text = f"{self.timestamp}-{self.sender}-{self.recipient}-{self.amount}-{self.tip}"
        self.signature = sign_text(tx_text, prv_key)
        return self

    def create_conflicting_transaction(self, conflict):
        self.create_transaction()
        self.amount = 'conflicting tx' + str(conflict)
        return self

    @classmethod
    def calculate_transaction_fee(cls, tx, proposed_tip):
        if tx.tip < proposed_tip:
            return proposed_tip
        else:
            return tx.tip

    @staticmethod
    def prepare_tx():
        pool_sorted = sorted(P.Shared_pool.get_transactions(), key=lambda x: x.fee,
                             reverse=False)  # sort pending transactions in the pool based on their fees
        return pool_sorted[:P.Bsize]

    def __repr__(self):
        return f"Transaction#{self.tid}-({self.amount}PCs|{self.tip}T)"

    def __str__(self):
        return f"Transaction#{self.tid}-({self.amount}PCs|{self.tip}T)"


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
