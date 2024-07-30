import random
import time
import threading
import requests

from app.config import CONNECTED_NODE_ADDRESSES, FRONTEND_ADDRESS

def get_random_node_address():
    return random.choice(list(CONNECTED_NODE_ADDRESSES))

def get_frontend_address():
    return FRONTEND_ADDRESS

def update_node_addresses():
    while True:
        selected_node = get_random_node_address()
        if selected_node:
            response = requests.get(f"{selected_node}/peers")
            if response.status_code == 200:
                peers = response.json()['peers']
                if len(peers):
                    global CONNECTED_NODE_ADDRESSES
                    CONNECTED_NODE_ADDRESSES.update(peers)
        
        time.sleep(10)


update_node_addressesـthread = threading.Thread(target=update_node_addresses)
update_node_addressesـthread.start()