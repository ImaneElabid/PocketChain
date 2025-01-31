import logging
from collections import defaultdict

import src.common.globals as GLOB
from src.common.helpers import Map, timeit
from src.common.utils import log, transmission_energy

st_delivered = {}


class Statistics:
    exchanged_bytes = 0
    stop_now = False
    nbr_clients = 0
    nbr_processors = 0
    nbr_announcers = 0
    nbr_byzantines = 0
    created_blocks = 0
    pccp_blocks = 0
    channels = {}
    confirmed_blocks = 0
    unstable_blocks = 0
    stable_blocks = 0
    nbr_messages = {}
    endorsements_messages = {}
    endorsement_rate = {}

    @staticmethod
    def init_delivered(channel_id):  # {broadcast_id: {count,[nodes]}}
        delivered = Map({'count': 0, 'nodes': []})
        st_delivered[channel_id] = delivered

    @staticmethod
    def update_delivered(node_id, channel_id):
        # Check if node_id is already in the list
        if node_id not in st_delivered[channel_id].nodes:
            st_delivered[channel_id].count += 1
            st_delivered[channel_id].nodes.append(node_id)

    @staticmethod
    @timeit
    def display_delivery_rate():
        """Check how many nodes received the message"""
        num_nodes = Statistics.nbr_processors + Statistics.nbr_announcers
        for key in st_delivered:
            if st_delivered[key].count == num_nodes:
                log('result', f"{st_delivered[key].count} / {num_nodes} nodes delivered.")
            else:
                log('warning', f"Not all nodes have successfully delivered the message")
                log('',f"{st_delivered[key].count} / {num_nodes} nodes delivered message -> Channel: <{key[:4]}..>")
        total_time = 0
        for c, ch in Statistics.channels.items():
            log('success', f"Max Delivery time for Channel({c}) is: {ch['end'] - ch['start']} seconds")
            total_time += ch['end'] - ch['start']
        log('result', f"Total time: {total_time} seconds")
        log('result', f"Average time per channel: {total_time / len(Statistics.channels)} seconds | {len(Statistics.channels)}")

    @staticmethod
    @timeit
    def display_bc_statistics():
        logging.info(f"The blockchain contains: {Statistics.created_blocks} blocks")

    @staticmethod
    @timeit
    def display_endorsement_stats(config, details=True):
        log('result', f"Created blocks: {Statistics.created_blocks} blocks")
        log('result', f"The blockchain contains: {Statistics.pccp_blocks} blocks")
        log('result', f"Exchanges PCCP messages per channel:")
        valid = []
        invalid = []
        for cblock in Statistics.endorsements_messages:
            n = Statistics.endorsements_messages[cblock]
            if sum(n) >= config.endorse_threshold:
                valid.append(sum(n))
            else:
                invalid.append(sum(n))
            if details:
                log('info',
                f">> Block#{cblock}: got {sum(n)} endorsements out of {len(n)} endorsement messages. {'[Validated]' if sum(n) >= config.endorse_threshold else ''}")
        log('success', f"#Candidate blocks[Valid] = {len(valid)} | #Candidate blocks[Invalid] = {len(invalid)}")
        total_valid = len(valid) if len(valid) > 0 else 1
        total_invalid = len(invalid) if len(invalid) > 0 else 1
        log('success', f">> Valid = {sum(valid)/total_valid} | invalid = {sum(invalid)/total_invalid}")

    @staticmethod
    @timeit
    def display_endorsement_rate():
        log('result', f"Candidate block validation rate:")
        announcers = Statistics.nbr_announcers
        # Communication overhead
        overhead = 0.001 * announcers
        log('', f"Number of announcers: {announcers}")
        total_time = []
        validation_timeline = defaultdict(int)
        for b, info in Statistics.endorsement_rate.items():
            if info['endorsed']:
                tt = (overhead + info['end'] - info['start']) / announcers
                log('success', f"Candidate Block#{b} validated in {tt} seconds")
                total_time.append(tt)
                end_time = int((overhead + info['end']) / announcers)
                validation_timeline[end_time] += 1

        min_second = min(validation_timeline.keys())
        max_second = max(validation_timeline.keys())
        accumulated_blocks = 0
        validated_per_second = []
        for sec in range(min_second, max_second+1):
            accumulated_blocks += validation_timeline[sec]
            validated_per_second.append((sec - min_second +1, accumulated_blocks))
        log('warning', f"{announcers} Announcers created {len(total_time)} candidate blocks in {sum(total_time)} seconds")
        log('', f"Validation timeline (blocks per second): {validated_per_second}")

    @staticmethod
    @timeit
    def display_bloc_stats():
        log('result', f"Created blocks: {Statistics.created_blocks} blocks")
        log('result', f"The blockchain contains: {Statistics.pccp_blocks} blocks")
        log('result', f"Exchanges PCCP messages per channel:")
        avg_msg_channel = []
        nbr_nodes = Statistics.nbr_processors + Statistics.nbr_announcers + Statistics.nbr_byzantines
        for c in Statistics.nbr_messages:
            log('', f">> Channel <{c}>: {Statistics.nbr_messages[c]} messages.")
            avg_msg_channel.append(Statistics.nbr_messages[c] / nbr_nodes)
        avg_msg = sum(avg_msg_channel) / len(avg_msg_channel)
        log('result', f"Average Exchanges PCCP messages per channel per node: {round(avg_msg, 2)}")

    @staticmethod
    @timeit
    def display_energy():
        log('result', f"display_delivery_rate()")
        num_nodes = Statistics.nbr_processors + Statistics.nbr_announcers
        energy = transmission_energy(Statistics.exchanged_bytes, num_nodes)
        print("-------")
        energy = transmission_energy(Statistics.exchanged_bytes, 0)




