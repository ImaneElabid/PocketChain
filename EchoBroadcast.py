import logging

from InputsConfig import InputsConfig as Param


class EchoBroadcast:
    def __init__(self, node, gossip_layer, channel_id):
        self.node = node
        self.echo_sample = set()
        self.echo_subscribe_sample = set()
        self.echo_replies = {}
        self.echo_delivered = False
        self.echo = None
        self.channel_id = channel_id
        self.gossip_layer = gossip_layer

    def init(self):
        self.gossip_layer.init()
        self.echo_sample = self.node.sample_and_send("EchoSubscribe", Param.E, self.channel_id)
        self.echo_replies = {node: None for node in self.echo_sample}

    def broadcast(self, message):
        #  call broadcast function of lower layer
        self.gossip_layer.broadcast(message)
        # self.gossip_layer.byz_broadcast(message1="A", message2="B")

    def handle(self, event, message, source):
        if event == "delivered a gossip":
            # print(f"{self.node} -> {event}: <{message}>  -> Channel: <{self.channel_id[:4]}..>")#
            self.echo = message
            for target in self.echo_subscribe_sample:
                self.node.send(target, "Echo", message, self.node, self.channel_id)
            self.check_echo(message)

        elif event == "EchoSubscribe":
            if self.echo is not None:
                message = self.echo
                self.node.send(source, "Echo", message, self.node, self.channel_id)
            self.echo_subscribe_sample.add(source)

        elif event == "Echo":
            # print(f"{self.node} -> {event}: <{message}> == <{self.channel_id[:4]}..>")#
            if source in self.echo_sample and self.echo_replies[source] is None:
                self.echo_replies[source] = message
                self.check_echo(message)

    def check_echo(self, message):
        # Count the number of echo replies that match self.echo
        echo_count = sum(1 for reply in self.echo_replies.values() if reply == self.echo)
        # If the count meets the threshold and the message hasn't been delivered yet, deliver the message
        if echo_count >= Param.E_tilda and not self.echo_delivered:
            self.echo_delivered = True
            self.node.receive("delivered an echo", message, self.node, self.channel_id)

    def byz_handle(self, event, source, message1, message2):
        if event == "delivered a gossip":
            echo_subscribe_sample_list = list(self.echo_subscribe_sample)
            half = len(echo_subscribe_sample_list) // 2
            first_half = echo_subscribe_sample_list[:half]
            second_half = echo_subscribe_sample_list[half:]

            # Send first message to the first half
            for target in first_half:
                self.node.send(target, "Echo", message1, self.node, self.channel_id)

            # Send second message to the second half
            for target in second_half:
                self.node.send(target, "Echo", message2, self.node, self.channel_id)

        elif event == "EchoSubscribe":
            if self.echo is not None:
                message = self.echo
                self.node.send(source, "Echo", message, self.node, self.channel_id)
            self.echo_subscribe_sample.add(source)

        elif event == "Echo":
            # print(f"{self.node} -> {event}: <{message}> == {self.channel_id}")#
            self.node.receive("delivered an echo", message1, self.node, self.channel_id)
            self.node.receive("delivered an echo", message2, self.node, self.channel_id)

    def __repr__(self):
        return f"EB({self.channel_id[:4]})"

    def __str__(self):
        return f"EB({self.channel_id[:4]})"
