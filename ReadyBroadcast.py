import logging

from InputsConfig import InputsConfig as Param


class ReadyBroadcast:
    def __init__(self, node, echo_layer, hid):
        self.node = node
        self.already_executed_flag = False
        self.ready_subscribe_sample = set()
        self.ready_delivered = False
        self.ready_sample = set()
        self.delivery_sample = set()

        self.ready = set()
        self.delivered = False
        self.ready_replies = {}
        self.delivery_replies = {}
        self.broadcast_channel = hid
        self.echo_layer = echo_layer
        self.init()
    def init(self):
        self.ready_sample = self.node.sample_and_send("ReadySubscribe", Param.R, self.broadcast_channel)
        self.ready_replies = {node_id: set() for node_id in self.ready_sample}

        self.delivery_sample = self.node.sample_and_send("ReadySubscribe", Param.D, self.broadcast_channel)
        self.delivery_replies = {node_id: set() for node_id in self.delivery_sample}

    def broadcast(self, message):
        self.echo_layer.broadcast(message)
        # Code to handle ready/delivery after echo is delivered

    def handle(self, event, message, source):
        if event == "delivered an echo":
            # print(f"{self.node} -> {event}: <{message}>")#
            self.ready.add(message)
            for node in self.ready_subscribe_sample:
                self.node.send(node, "Ready", message, self.node, self.broadcast_channel)
        elif event == "ReadySubscribe":
            for message in self.ready:
                self.node.send(source, "Ready", message, self.node, self.broadcast_channel)
            self.ready_subscribe_sample.add(source)

        elif event == "Ready":
            if source in self.ready_sample:
                if message not in self.ready_replies[source]:
                    self.ready_replies[source].add(message)
                self.check_ready(message)
            if source in self.delivery_sample:
                # Add the reply only if it's not already present
                if message not in self.delivery_replies[source]:
                    self.delivery_replies[source].add(message)
                self.check_delivery(message)

        elif event == "achieved consensus":
            print(f"{self.node} delivered {message}")
            pass

    def check_ready(self, message):
        # if message not in self.ready:
        ready_count = sum(1 for reply in self.ready_replies.values() if message in reply)
        if ready_count >= Param.R_tilda and not self.delivered and not self.already_executed_flag:
            self.already_executed_flag = True
            self.ready.add(message)
            self.ready_delivered = True
            for target in self.ready_subscribe_sample:
                self.node.send(target, "Ready", message, self.node,self.broadcast_channel)

    def check_delivery(self, message):
        # Check if enough Delivery confirmations have been received to consider the message "delivered"
        delivery_count = sum(1 for reply in self.delivery_replies.values() if message in reply)
        if delivery_count >= Param.D_tilda and not self.delivered:
            self.delivered = True
            self.node.receive("achieved consensus", message)