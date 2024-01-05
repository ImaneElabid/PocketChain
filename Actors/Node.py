import copy
import logging
import time

from Blocks.Block import Block
from Config.InputsConfig import InputsConfig as P
from Statistics import Statistics as ST
from Blocks.RoutingTable import RoutingTable
from Blocks.Transaction import Transaction as TX, TransactionPool


class Node:

    def __init__(self, node_id, byzantine=False, has_tx=True):
        self.id = node_id
        self.byzantine = byzantine
        self.local_blockchain = []
        self.local_blockchain.append(Block())
        self.routing_table = RoutingTable(self)
        self.has_tx = has_tx

    ##########################################################################

    # def create_and_broadcast(self, sender):
    #     if self.has_tx:
    #         Param.Shared_pool.add_transaction(TX.create_transaction())
    #     if self == sender:
    #         if Param.Shared_pool:  # Check if the pool is not empty
    #             block_to_broadcast = Block()
    #             hid = Param.hid(block_to_broadcast.id)
    #             channel = self.routing_table.add_channel(hid)
    #             ST.init_delivered(
    #                 hid)  # add broadcast channel with id=hid to the stats to keep track on delivery threshold
    #             time.sleep(0.01)
    #             channel.ready_layer.broadcast(block_to_broadcast)
    def create_and_broadcast_multiple(self, sender, num_blocks):
         # Generate the Genesis block and append it to the local blockchain for all nodes
        if self.has_tx:
            P.Shared_pool.add_transaction(TX().create_transaction())

        if self == sender:
            for _ in range(num_blocks):
                if P.Shared_pool.has_enough_transactions():  # Check if the pool is not empty
                    # Create a block from transactions in the pool
                    block_to_broadcast = Block()  # miner=self
                    block_to_broadcast.generate_block(self)

                    # Generate a unique identifier for the broadcast
                    hid = P.hid(block_to_broadcast.id)

                    # Add the broadcast channel to the routing table
                    channel = self.routing_table.add_channel(hid)

                    # Initialize statistics tracking for the broadcast
                    ST.init_delivered(hid)
                    # Delay to ensure channel setup is complete
                    time.sleep(0.01)

                    # Broadcast the block
                    channel.ready_layer.broadcast(block_to_broadcast)
                else:
                    logging.warning(f'Not enough transactions to broadcast in the Pool')
                # Optional delay between broadcasting each block
                time.sleep(P.BlockInterval)

    def send(self, target, event, block, source=None, hid=None):
        target.receive(event, block, source=source, hid=hid)

    def receive(self, event, block, source=None, hid=None):
        # Retrieve the broadcast layers for this h_id
        if self.routing_table.channel_exist(hid):
            channel = self.routing_table.get_channel(hid)
        else:
            channel = self.routing_table.add_channel(hid)
        self.handle_request(channel, event, block, source, hid)

    def byzantine_attack(self, channel, event, block, source=None, hid=None):
        if self.byzantine:
            if isinstance(block, tuple):
                print(f'===> : {block}')
                block, conflicting_block = block
            else:
                conflicting_block = None
            if event in ['Broadcast', 'GossipSubscribe', 'Gossip']:
                channel.gossip_layer.byz_handle(event, source, block, conflicting_block)
            elif event in ['delivered a gossip', 'EchoSubscribe', 'Echo']:
                channel.echo_layer.byz_handle(event, source, block, conflicting_block)
            elif event in ['delivered an echo', 'ReadySubscribe', 'Ready']:
                channel.ready_layer.byz_handle(event, source, block, conflicting_block)
            elif event == 'achieved consensus':
                channel.delivered = True
                ST.update_delivered(self.id, hid)
        return self.byzantine

    def handle_request(self, channel, event, block,  source=None, hid=None):
        if not self.byzantine_attack(channel, event, block,  source, hid):
            if event in ['Broadcast', 'GossipSubscribe', 'Gossip']:
                channel.gossip_layer.handle(event, block,  source)
            elif event in ['delivered a gossip', 'EchoSubscribe', 'Echo']:
                channel.echo_layer.handle(event, block, source)
            elif event in ['delivered an echo', 'ReadySubscribe', 'Ready']:
                channel.ready_layer.handle(event, block, source)
            elif event == 'achieved consensus':
                channel.delivered = True
                self.local_blockchain.append(block)
                # print((self.local_blockchain))
                ST.update_delivered(self.id, hid)
                P.Shared_pool.remove_transaction(
                    block.transactions)  # TODO Remove the broadcast transaction but only when delivered only by the miner
                # self.routing_table.remove_channel(hid)    # TODO Remove the broadcast channel but only when delivered

    def sample_and_send(self, message, size, hid):
        sampled_nodes = P.omega(P.all_nodes, size)
        for node in sampled_nodes:
            self.send(node, message, None, self, hid)
        return sampled_nodes

        # Special methods

    def last_block(self):
        # if len(self.local_blockchain) == 1:
        return self.local_blockchain[len(self.local_blockchain) - 1]

    def blockchain_length(self):
        return len(self.local_blockchain)

    def __repr__(self):
        return f"Node({self.id})"

    def __str__(self):
        return f"Node({self.id})"
