import logging

from InputsConfig import InputsConfig as Param


class GossipBroadcast:
    def __init__(self, node, hid):
        self.node = node
        self.gossip_sample = set()
        self.gossip = None
        self.broadcast_channel = hid
        self.init()

    def init(self):
        self.gossip_sample = set(Param.omega(Param.all_nodes, Param.G))
        for target in self.gossip_sample.copy():
            self.node.send(target, "GossipSubscribe", None, self.node, self.broadcast_channel)

    def broadcast(self, message):
        self.node.receive("Broadcast", message, self.broadcast_channel)
        print(self.node.routing_table)

    def dispatch(self, message):
        if self.gossip is None:
            self.gossip = message
            for target in self.gossip_sample:
                self.node.send(target, "Gossip", message, self.node, self.broadcast_channel)
            self.node.receive("delivered a gossip", message)

    def handle(self, event, message, source):
        if event == "Broadcast":
            print(message)
            self.dispatch(message)

        elif event == "GossipSubscribe":
            if self.gossip is not None:
                message = self.gossip
                self.node.send(source, "Gossip", message, self.node, self.broadcast_channel)
            self.gossip_sample.add(source)

        elif event == "Gossip":
            self.dispatch(message)
