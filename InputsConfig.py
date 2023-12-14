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
    all_nodes = []     # List of nodes

    # Sampling oracle
    def omega(all_nodes, size):
        return random.sample(all_nodes, int(size))


    #  hash code for virtual broadcast channel
    def hid(id):
        # Generate a unique hash ID based on node ID, timestamp, and a random component
        raw_id = f"{id}-{time.time()}-{random.random()}"
        return hashlib.sha256(id.encode()).hexdigest()

