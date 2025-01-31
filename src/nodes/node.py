import pickle
import socket
import struct
import sys
import traceback
from threading import Thread

import src.common.globals as GLOB
from src.common import protocol
from src.common.crypto import generate_key_pair, sign_text
from src.common.globals import PORT
from src.common.helpers import Map
from src.common.statistics import Statistics
from src.common.utils import create_tcp_socket, get_ip_address, log, prexit


class Node(Thread):
    port = PORT - 1

    def __init__(self, config, pub_key=None):
        super(Node, self).__init__()

        # Node wallet
        self.role = "Node"
        if pub_key is None:
            # initialize node
            key_pair = generate_key_pair()
            self.pub_key = key_pair.pub_key
            self.prv_key = key_pair.prv_key
            self.balance = GLOB.DEFAULT_BALANCE
            self.tips = GLOB.DEFAULT_TIPS
        else:
            # load node
            restored = self.load_node(pub_key)
            self.pub_key = pub_key
            self.prv_key = restored.prv_key
            self.balance = restored.balance
            self.tips = restored.tips
        # Network settings
        self.config = config
        self.announcer_registry = Map()
        self.local_chain = []  # Final blocks of PocketChain
        self.block_store = []  # List of unstable blocks
        # Software settings
        self.registry = []
        self.mp = self.config.mp  # flag [True: message passing | False: shared memory]
        self.host = get_ip_address()
        Node.port += 1
        self.port = Node.port
        self.terminate = False
        self._init_server()

    def run(self):
        if self.mp:
            while not self.terminate:
                try:
                    # log('log', f"{self} is online and waiting for connection...")
                    conn, address = self.sock.accept()
                    if not self.terminate:
                        node_conn = NodeConn(self, conn, address[0], address[1])
                        node_conn.start()
                        self.registry.append(node_conn)
                except socket.timeout:
                    self.terminate = True
                except Exception as e:
                    log('error', f"{self} Error :: {e}")
                    traceback.print_exc()
            # terminate socket connections
            for node in self.registry:
                node.stop()
            self.sock.close()
            log('log', f"{self} terminated.")
        else:
            # log('log', f"{self} is online!")
            pass

    def load_node(self, pub_key):
        self.announcer_registry = Map()
        self.block_store = Map()
        return Map({'prv_key': None, 'balance': 0, 'tips': 0})

    def send(self, message, recipient, sign=False):
        if sign:
            # Sign the message using the private key before sending
            signature = sign_text(message, self.prv_key)
            message = {'message': message, 'signature': signature}

        if self.config.mp:
            self.send_via_sockets(message, recipient)
        else:
            self.send_via_shared_memory(message, recipient)

    def receive(self, message):
        # Process received message
        pass

    def connect(self, node):
        # Establish connection to a node
        try:
            if node.port in [r.port for r in self.registry]:
                # log('log', f"{self}, node {node} already connected.")
                return True
            if self.mp:
                sock = create_tcp_socket()
                sock.settimeout(GLOB.SOCK_TIMEOUT)
                sock.connect((node.host, node.port))
                conn = NodeConn(self, sock, node.host, node.port, node.pub_key, node.role)
                conn.start()
                conn.send(protocol.connect(self.host, self.port, self.pub_key, self.role))
                self.registry.append(conn)
            else:
                slink = NodeLink(self, node, None)
                dlink = NodeLink(node, self, slink)
                slink.link = dlink
                self.registry.append(slink)
            return True
        except Exception as e:
            log('error', f"{self}: Can't connect to {node} -- {e}")
            traceback.print_exc()

            return False

    def disconnect(self, peer):
        # Disconnect from a peer
        pass

    def broadcast(self, message):
        # Send a message to all peers
        pass

    def multicast(self, message, recipients):
        # Send a message to a subset of peers
        pass

    def gossip(self, message):
        # Gossip protocol implementation
        pass

    def send_via_sockets(self, message, recipient):
        # Code to send message using sockets
        pass

    def send_via_shared_memory(self, message, recipient):
        # Code to send message using shared memory
        pass

    def stop(self):
        self.terminate = True
        for node in self.registry:
            self.send(protocol.disconnect(self.host, self.port), node)

    def __repr__(self):
        return f"{self.role}({self.port})"

    def __str__(self):
        return f"{self.role}({self.port})"

    #  Private methods --------------------------------------------------------
    def _init_server(self):
        if self.mp:
            self.sock = create_tcp_socket()
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(GLOB.SOCK_TIMEOUT)
            self.sock.listen(GLOB.TCP_SOCKET_SERVER_LISTEN)
            self.port = self.sock.getsockname()[1]
        else:
            self.sock = None


class NodeConn(Thread):
    def __init__(self, node, sock, host="", port=0, pub_key=None, role="Node"):
        super(NodeConn, self).__init__()
        self.node = node
        self.pub_key = pub_key
        self.role = role
        self.host = host
        self.port = port
        self.sock = sock
        self.terminate = False

    def run(self):
        while not self.terminate:
            try:
                # Read message length
                length_data = self.sock.recv(8)
                if not length_data or len(length_data) != 8:
                    self.terminate = True
                    continue

                (length,) = struct.unpack('>Q', length_data)

                # Validate length
                if length <= 0 or length > GLOB.MAX_MESSAGE_SIZE:  # Add MAX_MESSAGE_SIZE to globals
                    raise ValueError(f"Invalid message length: {length}")

                # Read message data
                buffer = b''
                while len(buffer) < length:
                    to_read = length - len(buffer)
                    chunk = self.sock.recv(4096 if to_read > 4096 else to_read)
                    if not chunk:
                        raise ConnectionError("Connection broken")
                    buffer += chunk

                # Validate buffer before unpickling
                if len(buffer) == length and buffer:
                    try:
                        data = pickle.loads(buffer)
                        if isinstance(data, dict) and 'mtype' in data:
                            self.handle_request(data)
                        else:
                            log('error', f"{self.node}: Invalid message format")
                    except pickle.UnpicklingError as e:
                        log('error', f"{self.node}: Corrupted message: {e}")
                        traceback.print_exc()

            except socket.timeout:
                pass
            except struct.error as e:
                self.terminate = True
                log('error', f"{self.node}: Malformed message header: {e}")
            except Exception as e:
                self.terminate = True
                log('error', f"{self.node} NodeConn <{self.port}> Exception: {e}")
                traceback.print_exc()

    def run2(self):
        # Wait for messages from device
        while not self.terminate:
            try:
                (length,) = struct.unpack('>Q', self.sock.recv(8))
                buffer = b''
                while len(buffer) < length:
                    to_read = length - len(buffer)
                    buffer += self.sock.recv(4096 if to_read > 4096 else to_read)
                if buffer:
                    data = pickle.loads(buffer)
                    del buffer
                    self.handle_request(data)

            except pickle.UnpicklingError as e:
                log('error', f"{self.node}: Corrupted message : {e}")
                traceback.print_exc()
            except socket.timeout:
                pass
            except struct.error as e:
                # log('error', f"{self.node}: struct.error: {e}")
                self.terminate = True
                pass
            except Exception as e:
                self.terminate = True
                log('error', f"{self.node} NodeConn <{self.port}> Exception: {e}")
                traceback.print_exc()
                prexit("DDD")
        self.sock.close()
        log('log', f"{self.node}: neighbor {self.port} disconnected")

    def handle_request(self, data):
        Statistics.exchanged_bytes += sys.getsizeof(data) * 8  # size in bits
        if data and data['mtype'] == protocol.CONNECT:
            self.handle_connect(data['data'])
        elif data and data['mtype'] == protocol.TX_SUBMIT:
            self.node.handle_receive_transaction(data['data'])
        elif data and data['mtype'] == protocol.CANDIDATE_BLOCK:
            self.node.handle_candidate_block(data['data'], self)
        elif data and data['mtype'] == protocol.ENDORSEMENT:
            self.node.handle_endorsements(data['data'], self)
        elif data and data['mtype'] == protocol.TX_CONFIRMATION:
            log('info', f"{self} protocol.TX_CONFIRMATION")
            self.node.handle_receive_transaction_confirmation(data['data'])
        elif data and data['mtype'] == protocol.DISCONNECT:
            self.handle_disconnect(data['data'])
        else:
            log('error', f"{self.node.name}: Unknown type of message: {data['mtype']}.")

    def send2(self, msg):
        try:
            if self.terminate:
                log('log', f"{self} tries to send on terminated")
            length = struct.pack('>Q', len(msg))
            self.sock.sendall(length)
            self.sock.sendall(msg)
        except socket.error as e:
            self.terminate = True
            # log('error', f"{self}: Socket error: {e}: ")
            # traceback.print_exc()
        except Exception as e:
            log('error', f"{self}: Exception\n{e}")
            traceback.print_exc()

    def send(self, msg):
        try:
            if self.terminate:
                log('log', f"{self} tries to send on terminated")
                return

            # Validate message before sending
            if not msg:
                log('error', f"{self}: Attempted to send empty message")
                return

            # Ensure message is properly pickled
            if not isinstance(msg, bytes):
                msg = pickle.dumps(msg)

            # Add message length header
            length = struct.pack('>Q', len(msg))

            # Send as a single packet to avoid fragmentation
            self.sock.sendall(length + msg)

        except socket.error as e:
            self.terminate = True
            log('error', f"{self}: Socket error: {e}")
        except Exception as e:
            log('error', f"{self}: Exception while sending: {e}")
            traceback.print_exc()

    def stop(self):
        self.terminate = True
        self.send(protocol.disconnect(self.host, self.port))

    def handle_connect(self, data):
        self.host = data['host']
        self.port = int(data['port'])
        self.pub_key = data['pub_key']
        self.role = data['role']

    def handle_disconnect(self, data):
        del data
        self.terminate = True
        if self in self.node.registry:
            self.node.registry.remove(self)

    #  Private methods --------------------------------------------------------

    def __repr__(self):
        return f"{self.node.role}Conn({self.node.port}, {self.port})"

    def __str__(self):
        return f"{self.node.role}Conn({self.node.port}, {self.port})"


class NodeLink:
    def __init__(self, node, conn, link=None):
        self.node = node
        self.conn = conn
        self.link = link
        # kept for compatibility with NodeConnection
        self.host = conn.host
        self.port = conn.port
        self.role = conn.role
        self.pub_key = conn.pub_key
        self.terminate = False

    def send(self, msg):
        if msg:
            data = pickle.loads(msg)
            if data and data['mtype'] == protocol.CONNECT:
                self.link.handle_connect(data['data'])
            elif data and data['mtype'] == protocol.TX_SUBMIT:
                self.conn.handle_receive_transaction(data['data'])
            elif data and data['mtype'] == protocol.CANDIDATE_BLOCK:
                self.conn.handle_candidate_block(data['data'], self)
            elif data and data['mtype'] == protocol.ENDORSEMENT:
                self.conn.handle_endorsements(data['data'], self)
            elif data and data['mtype'] == protocol.TX_CONFIRMATION:
                self.conn.handle_receive_transaction_confirmation(data['data'])
            elif data and data['mtype'] == protocol.DISCONNECT:
                self.link.handle_disconnect(data['data'])
            else:
                log('error', f"{self.node.name}: Unknown type of message: {data['mtype']}.")
        else:
            log('error', f"{self.node.name}: Corrupted message.")

    def handle_transaction(self, data):
        log('warning', f"{self.node} :: NodeLink {data['tx']}")

    def handle_connect(self, data):
        pass

    def handle_disconnect(self, data):
        self.terminate = True
        if self in self.node.registry:
            self.node.registry.remove(self)

    def stop(self):
        self.terminate = True

    #  Private methods --------------------------------------------------------

    def __repr__(self):
        return f"NodeLink({self.node.port}, {self.conn.port})"

    def __str__(self):
        return f"NodeLink({self.node.port}, {self.conn.port})"
