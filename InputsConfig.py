import math
import hashlib
import random
import time


class InputsConfig:
    N = 100  # Number of nodes
    G = math.ceil(math.log(N))  # Expected gossip sample size
    E = G  # echo sample size
    R = G  # Ready sample size
    D = G  # Delivery sample size
    E_tilda = G  # Echo threshold
    R_tilda = G  # Ready threshold
    D_tilda = G  # Delivery threshold
    all_nodes = []  # List of nodes

    # Sampling oracle
    def omega(all_nodes, size):
        return random.sample(all_nodes, int(size))

    # hash code for virtual broadcast channel
    def hid(id):
        # Generate a unique hash ID based on node ID, timestamp, and a random component
        raw_id = f"{id}-{time.time()}-{random.random()}"
        return hashlib.sha256(id.encode()).hexdigest()


class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]
