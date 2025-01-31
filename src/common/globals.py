import math

PORT = 19000
LAUNCHER_PORT = 19491
TCP_SOCKET_BUFFER_SIZE = 5000000
TCP_SOCKET_SERVER_LISTEN = 10
SOCK_TIMEOUT = 60

IDLE_POWER = 12.60

MAX_MESSAGE_SIZE = 1024 * 1024 * 10  # 10MB max message size
MESSAGE_HEADER_SIZE = 8  # Size of length prefix

TOTAL_NODES = 300
G = math.ceil(TOTAL_NODES / 100)
G_TILDA = math.ceil(TOTAL_NODES / 100)
VERBOSE = 3
OLD_TYPE = 'info'
SEED = 0

NODE_ZERO_BALANCE = 1500  # initial balance of Imane: 1500 PCs
NODE_ZERO_TIPS = 50000  # initial tips of Imane: 50000T
BLOCK_SIZE = 50  # nbr of tx  >>>> The block size in MB
QSUB = 1 # Number of announcers to subscribe to
MIN_TIPS = 10  # 100T
BLOCK_SATISFACTORY_TIPS = BLOCK_SIZE * MIN_TIPS * 2
DEFAULT_BALANCE = 100
DEFAULT_TIPS = MIN_TIPS * DEFAULT_BALANCE * 200
MIN_ENDORSE = QSUB
MIN_TX_CONFIRMATIONS = QSUB
STAKE_AMOUNT = 100  # 100PC
STAKE_EXPIRY = 10  # number of blocks proposed for BRB # 3600 * 24  # in seconds
MIN_STORAGE = 1  # 1GB
MAX_BLOCK_SIZE = 1  # 1MB
TX_SIZE = 0.000546  # The average transaction size  in MB
# Block state
BLOCK_INIT = 60
BLOCK_CONFIRMED = 61
BLOCK_REJECTED = 62
BLOCK_EXPIRED = 63
BLOCK_FINAL = 64

ROLES = ['Announcer', 'Processor', 'Client']
