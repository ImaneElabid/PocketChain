import argparse
import random

import numpy as np

import src.common.globals as GLOB
from src.common.utils import log


def load_config(seed=None):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    parser = argparse.ArgumentParser()
    # Nodes parameters
    parser.add_argument('--num_nodes', type=int, default=GLOB.TOTAL_NODES, help="number of nodes in the network")
    parser.add_argument('--perc_processors', type=float, default=0.2, help="percentage of processors nodes")
    parser.add_argument('--perc_announcers', type=int, default=0.01, help="percentage of announcer nodes")
    parser.add_argument('--num_byz', type=int, default=0, help="number of Byzantine nodes in the network")
    # PocketChain parameters
    parser.add_argument('--Qsub', type=int, default=GLOB.QSUB, help="Number of announcers to subscribe to")
    parser.add_argument('--min_tips', type=int, default=GLOB.MIN_TIPS, help="minimum number of tips")
    parser.add_argument('--staked', type=int, default=GLOB.STAKE_AMOUNT, help="amount of staked PCs")
    parser.add_argument('--stake_expiry', type=int, default=GLOB.STAKE_EXPIRY, help="stake expiry time in seconds")
    parser.add_argument('--min_storage', type=int, default=GLOB.MIN_STORAGE, help="minimum amount of reserved storage")
    parser.add_argument('--max_block_size', type=int, default=GLOB.MAX_BLOCK_SIZE, help="maximum block size")
    # Endorsement parameters
    parser.add_argument('--endorse_threshold', type=int, default=GLOB.QSUB, help="Endorsement threshold")
    # pcc parameters
    parser.add_argument('--G', type=int, default=GLOB.G, help="Gossip sample size")
    parser.add_argument('--E', type=int, default=GLOB.G, help="Echo sample size")
    parser.add_argument('--R', type=int, default=GLOB.G, help="Ready sample size")
    parser.add_argument('--D', type=int, default=GLOB.G, help="Delivery sample size")
    parser.add_argument('--E_tilda', type=int, default=GLOB.G_TILDA, help="Echo threshold")
    parser.add_argument('--R_tilda', type=int, default=GLOB.G_TILDA, help="Ready threshold")
    parser.add_argument('--D_tilda', type=int, default=GLOB.G_TILDA, help="Delivery threshold")
    # Software parameters
    parser.add_argument('--mp', type=int, default=0, help="Use message passing (1) or shared memory (0)")
    parser.add_argument('--verbose', type=int, default=GLOB.VERBOSE, help='verbose')
    parser.add_argument('--seed', type=int, default=GLOB.SEED, help='random seed')

    return parser.parse_args()


def show_config(config):
    log('success', f"Software parameters")
    log('', f"Communication channel : {'TCP' if config.mp else 'Shared memory'}")
    log('', f"Verbose: {config.verbose}")
    log('success', f'Network configuration:')
    log('', f"Total number of nodes: {config.num_nodes}")
    log('', f"Number of announcer nodes: {int(config.num_nodes * config.perc_announcers)}")
    log('', f"Number of processor nodes: {int(config.num_nodes * config.perc_processors)}")
    log('', f"Number of Byzantine nodes: {config.num_byz}")
    log('success', f'PocketChain configuration:')
    log('', f"Number of announcers to subscribe to: {config.Qsub}")
    log('', f"Minimum number of tips: {config.min_tips}T")
    log('', f"Amount of PCs to stake: {config.staked}PCs")
