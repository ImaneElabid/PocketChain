import time
from time import sleep

from src.common.config import load_config, show_config
from src.common.network import init_network, init_PC, concurrent_submit_TXs
from src.common.statistics import Statistics
from src.common.utils import wait_until_all_submitted, prexit, log

if __name__ == '__main__':
    # Load and update configs
    config = load_config(seed=10)
    config.mp = 1
    config.num_nodes = 200
    config.perc_announcers = 0.05
    config.perc_processors = 0.5
    show_config(config)
    # Set up Statistics
    Statistics.config = config
    # Initialize Network
    nodes = init_network(config)
    # Initialize PocketChain
    init_PC(nodes)
    # Create transactions
    # submit_TXs(nbr_txs=5000)
    t = time.time()
    concurrent_submit_TXs(nbr_txs=5000)
    # wait for submission
    wait_until_all_submitted(nodes, stop=True)
    # get statistics
    log('warning', f"Sleeping for 2 second(s)")
    sleep(2)
    Statistics.display_energy()
    Statistics.display_delivery_rate()
    Statistics.display_bloc_stats()
    Statistics.display_endorsement_rate()
    Statistics.display_endorsement_stats(config)
    Statistics.display_bc_statistics()
    prexit(f"Finished in {time.time() - t:.4f} seconds.")
