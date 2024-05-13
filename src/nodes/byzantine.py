from src.nodes.node import Node


class Byzantine(Node):
    def __init__(self, config, pub_key=None, e=0):
        super(Byzantine, self).__init__(config, pub_key)
        self.node_type = "Byzantine"
        self.e = e
