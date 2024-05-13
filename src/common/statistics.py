import logging


from src.common.utils import log

st_delivered = {}


class Statistics:
    created_blocks = 0
    confirmed_blocks = 0
    unstable_blocks = 0
    stable_blocks = 0
    nbr_messages = {}

    @staticmethod
    def init_delivered(broadcast_id):  # {broadcast_id: {count,[nodes]}}
        delivered = Map({'count': 0, 'nodes': []})
        st_delivered[broadcast_id] = delivered

    @staticmethod
    def update_delivered(node_id, broadcast_id):
        # Check if node_id is already in the list
        if node_id not in st_delivered[broadcast_id].nodes:
            st_delivered[broadcast_id].count += 1
            st_delivered[broadcast_id].nodes.append(node_id)

    @staticmethod
    def display_delivery_rate():
        """Check how many nodes received the message"""
        for key in st_delivered:
            if st_delivered[key].count == P.Total_nodes:
                # print(f'Consensus reached -> Channel: <{key[:4]}..>')
                logging.info(f"{st_delivered[key].count} / {P.Total_nodes} nodes delivered.")
            else:
                print("Not all nodes have successfully delivered the message")
                logging.warning(
                    f"{st_delivered[key].count} / {P.Total_nodes} nodes delivered message -> Channel: <{key[:4]}..>")
            # print(f"{st_delivered}")

    @staticmethod
    def display_bc_statistics():
        logging.info(f"The blockchain contains: {Statistics.created_blocks} blocks")

    @staticmethod
    def display_PC_stats(detailed=False):
        log('success', f"The blockchain contains: {Statistics.created_blocks} blocks")
        log('info', f"Exchanges PCC messages per channel:")
        for c in Statistics.nbr_messages:
            log('', f">> Channel <{c}>: {Statistics.nbr_messages[c]} messages.")
