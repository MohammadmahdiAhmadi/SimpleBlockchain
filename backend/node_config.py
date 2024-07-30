import os

SEED_NODE = os.environ.get('SEED_NODE', 'http://127.0.0.1:8000') # Seed node that help new nodes to register
NODE_IP = os.environ.get('NODE_IP', '127.0.0.1') # Current node ip
NODE_PORT = os.environ.get('NODE_PORT', 8000) # Current node port
NODE_ADDRESS = f'http://{NODE_IP}:{NODE_PORT}' # Current node address
chain_file_name = os.environ.get('DATA_FILE', './data/chain_bkp.json') # File path to store backup of seed node

def is_seed_node():
    return True if NODE_ADDRESS == SEED_NODE else False

def get_node_address():
    global NODE_ADDRESS

    return NODE_ADDRESS
