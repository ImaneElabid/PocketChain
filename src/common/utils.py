import random
import socket
import time
from datetime import datetime

from termcolor import cprint

import src.common.globals as GLOB


# from src.common.crypto import calculate_hash


def log(mtype, message):
    title = True
    if not mtype:
        title = False
        mtype = GLOB.OLD_TYPE
    GLOB.old_type = mtype
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


def network_delay(delay=0.01):
    """
    Network delay in seconds
    """
    mean_delay = delay / 10
    std_delay = delay / 100
    delay = delay + random.normalvariate(mean_delay, std_delay)
    delay = max(delay, 0)
    time.sleep(delay)
