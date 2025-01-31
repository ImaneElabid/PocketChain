from __future__ import annotations

from threading import Lock
from typing import Optional

import numpy as np

from src.common.helpers import Map
from src.common.utils import log


class Registry:
    nodes = {}
    size = 0
    lock = Lock()

    @classmethod
    def register(cls, node):
        # with cls.lock:
        cls.nodes[node.pub_key] = Map({
            'instance': node,
            'pub_key': node.pub_key,
            'host': node.host,
            'port': node.port,
            'role': "Client"
        })
        cls.size += 1

    @classmethod
    def register_as_announcer(cls, node):
        # with cls.lock:
        try:
            cls.register(node)
            if node.verify_stake():
                cls.nodes[node.pub_key].role = "Announcer"
                # log('event', f"{node} registered as an Announcer.")
        except Exception as e:
            cls.unregister(node.pub_key)
            log('error', f"{node} field to register as an announcer: {e}")

    @classmethod
    def register_as_processor(cls, node):
        # with cls.lock:
        try:
            cls.register(node)
            if node.verify_storage():
                cls.nodes[node.pub_key].role = "Processor"
                # log('event', f"{node} registered as a Processor.")
        except Exception as e:
            cls.unregister(node.pub_key)
            log('error', f"{node} field to register as a processor: {e}")

    @classmethod
    def unregister(cls, pub_key):
        # with cls.lock:
        if pub_key in cls.nodes:
            node = cls.nodes[pub_key]
            log('info', f"{node} has been unregistered.")
            del cls.nodes[pub_key]
            del node
            cls.size -= 1

    @classmethod
    def get_node_info(cls, pub_key):
        # with cls.lock:
        return cls.nodes.get(pub_key, None)

    @classmethod
    def get_random_node(cls, role: Optional[str] = None, nbr: int = 1):
        # with cls.lock:
        if role == "Client":
            nodes = Registry.get_clients()
        elif role == "Announcer":
            nodes = Registry.get_announcers()
        elif role == "Processor":
            nodes = Registry.get_processors()
        else:
            nodes = Registry.nodes
        key = np.random.choice(list(nodes.keys()))
        return nodes[key]

    @classmethod
    def get_announcers(cls, q=None) -> dict:
        # with cls.lock:
        announcers = {pub_key: node for pub_key, node in cls.nodes.items() if node['role'] == 'Announcer'}
        if q is None:
            return announcers
        else:
            keys = list(announcers.keys())
            if len(keys) < q:
                log('error', f"Number of Announcers in the system {len(keys)} < {q}.")
                exit()
            else:
                selected_keys = np.random.choice(keys, q, replace=False)
                return {key: announcers[key] for key in selected_keys}

    @classmethod
    def get_processors(cls) -> dict:
        # with cls.lock:
        return {pub_key: node for pub_key, node in cls.nodes.items() if node['role'] == 'Announcer'}

    @classmethod
    def get_clients(cls) -> dict:
        # with cls.lock:
        return {pub_key: node for pub_key, node in cls.nodes.items() if node.role == 'Client'}

    @classmethod
    def omega(cls, size) -> set:
        # with cls.lock:
        roles = ["Processor", "Announcer"]
        if size > cls.size:
            log('error', f"Sample size exceeds number of nodes in PC ({cls.size}).")
            exit("Terminated in registry.py::102")
        return set(
            np.random.choice([n.instance for n in cls.nodes.values() if n.role in roles], size, replace=False))
