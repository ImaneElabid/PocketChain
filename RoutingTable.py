from EchoBroadcast import EchoBroadcast
from GossipBroadcast import GossipBroadcast
from ReadyBroadcast import ReadyBroadcast
from InputsConfig import Map


class RoutingTable:
    def __init__(self, node):
        self.node = node
        self.table = {}

    def add_channel(self, channel_id):
        """Add a new channel to the routing table."""
        gossip_layer = GossipBroadcast(self.node, channel_id)
        echo_layer = EchoBroadcast(self.node, gossip_layer, channel_id)
        ready_layer = ReadyBroadcast(self.node, echo_layer, channel_id)
        channel = Map({'gossip_layer': gossip_layer, 'echo_layer': echo_layer, 'ready_layer': ready_layer})
        self.table[channel_id] = channel
        ready_layer.init()
        return channel

    def remove_channel(self, h_id):
        """Remove an instance from the routing table."""
        if h_id in self.table:
            del self.table[h_id]

    def get_channel(self, h_id):
        """Retrieve an instance from the routing table."""
        return self.table.get(h_id)

    def handle_message(self, h_id, event, message, source):
        """Route the message to the correct instance based on h_id."""
        if h_id in self.table:
            instance = self.table[h_id]
            instance.handle(event, message, source)

    def send(self, target, event, message, source=None, hid=None):
        self.node.send(target, event, message, source, hid)

    def channel_exist(self, channel_id):
        return channel_id in self.table

    def __repr__(self):
        return f"({self.table})"

    def __str__(self):
        return f"({self.table})"
