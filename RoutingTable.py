class RoutingTable:
    def __init__(self):
        self.table = {}

    def add_instance(self, h_id, instance):
        """Add a new instance to the routing table."""
        self.table[h_id] = instance

    def remove_instance(self, h_id):
        """Remove an instance from the routing table."""
        if h_id in self.table:
            del self.table[h_id]

    def get_instance(self, h_id):
        """Retrieve an instance from the routing table."""
        return self.table.get(h_id)

    def handle_message(self, h_id, event, message, source):
        """Route the message to the correct instance based on h_id."""
        if h_id in self.table:
            instance = self.table[h_id]
            instance.handle(event, message, source)

    def create_channel(self, h_id):
        pass

    def __repr__(self):
        return f"({self.table})"

    def __str__(self):
        return f"({self.table})"