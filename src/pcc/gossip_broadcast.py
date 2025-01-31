import copy
import logging
import sys

from src.blockchain.registry import Registry
from src.common import protocol
from src.common.statistics import Statistics


class GossipBroadcast:
    def __init__(self, node, channel_id):
        self.node = node
        self.gossip_sample = set()
        self.gossip = None
        self.channel_id = channel_id

    def init(self):
        self.gossip_sample = Registry.omega(self.node.config.G)
        for target in self.gossip_sample.copy():
            msg = protocol.pcc_message(protocol.GOSSIP_SUBSCRIBE, self.node, self.channel_id)
            self.node.pcc_send(target, msg)

    def broadcast(self, block):
        if self.node.role == "Byzantine":
            conflicting_block = copy.deepcopy(block)
            conflicting_block.generate_conflicting_block(self.node)
            self.node.receive("pcc", (block, conflicting_block), hid=self.channel_id)
        else:
            msg = protocol.pcc_message(protocol.PCC, self.node, self.channel_id, block)
            self.node.pcc_receive(msg)

    def dispatch(self, msg):
        if self.gossip is None:
            self.gossip = msg.data
            for target in self.gossip_sample:
                forward = protocol.pcc_message(protocol.GOSSIP, self.node, self.channel_id, msg.data)
                self.node.pcc_send(target, forward)
            dmsg = protocol.pcc_message(protocol.DELIVERED_GOSSIP, self.node, self.channel_id, msg.data)
            self.node.pcc_receive(dmsg)

    def handle(self, msg):
        Statistics.exchanged_bytes += sys.getsizeof(msg) * 8
        if msg.mtype == protocol.PCC:
            self.dispatch(msg)
        elif msg.mtype == protocol.GOSSIP_SUBSCRIBE:
            if self.gossip is not None:
                reply = protocol.pcc_message(protocol.GOSSIP, self.node, self.channel_id, self.gossip)
                self.node.pcc_send(msg.source, reply)
            self.gossip_sample.add(msg.source)
        elif msg.mtype == protocol.GOSSIP:
            self.dispatch(msg)

    def byz_dispatch(self, block1, block2):
        gossip_sample_list = list(self.gossip_sample)
        half = len(gossip_sample_list) // 2
        first_half = gossip_sample_list[:half]
        second_half = gossip_sample_list[half:]

        # Send first message to the first half
        for target in first_half:
            self.node.send(target, "Gossip", block1, self.node, self.channel_id)

        # Send second message to the second half
        for target in second_half:
            self.node.send(target, "Gossip", block2, self.node, self.channel_id)

    def byz_handle(self, event, source, block1, block2):
        if event == "pcc":
            logging.info(
                f"{self.node} -> {event} of conflicting blocks: <{block1}> =\=  <{block2}>-> Channel: <{self.channel_id[:4]}..>")  #
            # logging.info(f"{self.node} -> {event}: <{block2}>  -> Channel: <{self.channel_id[:4]}..>")#
            self.byz_dispatch(block1, block2)

        elif event == "GossipSubscribe":
            # print(f"{self.node} -> {event}: <{block1}> == {self.channel_id}")#
            if self.gossip is not None:
                message = self.gossip
                self.node.send(source, "Gossip", message, self.node, self.channel_id)
            self.gossip_sample.add(source)

        elif event == "Gossip":
            # print(f"{self.node} -> {event}: <{block1}> == {self.channel_id}")#
            self.byz_dispatch(block1, block2)

    def __repr__(self):
        return f"GB({self.channel_id[:4]})"

    def __str__(self):
        return f"GB({self.channel_id[:4]})"
