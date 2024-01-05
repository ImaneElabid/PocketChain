import math
import hashlib
import random
import sys
import time

sys.setrecursionlimit(1000000)


class InputsConfig:
    # Nodes parameters
    Total_nodes = 100  # Number of nodes
    byzantine_percentage = 0  # Percentage of Byzantine nodes
    all_nodes = []  # List of nodes

    # Broadcast parameters
    G = math.ceil((Total_nodes / 10))  # Expected gossip sample size
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

    Shared_pool = None
    # block parameters
    Bsize = 2  # nbr of tx  >>>> The block size in MB
    Bdelay = 0.42  # average block propogation delay in seconds
    BlockInterval = 0.1
    BlockchainSize = 1  # + genesis block

    def omega(all_nodes, size):
        """Sampling oracle"""
        return random.sample(all_nodes, int(size))

    def hid(id):
        """hash code as an id for the virtual broadcast channel"""
        raw_id = f"{id}-{time.time()}-{random.random()}"
        return hashlib.sha256(raw_id.encode()).hexdigest()

    @staticmethod
    def get_hash(message):
        """Return sha256 of the given message"""
        return hashlib.sha256(message.encode()).hexdigest()

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


import logging

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    SUCCESS_LEVEL_NUM = 25
    logging.addLevelName(SUCCESS_LEVEL_NUM, 'SUCCESS')
    grey = "\x1b[38;21m"
    green = "\x1b[32;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(levelname)s] - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
