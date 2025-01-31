import sys

from src.blockchain.registry import Registry
from src.common import protocol
from src.common.statistics import Statistics
from src.pcc.gossip_broadcast import GossipBroadcast


class EchoBroadcast:
    def __init__(self, node, gossip_layer, channel_id):
        self.node = node
        self.echo_sample = set()
        self.echo_subscribe_sample = set()
        self.echo_replies = {}
        self.echo_delivered = False
        self.echo = None
        self.channel_id = channel_id
        self.gossip_layer: GossipBroadcast = gossip_layer

    def init(self):
        self.gossip_layer.init()
        self.echo_sample = Registry.omega(self.node.config.E)
        for target in self.echo_sample:
            msg = protocol.pcc_message(protocol.ECHO_SUBSCRIBE, self.node, self.channel_id)
            self.node.pcc_send(target, msg)
        self.echo_replies = {node.port: None for node in self.echo_sample}

    def broadcast(self, block):
        #  call broadcast function of lower layer
        self.gossip_layer.broadcast(block)
        # self.gossip_layer.byz_broadcast(message1="A", message2="B")

    def handle(self, msg):
        Statistics.exchanged_bytes += sys.getsizeof(msg) * 8
        if msg.mtype == protocol.DELIVERED_GOSSIP:
            self.echo = msg.data
            for target in self.echo_subscribe_sample:
                echo_msg = protocol.pcc_message(protocol.ECHO, self.node, self.channel_id, msg.data)
                self.node.pcc_send(target, echo_msg)
            self.check_echo(msg)
        elif msg.mtype == protocol.ECHO_SUBSCRIBE:
            if self.echo is not None:
                forward = protocol.pcc_message(protocol.ECHO, self.node, self.channel_id, self.echo)
                self.node.pcc_send(msg.source, forward)
            self.echo_subscribe_sample.add(msg.source)
        elif msg.mtype == protocol.ECHO:
            if msg.source in self.echo_sample and self.echo_replies[msg.source.port] is None:
                self.echo_replies[msg.source.port] = msg.data
                self.check_echo(msg.data)

    def check_echo(self, message):
        # Count the number of echo replies that match self.echo
        echo_count = sum(1 for reply in self.echo_replies.values() if reply == self.echo)
        # If the count meets the threshold and the message hasn't been delivered yet, deliver the message
        if echo_count >= self.node.config.E_tilda and not self.echo_delivered:
            self.echo_delivered = True
            msg = protocol.pcc_message(protocol.DELIVERED_ECHO, self.node, self.channel_id, message)
            self.node.pcc_receive(msg)

    def byz_handle(self, event, source, block1, block2):
        if event == "delivered a gossip":
            echo_subscribe_sample_list = list(self.echo_subscribe_sample)
            half = len(echo_subscribe_sample_list) // 2
            first_half = echo_subscribe_sample_list[:half]
            second_half = echo_subscribe_sample_list[half:]

            # Send first message to the first half
            for target in first_half:
                self.node.send(target, "Echo", block1, self.node, self.channel_id)

            # Send second message to the second half
            for target in second_half:
                self.node.send(target, "Echo", block2, self.node, self.channel_id)

        elif event == "EchoSubscribe":
            if self.echo is not None:
                message = self.echo
                self.node.send(source, "Echo", message, self.node, self.channel_id)
            self.echo_subscribe_sample.add(source)

        elif event == "Echo":
            # print(f"{self.node} -> {event}: <{message}> == {self.channel_id}")#
            self.node.receive("delivered an echo", block1, source=self.node, hid=self.channel_id)
            self.node.receive("delivered an echo", block2, source=self.node, hid=self.channel_id)

    def __repr__(self):
        return f"EB({self.channel_id[:4]})"

    def __str__(self):
        return f"EB({self.channel_id[:4]})"
