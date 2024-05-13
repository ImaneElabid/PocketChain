import pickle

from src.blockchain.transaction import Transaction
from src.common.helpers import Map

LOGS = 0
CONNECT = 1
DISCONNECT = 2
TX_SUBMIT = 3
CANDIDATE_BLOCK = 4
ENDORSEMENT = 5
TX_CONFIRMATION = 6
PREFERENCES = 10
ENDORSEMENT_OLD_BLOCK = 11

PCC = 50
GOSSIP_SUBSCRIBE = 51
GOSSIP = 52
DELIVERED_GOSSIP = 53
ECHO_SUBSCRIBE = 54
ECHO = 55
DELIVERED_ECHO = 56
READY_SUBSCRIBE = 57
READY = 58
ACHIEVED_CONSENSUS = 59


def connect(host, port, pub_key, role):
    return pickle.dumps({
        'mtype': CONNECT,
        'data': {'host': host, 'port': port, 'pub_key': pub_key, 'role': role},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def disconnect(host, port):
    return pickle.dumps({
        'mtype': DISCONNECT,
        'data': {'host': host, 'port': port},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def transaction_submit_message(pub_key: str, tx: Transaction):
    return pickle.dumps({
        'mtype': TX_SUBMIT,
        'data': {'pub_key': pub_key, 'tx': tx},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def transaction_confirmation_message(pub_key: str, tx: Transaction):
    return pickle.dumps({
        'mtype': TX_CONFIRMATION,
        'data': {'pub_key': pub_key, 'tx': tx},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def candidate_block_message(pub_key: str, candidate_block):
    return pickle.dumps({
        'mtype': CANDIDATE_BLOCK,
        'data': {'pub_key': pub_key, 'candidate_block': candidate_block},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def endorse_block_message(pub_key: str, candidate_block, endorse, message):
    return pickle.dumps({
        'mtype': ENDORSEMENT,
        'data': {'pub_key': pub_key, 'candidate_block': candidate_block, 'endorse': endorse, 'message': message},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def enforce_old_block_message(pub_key: str, candidate_block, old_block):
    return pickle.dumps({
        'mtype': ENDORSEMENT_OLD_BLOCK,
        'data': {'pub_key': pub_key, 'candidate_block': candidate_block, 'enforce': old_block},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def preferences(pref):
    return pickle.dumps({
        'mtype': PREFERENCES,
        'data': pref,
    }, protocol=pickle.HIGHEST_PROTOCOL)


def gossip_subscribe_message(node, channel_id):
    return pickle.dumps({
        'mtype': GOSSIP_SUBSCRIBE,
        'data': {'pub_key': node.pub_key, 'node': node, 'channel_id': channel_id},
    }, protocol=pickle.HIGHEST_PROTOCOL)


def pcc_message(mtype, source, channel_id, data=None):
    return Map({
        'mtype': mtype,
        'source': source,
        'channel_id': channel_id,
        'data': data
    })
