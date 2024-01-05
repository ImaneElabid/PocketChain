import copy
import logging

from Config.InputsConfig import InputsConfig as Param


class GossipBroadcast:
    def __init__(self, node, channel_id):
        self.node = node
        self.gossip_sample = set()
        self.gossip = None
        self.channel_id = channel_id

    def init(self):
        self.gossip_sample = set(Param.omega(Param.all_nodes, Param.G))
        for target in self.gossip_sample.copy():
            self.node.send(target, "GossipSubscribe", None, self.node, self.channel_id)

    def broadcast(self, block):
        if self.node.byzantine:
            conflicting_block = copy.deepcopy(block)
            conflicting_block.generate_conflicting_block(self.node)
            self.node.receive("Broadcast", (block, conflicting_block), hid=self.channel_id)
        else:
            self.node.receive("Broadcast", block, hid=self.channel_id)

    def dispatch(self, message):
        if self.gossip is None:
            self.gossip = message
            for target in self.gossip_sample:
                self.node.send(target, "Gossip", message, self.node, self.channel_id)
            self.node.receive("delivered a gossip", message, source=self.node, hid=self.channel_id)

    def handle(self, event, message, source):
        if event == "Broadcast":
            logging.info(f"{self.node} -> {event}: <{message}>  -> Channel: <{self.channel_id[:4]}..>")#
            self.dispatch(message)

        elif event == "GossipSubscribe":
            if self.gossip is not None:
                message = self.gossip
                self.node.send(source, "Gossip", message, self.node, self.channel_id)
            self.gossip_sample.add(source)

        elif event == "Gossip":
            print(f"{self.node} -> {event}: <{message}> == <{self.channel_id[:4]}>")#
            self.dispatch(message)

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
        if event == "Broadcast":
            logging.info(f"{self.node} -> {event} of conflicting blocks: <{block1}> =\=  <{block2}>-> Channel: <{self.channel_id[:4]}..>")#
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
