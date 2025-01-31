from threading import Lock

import src.common.globals as GLOB
from src.blockchain.registry import Registry
from src.common.protocol import PCC, GOSSIP_SUBSCRIBE, GOSSIP, DELIVERED_GOSSIP, ECHO_SUBSCRIBE, ECHO, DELIVERED_ECHO, \
    READY_SUBSCRIBE, READY, ACHIEVED_CONSENSUS
from src.common.statistics import Statistics
from src.common.utils import log
from src.nodes.client import Client
from src.pcc.router import Router


class Processor(Client):
    def __init__(self, config, pub_key=None):
        super(Processor, self).__init__(config, pub_key)
        self.role = "Processor"
        self.reserved_storage = 0  # in GB
        self.local_blockchain = []
        self.router = Router(self)
        self.lock = Lock()

    def allocate_storage(self):
        self.reserved_storage = GLOB.MIN_STORAGE
        return True

    def verify_storage(self):
        return self.reserved_storage >= GLOB.MIN_STORAGE  # Storage requirement

    def discover_announcers(self):
        announcers = Registry.get_announcers()
        for announcer in announcers.values():
            if announcer.instance.verify_stake():
                self.connect(announcer.instance)
        # log('event', f"{self} subscribed to {len(self.registry)} announcers!")

    def pcc_send(self, target, msg):
        self.terminate = False
        target.pcc_receive(msg)

    def pcc_receive(self, msg):
        if msg.channel_id in Statistics.nbr_messages:
            Statistics.nbr_messages[msg.channel_id] += 1
        else:
            Statistics.nbr_messages[msg.channel_id] = 1
        if msg is not None:
            channel = self.get_or_create_channel(msg.channel_id)
            self.handle_pcc_request(channel, msg)
        else:
            log('error', f"{msg} is not a valid message")

    def handle_pcc_request(self, channel, msg):
        # log('info', f"{self} Got message type : {msg.mtype}")
        if msg.mtype in [PCC, GOSSIP_SUBSCRIBE, GOSSIP]:
            channel.gossip_layer.handle(msg)
        elif msg.mtype in [DELIVERED_GOSSIP, ECHO_SUBSCRIBE, ECHO]:
            channel.echo_layer.handle(msg)
        elif msg.mtype in [DELIVERED_ECHO, READY_SUBSCRIBE, READY]:
            channel.ready_layer.handle(msg)
        elif msg.mtype == ACHIEVED_CONSENSUS:
            self.consensus_achieved(channel, msg)
        else:
            log('error', f"{self}: Unknown type of message: {mtype}.")

    def consensus_achieved(self, channel, msg):
        channel.delivered = True
        self.local_blockchain.append(msg.data)
        log('info', f"{self} Delivered {msg.data} and append to local PC[{len(self.local_blockchain)}]")
        # ST.update_delivered(self.id, hid)
        # P.Shared_pool.remove_transaction(
        #     block.transactions)

    def get_or_create_channel(self, channel_id):
        if self.router.channel_exist(channel_id):
            return self.router.get_channel(channel_id)
        else:
            return self.router.add_channel(channel_id)
