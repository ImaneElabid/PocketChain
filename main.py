import sys
import random
import math
import threading
import time
from Node import Node

if __name__ == "__main__":
    sys.setrecursionlimit(30000)
    N = 100  # Number of nodes
    G =  math.ceil(math.log(N))  # Expected gossip sample size
    E =  G  # echo sample size
    R =  G  # Ready sample size
    D =  G  # Delivery sample size
    E_tilda = G  # Echo threshold
    R_tilda = G  # Contagion/Ready threshold
    D_tilda = G  # Delivery threshold
    print(f"Number of neighbors: {math.log(N)}")
    random.seed(10)
    print(f"E={E}  ---- R={R} ---- D={D} ---- E_tilda={E_tilda} ---- R_tilda={R_tilda} ---- D_tilda={D_tilda}")
    # Create nodes
    nodes = [Node(i, G, E, R, D, R_tilda, D_tilda, E_tilda) for i in range(N)]

    for node in nodes:
        node.all_nodes = nodes
        # Initialize each node
    # Create and start a thread for each node's initialization and gossip start
    threads = []
    for node in nodes:
        thread = threading.Thread(target=node.node_thread_init, args=())
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
        # Start gossip from this node

    # starter_node = random.choice(nodes)
    # print(f"{starter_node} is broadcasting....")
    # message = f"Node {starter_node.id} is a leader"
    # starter_node.receive("Broadcast", message)

    Node.broadcast_malicious(Node, nodes)


    # Display messages
    # Check how many nodes received the message
    g_delivered_count = sum(1 for node in nodes if node.gossip)
    e_delivered_count = sum(1 for node in nodes if node.echo_delivered)
    r_delivered_count = sum(1 for node in nodes if node.ready_delivered)
    delivered_count = sum(1 for node in nodes if node.delivered)
    # print(f"XXXXXX {len([node.id for node in nodes if not node.gossip_delivered])} nodes couldn't deliver XXXXXX")
    print(f"{g_delivered_count} / {N} nodes gossiped the message")
    print(f"{e_delivered_count} / {N} nodes echoed the message")
    print(f"{r_delivered_count} / {N} nodes readied the message")
    print(f"{delivered_count} / {N} nodes delivered the message")

