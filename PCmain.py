import numpy as np

from src.common.config import load_config, show_config
from src.common.network import init_network, init_PC, submit_TXs
from src.common.statistics import Statistics

if __name__ == '__main__':
    # Load and update configs
    config = load_config(seed=10)
    config.num_nodes = 500
    config.perc_announcers = 0.01
    config.perc_processors = 0.2
    show_config(config)
    # Initialize Network
    nodes = init_network(config)
    # Initialize PocketChain
    init_PC(nodes)
    # Create transactions
    submit_TXs(nbr_txs=500)
    # get statistics
    Statistics.display_PC_stats()

    # plots
    # plot_throughput()
    # plot_energy()
