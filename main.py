import sys
import random
import threading
import logging
from Actors.Node import Node
from Config.InputsConfig import InputsConfig as P
from Statistics import Statistics as ST
from Blocks.Transaction import TransactionPool
from Config.InputsConfig import CustomFormatter

sys.setrecursionlimit(30000)
random.seed(10)
def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # Configure logging with the custom formatter
    console = logging.StreamHandler()
    console.setFormatter(CustomFormatter())
    logging.getLogger('').addHandler(console)


# logging.basicConfig(level=logging.INFO, format='%(levelname)s --- %(message)s')


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
    configure_logging()
    logging.info(f"# of nodes: {P.Total_nodes} with {P.G} neighbors.")

    P.all_nodes = create_nodes(P.Total_nodes, P.byzantine_percentage)
    P.Shared_pool = TransactionPool()

    # Select sender
    sender = random.choice(P.all_nodes)
    sender.byzantine = True
    logging.info(f"Sender is: {sender}")

    threads = []
    for node in P.all_nodes:
        thread = threading.Thread(target=node.create_and_broadcast_multiple, args=(sender, P.BlockchainSize))
        threads.append(thread)
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Display messages
    ST.display_delivery_rate()
    # ST.display_bc_statistics()
