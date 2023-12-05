import random
import math
import threading
import time
from Node import Node

if __name__ == "__main__":
    N = 10  # Number of nodes
    G =  2   #math.log(N)  # Expected gossip sample size
    E =  2   #int(math.log(N))  # echo sample size
    R =  2   #int(math.log(N))  # Ready sample size
    D =  2   #int(math.log(N))  # Delivery sample size
    R_tilda = 2  #int(R / 2)  # Contagion threshold
    D_tilda = 2  #int(D / 2)  # Delivery threshold
    E_tilda =  2 #int(E / 2)  # Echo threshold
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
    starter_node = random.choice(nodes)
    print(f"{starter_node} is broadcasting....")
    message = f"Node {starter_node.id} is a leader"
    starter_node.receive("Broadcast", message)


    # Display messages
    # Check how many nodes received the message
    g_delivered_count = sum(1 for node in nodes if node.gossip)
    e_delivered_count = sum(1 for node in nodes if node.echo_delivered)
    delivered_count = sum(1 for node in nodes if node.delivered)
    # print(f"XXXXXX {len([node.id for node in nodes if not node.gossip_delivered])} nodes couldn't deliver XXXXXX")
    print(f"{g_delivered_count} / {N} nodes gossiped the message")
    print(f"{e_delivered_count} / {N} nodes echoed the message")
    print(f"{delivered_count} / {N} nodes delivered the message")

