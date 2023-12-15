import logging
import random
import time
import threading

from InputsConfig import InputsConfig as Param

from RoutingTable import RoutingTable


class Node:
    already_executed_flag = False

    def __init__(self, node_id):
        # Node initialization
        self.id = node_id
        self.routing_table = RoutingTable(self)

    ##########################################################################
    def create_and_broadcast(self, message, sender):
        if self == sender:
            hid = Param.hid(message)
            channel = self.routing_table.add_channel(hid)
            time.sleep(0.01)
            channel.ready_layer.broadcast(message)

    def send(self, target, event, message, source=None, hid=None):
        target.receive(event, message, source, hid)

    def receive(self, event, message, source=None, hid=None):
        # Retrieve the broadcast layers for this h_id
        if self.routing_table.channel_exist(hid):
            channel = self.routing_table.get_channel(hid)
        else:
            channel = self.routing_table.add_channel(hid)
        self.handle_request(channel, event, message, source)

    def handle_request(self, channel, event, message, source=None):
        if event in ['Broadcast', 'GossipSubscribe', 'Gossip']:
            channel.gossip_layer.handle(event, message, source)
        elif event in ['delivered a gossip', 'EchoSubscribe', 'Echo']:
            channel.echo_layer.handle(event, message, source)
        elif event in ['delivered an echo', 'ReadySubscribe', 'Ready', 'achieved consensus']:
            channel.ready_layer.handle(event, message, source)

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
