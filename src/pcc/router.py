import hashlib
import random
import time
from threading import Lock

from src.common.helpers import Map
from src.pcc.echo_broadcast import EchoBroadcast
from src.pcc.gossip_broadcast import GossipBroadcast
from src.pcc.ready_broadcast import ReadyBroadcast


class Router:
    def __init__(self, node):
        self.lock = Lock()
        self.node = node
        self.role = node.role
        self.table = {}

    def add_channel(self, channel_id=None):
        """Add a new channel to the routing table."""
        if channel_id is None:
            channel_id = self.generate_channel_id(size=10)
        self.table[channel_id] = None
        gossip_layer = GossipBroadcast(self.node, channel_id)
        echo_layer = EchoBroadcast(self.node, gossip_layer, channel_id)
        ready_layer = ReadyBroadcast(self.node, echo_layer, channel_id)
        channel = Map({
            'channel_id': channel_id,
            'gossip_layer': gossip_layer,
            'echo_layer': echo_layer,
            'ready_layer': ready_layer,
            'delivered': False
        })
        self.table[channel_id] = channel
        ready_layer.init()

        return channel

    def remove_channel(self, h_id):
        """Remove an instance from the routing table."""
        if h_id in self.table:
            del self.table[h_id]
        print(self.table)

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

    @classmethod
    def generate_channel_id(cls, size=None):
        """hash code as an id for the virtual broadcast channel"""
        raw_id = f"{id}-{time.time()}-{random.random()}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:size]

    def __repr__(self):
        return f"({self.table})"

    def __str__(self):
        return f"({self.table})"
