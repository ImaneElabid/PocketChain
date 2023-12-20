import logging

from InputsConfig import Map
from InputsConfig import InputsConfig as Param

st_delivered = {}


class Statistics:

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
    def display():
        """Check how many nodes received the message"""
        for key in st_delivered:
            if st_delivered[key].count == Param.Total_nodes:
                # print(f'Consensus reached -> Channel: <{key[:4]}..>')
                logging.info(f"{st_delivered[key].count} / {Param.Total_nodes} nodes delivered.")
            else:
                print("Not all nodes have successfully delivered the message")
                logging.warning(
                    f"{st_delivered[key].count} / {Param.Total_nodes} nodes delivered message -> Channel: <{key[:4]}..>")
            print(f"{st_delivered}")
