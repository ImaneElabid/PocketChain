from __future__ import annotations

from typing import Optional

import src.common.globals as GLOB
from src.blockchain.registry import Registry
from src.blockchain.transaction import Transaction
from src.common import protocol
from src.common.utils import log
from src.nodes.node import Node


class Client(Node):
    def __init__(self, config, pub_key=None):
        super(Client, self).__init__(config, pub_key)
        self.role = "Client"
        self.pending_transactions = []
        self.confirmations = {}

    def subscribe_to_announcers(self, q=GLOB.QSUB):
        while len(self.registry) < q:
            announcers = Registry.get_announcers(q)
            for announcer in announcers.values():
                if announcer.instance.verify_stake():
                    self.connect(announcer.instance)
        # log('event', f"{self} subscribed to {len(self.registry)} announcers!")

    def create_transaction(self, receiver: str, amount: float, proposed_tip: int) -> Optional[Transaction]:
        if self.balance < amount:
            log('error', f"Insufficient balance")
            return None
        if self.tips < self.config.min_tips:
            log('error', f"Unsatisfying amount of tips")
            return None
        tx = Transaction(amount=amount, sender=self.pub_key, recipient=receiver)
        tx.tip = Transaction.calculate_transaction_fee(tx, proposed_tip)
        tx.build().sign(self.prv_key)
        self.tips -= tx.tip
        self.pending_transactions.append(tx)
        return tx

    def submit_transaction(self, tx):
        msg = protocol.transaction_submit_message(self.pub_key, tx)
        for conn in self.registry:
            conn.send(msg)

    def handle_receive_transaction_confirmation(self, data, minc=GLOB.MIN_TX_CONFIRMATIONS):
        if data['tx'] in self.pending_transactions:
            self.confirmations[data['tx']] += 1
            if self.confirmations[data['tx']] >= minc:
                self.pending_transactions.remove(data['tx'])
                self.balance -= data['tx'].amount
                log('success', f"{data['tx']} confirmed!")
