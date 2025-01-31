import inspect
import os
import random
import socket
import sys
from datetime import datetime

from termcolor import cprint, colored

import src.common.globals as GLOB


# from src.common.crypto import calculate_hash


def log(mtype, message):
    title = True
    if not mtype:
        title = False
        mtype = GLOB.OLD_TYPE
    GLOB.OLD_TYPE = mtype
    if GLOB.VERBOSE >= 0:
        if mtype == "result":
            if title:
                cprint("\r Result:  ", 'blue', attrs=['reverse'], end=' ', flush=True)
            else:
                cprint("          ", 'blue', end=' ')
            cprint(str(message), 'blue')
            GLOB.OLD_TYPE = 'result'
            return
    if GLOB.VERBOSE >= 1:
        if mtype == "error":
            if title:
                cprint("\r Error:   ", 'red', attrs=['reverse'], end=' ', flush=True)
            else:
                cprint("          ", 'red', end=' ')
            cprint(str(message), 'red')
            GLOB.OLD_TYPE = 'error'
            return
        elif mtype == "success":
            if title:
                cprint("\r Success: ", 'green', attrs=['reverse'], end=' ', flush=True)
            else:
                cprint("          ", 'green', end=' ')
            cprint(str(message), 'green')
            GLOB.OLD_TYPE = 'success'
            return
    if GLOB.VERBOSE > 1:
        if mtype == "event":
            if title:
                cprint("\r Event:   ", 'cyan', attrs=['reverse'], end=' ', flush=True)
            else:
                cprint("          ", 'cyan', end=' ')
            cprint(str(message), 'cyan')
            GLOB.OLD_TYPE = 'event'
            return
        elif mtype == "warning":
            if title:
                cprint("\r Warning: ", 'yellow', attrs=['reverse'], end=' ', flush=True)
            else:
                cprint("          ", 'yellow', end=' ')
            cprint(str(message), 'yellow')
            GLOB.OLD_TYPE = 'warning'
            return
    if GLOB.VERBOSE > 2:
        if mtype == "info":
            if title:
                cprint("\r Info:    ", attrs=['reverse'], end=' ', flush=True)
            else:
                cprint("          ", end=' ')
            cprint(str(message))
            GLOB.OLD_TYPE = 'info'
            return
    if GLOB.VERBOSE > 2:
        if mtype not in ["info", "warning", "event", "success", "error", "result"]:
            if title:
                cprint("\r Log:     ", 'magenta', attrs=['reverse'], end=' ', flush=True)
            else:
                cprint("          ", end=' ')
            cprint(str(message))
            log.OLD_TYPE = 'log'


def create_tcp_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, GLOB.TCP_SOCKET_BUFFER_SIZE)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, GLOB.TCP_SOCKET_BUFFER_SIZE)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sock


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(10)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return socket.gethostbyname(socket.gethostname())
    finally:
        s.close()


def execute_node(node):
    """Wrapper to call the run method of Node."""
    print(f"{node} is starting")
    node.run()


def current_timestamp():
    return datetime.now().timestamp()


def timestamp_to_time(timestamp):
    return datetime.fromtimestamp(timestamp)


def compute_merkle_root(transactions):
    if not transactions:
        return None
    if len(transactions) == 1:
        return calculate_hash(transactions[0])
    else:
        mid = len(transactions) // 2
        left_root = compute_merkle_root(transactions[:mid])
        right_root = compute_merkle_root(transactions[mid:])
        return calculate_hash(left_root + right_root)


def network_normalvariate_delay(delay=0.1):
    """
    Network delay in seconds
    """
    mean_delay = delay / 10
    std_delay = delay / 100
    delay = delay + random.normalvariate(mean_delay, std_delay)
    delay = max(delay, 0)
    print(f"Network delay: {delay}")
    time.sleep(delay)


def random_delay(delay=0.1):
    delay = random.uniform(0, delay)
    time.sleep(delay)


def prexit(msg, color="red", deep=False):
    caller_frame = inspect.stack()[1]
    filename = os.path.basename(caller_frame.filename)
    line_number = caller_frame.lineno
    file = colored(f"\r {filename}::{line_number}", color=color, attrs=['reverse'])
    if not deep:
        print(f"{file}\n{msg}", flush=True)
    else:
        print(f"{file}\n{msg}\n>>{msg} attributes:\n{vars(msg)}", flush=True)

    os._exit(0)
    sys.exit(0)


import time


def wait_until_all_submitted(nodes, timeout: int = 10, check_interval: float = 0.5, stop=False) -> bool:
    log('warning', "Waiting for all nodes to finish...")
    start_time = time.time()
    announcers = nodes.announcers

    while True:
        time.sleep(check_interval)
        if time.time() - start_time > timeout:
            return False
        # Assume all nodes are done until we find one that isn't
        all_nodes_done = True
        for node in announcers:
            if node.active_endorsement_phase:
                all_nodes_done = False
                break
        if all_nodes_done:
            for a in nodes.announcers:
                log('info', f"{a} has {len(a.mempool.transactions)} unprocessed transactions.")
            unprocessed_txs = sum(len(a.mempool.transactions) for a in nodes.announcers)
            if stop:
                for node in sum(nodes.values(), []):
                    node.stop()
                log('success', f"Announcers finished with {unprocessed_txs} unprocessed transactions...")
            return True


def transmission_energy(bits, users=0, rate=7736500, pm=0.01, ps=1):
    T = bits / rate  # Time in seconds
    # Calculate energy
    energy_mobile = pm * T  # Energy for mobile in joules
    energy_server = ps * T  # Energy for server in joules
    if users > 0:
        energy_mobile = energy_mobile / users
        energy_server = energy_server / users

        # Print results
    log('result', f"Message size: {bits} bits")
    log('', f"Transmission rate: {rate} bits/second")
    log('', f"Transmission T: {T:.5f} seconds")
    log('', f"Mobile energy consumption: {energy_mobile:.5f} joules")
    log('', f"Server energy consumption: {energy_server:.4f} joules")
