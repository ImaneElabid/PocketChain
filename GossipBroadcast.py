import logging

from InputsConfig import InputsConfig as Param


class GossipBroadcast:
    def __init__(self, node, channel_id):
        self.node = node
        self.gossip_sample = set()
        self.gossip = None
        self.channel_id = channel_id
        #self.init()

    def init(self):
        self.gossip_sample = set(Param.omega(Param.all_nodes, Param.G))
        for target in self.gossip_sample.copy():
            self.node.send(target, "GossipSubscribe", None, self.node, self.channel_id)

    def broadcast(self, message):
        self.node.receive("Broadcast", message, None, self.channel_id)

    def dispatch(self, message):
        if self.gossip is None:
            self.gossip = message
            for target in self.gossip_sample:
                self.node.send(target, "Gossip", message, self.node, self.channel_id)
            self.node.receive("delivered a gossip", message, self.node, self.channel_id)

    def handle(self, event, message, source):
        if event == "Broadcast":
            print(f"{self.node} -> {event}: <{message}> == {self.channel_id}")#
            self.dispatch(message)

        elif event == "GossipSubscribe":
            print(f"{self.node} -> {event}: <{message}> == {self.channel_id}")#
            if self.gossip is not None:
                message = self.gossip
                self.node.send(source, "Gossip", message, self.node, self.channel_id)
            self.gossip_sample.add(source)

        elif event == "Gossip":
            self.dispatch(message)



    def __repr__(self):
        return f"GB({self.channel_id[:4]})"

    def __str__(self):
        return f"GB({self.channel_id[:4]})"
