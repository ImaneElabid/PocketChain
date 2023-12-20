import math
import hashlib
import random
import sys
import time
import json
sys.setrecursionlimit(1000000)


class InputsConfig:
    # Nodes parameters
    Total_nodes = 100  # Number of nodes
    byzantine_percentage = 0  # Percentage of Byzantine nodes
    all_nodes = []  # List of nodes

    # Broadcast parameters
    G = math.ceil((Total_nodes/10))  # Expected gossip sample size
    E = G  # echo sample size
    R = G  # Ready sample size
    D = G  # Delivery sample size
    E_tilda = G  # Echo threshold
    R_tilda = G  # Ready threshold
    D_tilda = G  # Delivery threshold

    # tx parameters
    Tdelay = 5.1
    Tfee = 0.000062  # The average transaction fee
    Tsize = 0.000546  # The average transaction size  in MB
    Default_Psize = 1

    # block parameters
    Bsize = 1.0  # The block size in MB
    Bdelay = 0.42  # average block propogation delay in seconds

    def omega(all_nodes, size):
        """Sampling oracle"""
        return random.sample(all_nodes, int(size))

    def hid(id):
        """hash code as an id for the virtual broadcast channel"""
        raw_id = f"{id}-{time.time()}-{random.random()}"
        return hashlib.sha256(id.encode()).hexdigest()

    @staticmethod
    def get_hash(message):
        """Return sha256 of the given message"""
        return hashlib.sha256(message.encode()).hexdigest()

    # def compute_hash(x: list):
    #     """Compute the hash of a list of elements
    #         --> prev_hash: [S, X, Y]
    #         --> state: [X, Y]
    #     """
    #     message = ""
    #     for i in x:
    #         if isinstance(i, list):
    #             if len(i) > 0 and hasattr(i[0], 'value'):
    #                 message += json.dumps([trans.value for trans in i], sort_keys=True)
    #         elif isinstance(i, int):
    #             # message += json.dumps([str(i)], sort_keys=True)
    #             message += str(i)
    #         else:
    #             message += i
    #         dd = get_hash(message)
    #         # print(f">> Hash: {get_hash(message)} ---> {message}")
    #     return dd

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

