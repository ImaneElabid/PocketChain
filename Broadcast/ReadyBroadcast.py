from Config.InputsConfig import InputsConfig as Param


class ReadyBroadcast:
    def __init__(self, node, echo_layer, channel_id):
        self.node = node
        self.already_executed_flag = False
        self.ready_subscribe_sample = set()
        self.ready_delivered = False
        self.ready_sample = set()
        self.delivery_sample = set()

        self.ready = set()
        self.delivered = False
        self.ready_replies = {}
        self.delivery_replies = {}
        self.channel_id = channel_id

        self.echo_layer = echo_layer

    def init(self):
        self.echo_layer.init()
        self.ready_sample = self.node.sample_and_send("ReadySubscribe", Param.R, self.channel_id)
        self.ready_replies = {node_id: set() for node_id in self.ready_sample}

        self.delivery_sample = self.node.sample_and_send("ReadySubscribe", Param.D, self.channel_id)
        self.delivery_replies = {node_id: set() for node_id in self.delivery_sample}

    def broadcast(self, block):
        self.echo_layer.broadcast(block)

    def handle(self, event, message, source):
        if event == "delivered an echo":
            # print(f"{self.node} -> {event}: <{message}>  -> Channel: <{self.channel_id[:4]}..>")#
            self.ready.add(message)
            for node in self.ready_subscribe_sample:
                self.node.send(node, "Ready", message, self.node, self.channel_id)

        elif event == "ReadySubscribe":
            # print(f"{self.node} -> {event}: <{message}> == {self.channel_id}")#
            for message in self.ready:
                self.node.send(source, "Ready", message, self.node, self.channel_id)
            self.ready_subscribe_sample.add(source)

        elif event == "Ready":
            # print(f"{self.node} -> {event}: <{message}> == <{self.channel_id[:4]}..>")#
            if source in self.ready_sample:
                if message not in self.ready_replies[source]:
                    self.ready_replies[source].add(message)
                self.check_ready(message)
            if source in self.delivery_sample:
                # Add the reply only if it's not already present
                if message not in self.delivery_replies[source]:
                    # print(f"{self.node} -> {event}: <{message}> == <{self.channel_id[:4]}..> DELIVERY SET from {source}")  #
                    self.delivery_replies[source].add(message)
                self.check_delivery(message)
        elif event == "achieved consensus":
            # print(f"{self.node} -> {event}: <{message}> ")  #
            pass

    def check_ready(self, message):
        # if message not in self.ready:
        ready_count = sum(1 for reply in self.ready_replies.values() if message in reply)
        if ready_count >= Param.R_tilda and not self.delivered and not self.already_executed_flag:
            # print(f"{self.node} -> got enough ready.:")
            self.already_executed_flag = True
            self.ready.add(message)
            self.ready_delivered = True
            for target in self.ready_subscribe_sample:
                self.node.send(target, "Ready", message, self.node, self.channel_id)

    def check_delivery(self, message):
        # Check if enough Delivery confirmations have been received to consider the message "delivered"
        delivery_count = sum(1 for reply in self.delivery_replies.values() if message in reply)
        if delivery_count >= Param.D_tilda and not self.delivered:
            self.delivered = True
            self.node.receive("achieved consensus", message, source=self.node, hid=self.channel_id)

    def byz_handle(self, event, source, block1, block2):
        if event == "delivered an echo":
            ready_sample_list = list(self.ready_subscribe_sample)
            half = len(ready_sample_list) // 2
            first_half = ready_sample_list[:half]
            second_half = ready_sample_list[half:]

            for node in first_half:
                self.node.send(node, "Ready", block1, self.node, self.channel_id)

            for node in second_half:
                self.node.send(node, "Ready", block2, self.node, self.channel_id)

        elif event == "ReadySubscribe":
            for message in self.ready:
                self.node.send(source, "Ready", message, self.node, self.channel_id)
            self.ready_subscribe_sample.add(source)

        elif event == "Ready":
            # print(f"{self.node} -> {event}: <{message}> == {self.channel_id}")#
            if source in self.ready_sample:
                if block1 not in self.ready_replies[source]:
                    self.ready_replies[source].add(block1)
                if block2 not in self.ready_replies[source]:
                    self.ready_replies[source].add(block2)
                self.check_byz_ready(block1, block2)
            if source in self.delivery_sample:
                # Add the reply only if it's not already present
                if block1 not in self.delivery_replies[source]:
                    self.delivery_replies[source].add(block1)
                if block2 not in self.delivery_replies[source]:
                    self.delivery_replies[source].add(block2)
                self.node.receive("achieved consensus", block1, source=self.node, hid=self.channel_id)
                self.node.receive("achieved consensus", block2, source=self.node, hid=self.channel_id)

        elif event == "achieved consensus":
            print(f"{self.node} -> {event}: <{block1}> ")  #
            print(f"{self.node} -> {event}: <{block2}> ")  #

    def check_byz_ready(self, message1, message2):
        # if message not in self.ready:
        self.ready.add(message1)
        self.ready.add(message2)
        self.ready_delivered = True
        ready_sample_list = list(self.ready_subscribe_sample)
        half = len(ready_sample_list) // 2
        first_half = ready_sample_list[:half]
        second_half = ready_sample_list[half:]

        for node in first_half:
            self.node.send(node, "Ready", message1, self.node, self.channel_id)

        for node in second_half:
            self.node.send(node, "Ready", message2, self.node, self.channel_id)

    def __repr__(self):
        return f"RB({self.channel_id[:4]})"

    def __str__(self):
        return f"RB({self.channel_id[:4]})"
