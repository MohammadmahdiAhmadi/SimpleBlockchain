import threading

# the node's copy of blockchain
blockchain_instance = None

blockchain_mutex = threading.Lock()

# the address to other participating members of the network
peers = set()

def set_get_blockchain_instance(blockchain=None):
    global blockchain_instance
    
    if blockchain:
        blockchain_instance = blockchain

    return blockchain_instance