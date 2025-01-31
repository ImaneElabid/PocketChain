from __future__ import annotations

import copy
from typing import Optional

import numpy as np

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

    def subscribe_to_announcers(self, q=None):
        if q is None:
            q = self.config.Qsub
        while len(self.registry) < q:
            announcers = Registry.get_announcers(q)
            for announcer in announcers.values():
                if announcer.instance.verify_stake():
                    self.connect(announcer.instance)
        # log('event', f"{self} subscribed to {len(self.registry)} announcers!")

    def create_transaction(self, receiver: str, amount: float) -> Optional[Transaction]:
        if self.balance < amount:
            log('error', f"Insufficient balance")
            return None
        if self.tips < self.config.min_tips:
            log('error', f"Unsatisfying amount of tips")
            return None
        tx = Transaction(amount=amount, sender=self.pub_key, recipient=receiver)
        tx.build().sign(self.prv_key)
        self.tips -= tx.tip
        self.pending_transactions.append(tx)
        return tx

    def submit_transaction(self, tx: Transaction, tips_to_spend):
        tips = self.tip_per_announcer(tips_to_spend)

        for conn in self.registry:
            if len(tips) == 0:
                return
            tx_ = copy.deepcopy(tx)
            tx_.tip = tips.pop(0)
            msg = protocol.transaction_submit_message(self.pub_key, tx_)
            conn.send(msg)

    def handle_receive_transaction_confirmation(self, data, minc=GLOB.MIN_TX_CONFIRMATIONS):
        if data['tx'] in self.pending_transactions:
            self.confirmations[data['tx']] += 1
            if self.confirmations[data['tx']] >= minc:
                self.pending_transactions.remove(data['tx'])
                self.balance -= data['tx'].amount
                log('success', f"{data['tx']} confirmed!")

    def tip_per_announcer(self, tips_to_spend, alpha=0.5):
        nb_announcers = len(self.registry)
        powers = np.arange(0, nb_announcers)
        proportions = alpha ** powers
        proportions /= proportions.sum()
        tips = (tips_to_spend * proportions).astype(int)
        if tips[0] < GLOB.MIN_TIPS:
            tips[0] = tips_to_spend
        tips = [tip for tip in tips if tip >= GLOB.MIN_TIPS]
        return tips
