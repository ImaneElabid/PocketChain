import logging
import random
import threading
import time

from InputsConfig import InputsConfig as Param

from GossipBroadcast import GossipBroadcast
from EchoBroadcast import EchoBroadcast
from ReadyBroadcast import ReadyBroadcast
from RoutingTable import RoutingTable

random.seed(10)


class Node:
    already_executed_flag = False

    def __init__(self, node_id):
        # Node initialization
        self.id = node_id
        self.routing_table = RoutingTable()

    ##########################################################################

    def send(self, target, event, message, source=None, hid=None):
        target.receive(event, message, source, hid)

    def receive(self, event, message, source=None, hid=None):
        # Retrieve the broadcast layers for this h_id
        if hid in self.routing_table:
            broadcast_layers = self.routing_table.get_instance(hid)
            if broadcast_layers:
                gossip_layer, echo_layer, ready_layer = broadcast_layers

                if event in ['Broadcast', 'GossipSubscribe', 'Gossip']:
                    gossip_layer.handle(event, message, source)
                elif event in ['delivered a gossip', 'EchoSubscribe', 'Echo']:
                    echo_layer.handle(event, message, source)
                elif event in ['delivered an echo', 'ReadySubscribe', 'Ready', 'achieved consensus']:
                    ready_layer.handle(event, message, source)
        else:
            # handle the case where the h_id is not found in the routing table


    def sample_and_send(self, message, size, hid):
        sampled_nodes = Param.omega(Param.all_nodes, size)
        for node in sampled_nodes:
            self.send(node, message, None, self, hid)
        return sampled_nodes

        # Special methods

    def node_thread_init(self, sender, message):
        pass


    def create_and_broadcast(self, message):
        hid = Param.hid(message)
        self.routing_table.add_instance(hid, [])  # Add the top layer instance to the routing table
        gossip_layer = GossipBroadcast(self, hid)
        echo_layer = EchoBroadcast(self, gossip_layer, hid)
        ready_layer = ReadyBroadcast(self, echo_layer, hid)
        # TODO how to add Br instances to RT
        ready_layer.broadcast(message)

    def __repr__(self):
        return f"Node({self.id})"

    def __str__(self):
        return f"Node({self.id})"
