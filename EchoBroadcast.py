import logging

from InputsConfig import InputsConfig as Param


class EchoBroadcast:
    def __init__(self, node, gossip_layer, hid):
        self.node = node
        self.echo_sample = set()
        self.echo_subscribe_sample = set()
        self.echo_replies = {}
        self.echo_delivered = False
        self.echo = None
        self.broadcast_channel = hid
        self.gossip_layer = gossip_layer
        self.init()

    def init(self):
        self.echo_sample = self.node.sample_and_send("EchoSubscribe", Param.E, self.broadcast_channel)
        self.echo_replies = {node: None for node in self.echo_sample}

    def broadcast(self, message):
        #  call broadcast function of lower layer
        self.gossip_layer.broadcast(message)

    def handle(self, event, message, source):
        if event == "delivered a gossip":
            # print(f"{self.node} -> {event}: <{message}>")#
            self.echo = message
            for target in self.echo_subscribe_sample:
                self.node.send(target, "Echo", message, self.node, self.broadcast_channel)
            self.check_echo(message)

        elif event == "EchoSubscribe":
            if self.echo is not None:
                message = self.echo
                self.node.send(source, "Echo", message, self.node, self.broadcast_channel)
            self.echo_subscribe_sample.add(source)

        elif event == "Echo":
            if source in self.echo_sample and self.echo_replies[source] is None:
                self.echo_replies[source] = message
                self.check_echo(message)

    def check_echo(self, message):
        # Count the number of echo replies that match self.echo
        echo_count = sum(1 for reply in self.echo_replies.values() if reply == self.echo)
        # If the count meets the threshold and the message hasn't been delivered yet, deliver the message
        if echo_count >= Param.E_tilda and not self.echo_delivered:
            self.echo_delivered = True
            self.node.receive("delivered an echo", message)
