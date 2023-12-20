import random
import sys
import time

from InputsConfig import InputsConfig as Param
from Statistics import Statistics as ST
from RoutingTable import RoutingTable
from Transaction import Transaction as TX


class Node:

    def __init__(self, node_id, byzantine=False):
        self.id = node_id
        self.byzantine = byzantine
        self.blockchain = []
        self.transaction_pool = []
        self.routing_table = RoutingTable(self)

    ##########################################################################

    def create_tx(self):
        tx = TX()
        self.transaction_pool = TX.generate_transactions()
        tx = random.choice(self.transaction_pool)  # Select a random transaction and broadcast it
        print(f"Created Transaction: {tx}")

    def create_and_broadcast(self, sender):
        if self == sender:
            self.create_tx()
            if self.transaction_pool:  # Check if the pool is not empty
                tx_to_broadcast = random.choice(self.transaction_pool)
                hid = Param.hid(tx_to_broadcast.value)
                channel = self.routing_table.add_channel(hid)
                ST.init_delivered(
                    hid)  # add broadcast channel with id=hid to the stats to keep track on delivery threshold
                time.sleep(0.01)
                channel.ready_layer.broadcast(tx_to_broadcast)
                self.transaction_pool.remove(tx_to_broadcast)  # Remove the broadcasted transaction

    def send(self, target, event, message, source=None, hid=None):
        target.receive(event, message, source, hid)

    def receive(self, event, message, source=None, hid=None):
        # Retrieve the broadcast layers for this h_id
        if self.routing_table.channel_exist(hid):
            channel = self.routing_table.get_channel(hid)
        else:
            channel = self.routing_table.add_channel(hid)
        self.handle_request(channel, event, message, source, hid)

    def handle_request(self, channel, event, message, source=None, hid=None):
        if self.id == 400:
            if event in ['Broadcast', 'GossipSubscribe', 'Gossip']:
                channel.gossip_layer.byz_handle(event, source, message1="A", message2="B")
            elif event in ['delivered a gossip', 'EchoSubscribe', 'Echo']:
                channel.echo_layer.byz_handle(event, source, message1="A", message2="B")
            elif event in ['delivered an echo', 'ReadySubscribe', 'Ready']:
                channel.ready_layer.byz_handle(event, source, message1="A", message2="B")
            elif event == 'achieved consensus':
                channel.delivered = True
                ST.update_delivered(self.id, hid)
        else:
            if event in ['Broadcast', 'GossipSubscribe', 'Gossip']:
                channel.gossip_layer.handle(event, message, source)
            elif event in ['delivered a gossip', 'EchoSubscribe', 'Echo']:
                channel.echo_layer.handle(event, message, source)
            elif event in ['delivered an echo', 'ReadySubscribe', 'Ready']:
                channel.ready_layer.handle(event, message, source)
            elif event == 'achieved consensus':
                channel.delivered = True
                ST.update_delivered(self.id, hid)
                # print(f"{self} -> {event}: <{message}> ")#
                # self.routing_table.remove_channel(hid)

    def update_transactionsPool(self, block):
        j = 0
        while j < len(block.transactions):
            for t in self.transactions_pool:
                if block.transactions[j].id == t.id:
                    del t
                    break
            j += 1

    def sample_and_send(self, message, size, hid):
        sampled_nodes = Param.omega(Param.all_nodes, size)
        for node in sampled_nodes:
            self.send(node, message, None, self, hid)
        return sampled_nodes

        # Special methods

    def __repr__(self):
        return f"Node({self.id})"

    def __str__(self):
        return f"Node({self.id})"
