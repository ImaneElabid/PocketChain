from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

import src.common.globals as GLOB
from src.blockchain.block import Block
from src.blockchain.registry import Registry
from src.blockchain.transaction import Transaction
from src.common.helpers import Map, timeit
from src.common.statistics import Statistics
from src.common.utils import log
from src.nodes.announcer import Announcer
from src.nodes.byzantine import Byzantine
from src.nodes.client import Client
from src.nodes.processor import Processor


@timeit
def init_network(config):
    # nodes handling
    log('event', f"init_network()")
    nodes_ids = list(range(config.num_nodes))
    num_processors = int(config.perc_processors * config.num_nodes)
    num_announcers = int(config.perc_announcers * config.num_nodes)
    config.G = int(np.log(num_processors + num_announcers)) + 1
    config.endorse_threshold = (num_announcers // 2)
    # Get unique processor_ids
    processor_ids = np.random.choice(nodes_ids, num_processors, replace=False)
    nodes_ids = np.setdiff1d(nodes_ids, processor_ids)
    # Get unique byz_ids
    byz_ids = np.random.choice(nodes_ids, config.num_byz, replace=False)
    nodes_ids = np.setdiff1d(nodes_ids, byz_ids)
    # Get unique announcer_ids
    announcer_ids = np.random.choice(nodes_ids, num_announcers, replace=False)
    nodes_ids = np.setdiff1d(nodes_ids, announcer_ids)
    processors = [Processor(config) for _ in processor_ids]
    announcers = [Announcer(config) for _ in announcer_ids]
    byzantines = [Byzantine(config) for _ in byz_ids]
    clients = [Client(config) for _ in nodes_ids]
    # Statistics
    Statistics.nbr_clients = len(clients)
    Statistics.nbr_processors = len(processors)
    Statistics.nbr_announcers = len(announcers)
    Statistics.nbr_byzantines = len(byzantines)
    # Start node instances
    for node in announcers + processors + byzantines + clients:
        node.start()

    return Map({'clients': clients, 'processors': processors, 'announcers': announcers, 'byzantines': byzantines})


@timeit
def init_PC(nodes):
    # Generate PocketChain genesis block
    genesis_node = nodes.announcers[0]
    log('info', f"Genesis node: {genesis_node}")
    genesis_block = create_genesis_block(genesis_node)
    # Populate all participants [Announcers and Processors] with genesis block.
    [announcer.local_chain.append(genesis_block) for announcer in nodes.announcers]
    [processor.local_chain.append(genesis_block) for processor in nodes.processors]
    log('info', f"Genesis block propagated to all PocketChain participants")
    # Initialize Announcers staking
    init_announcers(nodes.announcers)
    # Initialize Processors requirements
    init_processors(nodes.processors)
    # Initialize Clients
    init_clients(nodes.clients)


@timeit
def init_announcers(announcers):
    n = len(announcers)
    connected = True
    # Verify staking and join the network as an announcer
    for i in range(n):
        announcer = announcers[i]
        announcer.stake()
        Registry.register_as_announcer(announcer)
        # connect announcers to each other
        for j in range(n):
            if i == j:
                continue
            if not announcer.connect(announcers[j]):
                log('error', f"{announcer} --> {announcers[j]} Not connected")
                connected = False
    if connected:
        log('success', f"Announcers successfully connected with each other.")
    else:
        log('error', f"Some Announcers could not connect.")


@timeit
def init_processors(processors):
    # Verify staking and join the network as an announcer
    for processor in processors:
        processor.allocate_storage()
        Registry.register_as_processor(processor)
        processor.discover_announcers()


def init_clients(clients):
    # Verify staking and join the network as an announcer
    for client in clients:
        client.role = "Client"
        Registry.register(client)
        client.subscribe_to_announcers(client.config.Qsub)


def submit_transaction(PCs: int = 2):
    sender_info = Registry.get_random_node(role="Client")
    sender: Client = sender_info.instance
    recipient_info = Registry.get_random_node(role="Client")
    tips_to_spend = np.random.randint(GLOB.MIN_TIPS, GLOB.MIN_TIPS * 10)
    tx = sender.create_transaction(receiver=recipient_info.pub_key, amount=PCs)
    if tx is not None:
        sender.submit_transaction(tx, tips_to_spend)
    return str(tx)


# @timeit
def submit_TXs(nbr_txs=120):
    log('info', f"Submitting {nbr_txs} transactions...")
    for i in range(nbr_txs):
        submit_transaction(PCs=2)


@timeit
def concurrent_submit_TXs(nbr_txs: int = 2000, max_workers: int = 10):
    log('info', f"Submitting {nbr_txs} transactions concurrently...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_tx = {
            executor.submit(submit_transaction): i
            for i in range(nbr_txs) if Statistics.stop_now != True
        }
        for future in as_completed(future_to_tx):
            # you can retirve the return of `submit_transaction()`
            _ = future.result()
        log('success', f"{nbr_txs} have been successfully submitted")


def create_genesis_block(node_zero):
    zero_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    coinbase_transaction = Transaction(GLOB.NODE_ZERO_BALANCE, sender=None, recipient=node_zero.pub_key, tip=0)
    coinbase_transaction.build().sign(node_zero.prv_key)
    genesis_block = Block("IMANE", [coinbase_transaction], block_state=GLOB.BLOCK_FINAL)
    genesis_block.prev_hash = zero_hash
    genesis_block.hash = zero_hash
    genesis_block.merkle_root = zero_hash
    genesis_block.prev_block = None
    genesis_block.endorsements = {i: f"GENESIS_{i}" for i in range(GLOB.MIN_ENDORSE)}
    genesis_block.compute_block_hash(None, confirmed=True)
    log('info', f"Genesis block created with {GLOB.NODE_ZERO_BALANCE} PCs for node: {node_zero}")
    return genesis_block
