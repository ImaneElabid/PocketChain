import sys
import random
import threading
import logging
from Node import Node
from InputsConfig import InputsConfig as Param

sys.setrecursionlimit(30000)
random.seed(10)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info(f"# of nodes: {Param.N}")
    logging.info(f"# of neighbors: {Param.G}")

    Param.all_nodes = [Node(i) for i in range(Param.N)]

    sender = random.choice(Param.all_nodes)
    print(f"{sender} is broadcasting....")
    message = f"{sender} is a leader"

    threads = []
    for node in Param.all_nodes:
        thread = threading.Thread(target=node.node_thread_init, args=(sender,message,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Display messages
    # Check how many nodes received the message
    # g_delivered_count = sum(1 for node in Param.all_nodes if node.gossip_layer.gossip)
    # e_delivered_count = sum(1 for node in Param.all_nodes if node.echo_layer.echo_delivered)
    # r_delivered_count = sum(1 for node in Param.all_nodes if node.ready_layer.ready_delivered)
    # delivered_count = sum(1 for node in Param.all_nodes if node.ready_layer.delivered)
    # # print(f"XXXXXX {len([node.id for node in nodes if not node.gossip_delivered])} nodes couldn't deliver XXXXXX")
    # print(f"{g_delivered_count} / {Param.N} nodes gossiped the message")
    # print(f"{e_delivered_count} / {Param.N} nodes echoed the message")
    # print(f"{r_delivered_count} / {Param.N} nodes readied the message")
    # print(f"{delivered_count} / {Param.N} nodes delivered the message")
    # if delivered_count < Param.N:
    #     logging.warning("Not all nodes have successfully delivered the message")

