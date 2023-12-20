import sys
import random
import threading
import logging
from Node import Node
from InputsConfig import InputsConfig as Param
from Statistics import Statistics as ST

sys.setrecursionlimit(30000)
random.seed(10)

logging.basicConfig(level=logging.INFO, format='%(levelname)s --- %(message)s')


def create_nodes(total_nodes, byzantine_percentage):
    byzantine_count = int(total_nodes * byzantine_percentage / 100)
    nodes = []

    for i in range(total_nodes):
        if i < byzantine_count:
            nodes.append(Node(i, byzantine=True))
        else:
            nodes.append(Node(i))
    # Shuffle the list so that Byzantine nodes are randomly distributed
    random.shuffle(nodes)
    return nodes


if __name__ == "__main__":
    logging.info(f"# of nodes: {Param.Total_nodes} with {Param.G} neighbors.")

    Param.all_nodes = create_nodes(Param.Total_nodes, Param.byzantine_percentage)

    # Select sender
    sender = random.choice(Param.all_nodes)
    logging.info(f"Sender is: {sender}")
    # message2 = f"Bye"
    # messages = [message1, message2]

    threads = []
    for node in Param.all_nodes:
        thread = threading.Thread(target=node.create_and_broadcast, args=(sender,))
        threads.append(thread)
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()




    # Display messages
    ST.display()
