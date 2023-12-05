import random
import time

class Node:
    already_executed_flag = False
    def __init__(self, node_id, G, E, R, D, R_tilda, D_tilda, E_tilda):
        self.id = node_id
        self.G = G
        self.E = E
        self.R = R
        self.D = D
        self.R_tilda = R_tilda
        self.D_tilda = D_tilda
        self.E_tilda = E_tilda

        self.gossip_sample = set()
        self.gossip = None

        self.echo_sample = set()
        self.echo_subscribe_sample = set()
        self.echo_delivered = False
        self.echo = None
        self.echo_replies = {}


        self.ready_subscribe_sample = set()
        self.ready_sample = set()
        self.delivery_sample = set()

        self.ready = set()
        self.delivered = False
        self.ready_replies = {}
        self.delivery_replies = {}

    ##################################################################################################################
    def send(self, target, event, message, source=None):
        target.receive(event, message, source)

    def receive(self, event, message, source=None):
        if event == "GossipSubscribe":
            if self.gossip is not None:
                message = self.gossip
                self.send(source, "Gossip", message, self)
            self.gossip_sample.add(source)

        elif event == "Gossip":
            self.dispatch(message)

        elif event == "delivered a gossip":
            #print(f"{self} -> {event}: <{message}>")#
            self.echo = message
            for target in self.echo_subscribe_sample:
                self.send(target, "Echo", message, self)
            self.check_echo(message)

        elif event == "EchoSubscribe":
            if self.echo is not None:
                message = self.echo
                self.send(source, "Echo", message, self)
            self.echo_subscribe_sample.add(source)

        elif event == "Echo":
            print(f"{self} << Echo :: {source}")
            if source in self.echo_sample and self.echo_replies[source] is None:
                print(f"{self} ********** Echo :: {source}")
                self.echo_replies[source] = message
                self.check_echo(message)

        elif event == "delivered an echo":
            #print(f"{self} -> {event}: <{message}>")#
            self.ready.add(message)
            for node in self.ready_subscribe_sample:
                self.send(node, "Ready", message, self)

        if event == "ReadySubscribe":
            for message in self.ready:
                self.send(source, "Ready", message, self)
            self.ready_subscribe_sample.add(source)

        elif event == "Ready":
            #print(f"{self} << Ready :: {source}")
            reply=message
            if source in self.ready_sample:
                if reply not in self.ready_replies[source]:
                    self.ready_replies[source].add(reply)
                    print(f"{self} ******** Ready :: {source}")
                self.check_ready(message)
            if source in self.delivery_sample:
                # Add the reply only if it's not already present
                if reply not in self.delivery_replies[source]:
                    self.delivery_replies[source].add(reply)
                    print(f"{self} ******** Delivery :: {source}")
                self.check_delivery(message)

        elif event == "achieved consensus":
            print(f"{self} -> {event}: <{message}>")#

        elif event == "Broadcast":
            self.dispatch(message)

    def omega(self, size):
        return random.sample(self.all_nodes, int(size))

    def sample_and_send(self, message, size):
        sampled_nodes = self.omega(size)
        for node in sampled_nodes:
            self.send(node, message, None, self)
        return sampled_nodes

    def init(self):
        self.gossip_sample = set(self.omega(self.G))
        for target in self.gossip_sample:
            self.send(target, "GossipSubscribe", None, self)
        # print(f"{(self)} gossip sample: {self.gossip_sample}")

        self.echo_sample = self.sample_and_send("EchoSubscribe", self.E)
        self.echo_replies = {node: None for node in self.echo_sample}
        #print(f"{(self)} echo sample: {self.echo_sample}")

        self.ready_sample = self.sample_and_send("ReadySubscribe", self.R)
        self.ready_replies = {node_id: set() for node_id in self.ready_sample}
        print(f"{(self)} ready sample: {self.ready_sample}")

        self.delivery_sample = self.sample_and_send("ReadySubscribe", self.D)
        self.delivery_replies = {node_id: set() for node_id in self.delivery_sample}
        print(f"{(self)} delivery sample: {self.delivery_sample}")

    def dispatch(self, message):
        if self.gossip is None:
            self.gossip = message
            for target in self.gossip_sample:
                self.send(target, "Gossip", message, self)
        self.receive("delivered a gossip", message)

    def check_echo(self,message):
        # Count the number of echo replies that match self.echo
        echo_count = sum(1 for reply in self.echo_replies.values() if reply == self.echo)
        # If the count meets the threshold and the message hasn't been delivered yet, deliver the message
        if echo_count >= self.E_tilda and not self.echo_delivered:
            self.echo_delivered = True
            self.receive("delivered an echo", message)

    def check_ready(self,message):
        # if message not in self.ready:
            ready_count = sum(1 for reply in self.ready_replies.values() if message in reply)
            if ready_count >= self.R_tilda and not self.delivered and not self.already_executed_flag:
                self.already_executed_flag = True
                self.ready.add(message)
                for target in self.ready_subscribe_sample:
                    self.send(target, "Ready", message, self)

    def check_delivery(self, message):
        # Check if enough Delivery confirmations have been received to consider the message "delivered"
        delivery_count = sum(1 for reply in self.delivery_replies.values() if message in reply)
        if delivery_count >= self.D_tilda and not self.delivered:
            self.delivered = True
            self.receive("achieved consensus", message)

    def node_thread_init(self):
        self.init()




        # Special methods
    def __repr__(self):
        return f"Node({self.id})"

    def __str__(self):
        return f"Node({self.id})"


