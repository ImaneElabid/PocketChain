import sys
import time

from src.blockchain.registry import Registry
from src.common import protocol
from src.common.helpers import Map
from src.common.statistics import Statistics
from src.common.utils import log
from src.pcc.echo_broadcast import EchoBroadcast


class ReadyBroadcast:
    def __init__(self, node, echo_layer, channel_id):
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
        self.channel_id = channel_id

        self.echo_layer: EchoBroadcast = echo_layer

    def init(self):
        self.echo_layer.init()
        # ready_sample
        self.ready_sample = Registry.omega(self.node.config.R)
        for target in self.ready_sample:
            msg = protocol.pcc_message(protocol.READY_SUBSCRIBE, self.node, self.channel_id)
            self.node.pcc_send(target, msg)
        self.ready_replies = {node.port: set() for node in self.ready_sample}
        # delivery_sample
        self.delivery_sample = Registry.omega(self.node.config.D)
        for target in self.delivery_sample:
            msg = protocol.pcc_message(protocol.READY_SUBSCRIBE, self.node, self.channel_id)
            self.node.pcc_send(target, msg)
        self.delivery_replies = {node.port: set() for node in self.delivery_sample}

    def broadcast(self, block):
        self.echo_layer.broadcast(block)

    def handle(self, msg):
        Statistics.exchanged_bytes += sys.getsizeof(msg) * 8
        if msg.mtype == protocol.DELIVERED_ECHO:
            if isinstance(msg.data, Map):
                msg.data = msg.data.data
            self.ready.add(msg.data)  # tempo
            for node in self.ready_subscribe_sample:
                ready_msg = protocol.pcc_message(protocol.READY, self.node, self.channel_id, msg.data)
                self.node.pcc_send(node, ready_msg)
        elif msg.mtype == protocol.READY_SUBSCRIBE:
            for message in self.ready:
                reply = protocol.pcc_message(protocol.READY, self.node, self.channel_id, message)
                self.node.pcc_send(msg.source, reply)
            self.ready_subscribe_sample.add(msg.source)
        elif msg.mtype == protocol.READY:
            if msg.source in self.ready_sample:
                if msg.data not in self.ready_replies[msg.source.port]:
                    self.ready_replies[msg.source.port].add(msg.data)
                self.check_ready(msg.data)
            if msg.source in self.delivery_sample:
                # Add the reply only if it's not already present
                if msg.data not in self.delivery_replies[msg.source.port]:  # tempo
                    self.delivery_replies[msg.source.port].add(msg.data)
                self.check_delivery(msg.data)
        elif msg.mtype == protocol.ACHIEVED_CONSENSUS:
            print(f"{self.node} | protocol.ACHIEVED_CONSENSUS | Received {msg.mtype}|{msg.data}")
            log('result', f"{self.node} -> ACHIEVED_CONSENSUS <{msg.data}>")

    def check_ready(self, message):
        # if message not in self.ready:
        ready_count = sum(1 for reply in self.ready_replies.values() if message in reply)
        if ready_count >= self.node.config.R_tilda and not self.delivered and not self.already_executed_flag:
            # print(f"{self.node} -> got enough ready.:")
            self.already_executed_flag = True
            self.ready.add(message)
            self.ready_delivered = True
            for target in self.ready_subscribe_sample:
                msg = protocol.pcc_message(protocol.READY, self.node, self.channel_id, message)
                self.node.pcc_send(target, msg)

    def check_delivery(self, message):
        # Check if enough Delivery confirmations have been received to consider the message "delivered"
        delivery_count = sum(1 for reply in self.delivery_replies.values() if message in reply)
        if delivery_count >= self.node.config.D_tilda and not self.delivered:
            self.delivered = True
            Statistics.channels[self.channel_id]['delivered'].append(self.node.port)
            Statistics.channels[self.channel_id]['end'] = time.time()
            Statistics.update_delivered(self.node.port, self.channel_id)
            msg = protocol.pcc_message(protocol.ACHIEVED_CONSENSUS, self.node, self.channel_id, message)
            self.node.pcc_receive(msg)

    def byz_handle(self, event, source, block1, block2):
        if event == "delivered an echo":
            ready_sample_list = list(self.ready_subscribe_sample)
            half = len(ready_sample_list) // 2
            first_half = ready_sample_list[:half]
            second_half = ready_sample_list[half:]

            for node in first_half:
                self.node.send(node, "Ready", block1, self.node, self.channel_id)

            for node in second_half:
                self.node.send(node, "Ready", block2, self.node, self.channel_id)

        elif event == "ReadySubscribe":
            for message in self.ready:
                self.node.send(source, "Ready", message, self.node, self.channel_id)
            self.ready_subscribe_sample.add(source)

        elif event == "Ready":
            # print(f"{self.node} -> {event}: <{message}> == {self.channel_id}")#
            if source in self.ready_sample:
                if block1 not in self.ready_replies[source.port]:
                    self.ready_replies[source.port].add(block1)
                if block2 not in self.ready_replies[source.port]:
                    self.ready_replies[source.port].add(block2)
                self.check_byz_ready(block1, block2)
            if source in self.delivery_sample:
                # Add the reply only if it's not already present
                if block1 not in self.delivery_replies[source.port]:
                    self.delivery_replies[source.port].add(block1)
                if block2 not in self.delivery_replies[source.port]:
                    self.delivery_replies[source.port].add(block2)
                self.node.receive("achieved consensus", block1, source=self.node, hid=self.channel_id)
                self.node.receive("achieved consensus", block2, source=self.node, hid=self.channel_id)

        elif event == "achieved consensus":
            print(f"{self.node} -> {event}: <{block1}> ")  #
            print(f"{self.node} -> {event}: <{block2}> ")  #

    def check_byz_ready(self, message1, message2):
        # if message not in self.ready:
        self.ready.add(message1)
        self.ready.add(message2)
        self.ready_delivered = True
        ready_sample_list = list(self.ready_subscribe_sample)
        half = len(ready_sample_list) // 2
        first_half = ready_sample_list[:half]
        second_half = ready_sample_list[half:]

        for node in first_half:
            self.node.send(node, "Ready", message1, self.node, self.channel_id)

        for node in second_half:
            self.node.send(node, "Ready", message2, self.node, self.channel_id)

    def __repr__(self):
        return f"RB({self.channel_id[:4]})"

    def __str__(self):
        return f"RB({self.channel_id[:4]})"
