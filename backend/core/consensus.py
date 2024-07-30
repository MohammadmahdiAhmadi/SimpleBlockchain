import requests
import time
import json

from core import set_get_blockchain_instance, blockchain_mutex, peers
from node_config import get_node_address


def consensus_new_block():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    longest_chain = None
    current_len = len(set_get_blockchain_instance().chain)

    for node in peers:
        response = requests.get('{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and set_get_blockchain_instance().check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        with blockchain_mutex:
            set_get_blockchain_instance(longest_chain)
        return True

    return False

def consensus_new_peers():
    global peers
    duplicate_peers_counter = 0
    while True:
        peers.discard(get_node_address())
        duplicate_peers_counter += 1
        for node in list(peers):
            try:
                response = requests.get(f"{node}/peers", timeout=5)
                if response.status_code == 200:
                    received_peers = set(response.json().get('peers', []))
                    received_peers.discard(get_node_address())
                    if not received_peers.issubset(peers):
                        peers.update(received_peers)
                        duplicate_peers_counter = 0
                        print(peers)
            except requests.RequestException as e:
                peers.discard(node)

        print(duplicate_peers_counter)
        time.sleep(2 if duplicate_peers_counter < 2 else 20)

def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """

    block_dict = block.to_json()

    for peer in peers:
        url = "{}/add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      json=block_dict,
                      headers=headers)

def announce_new_transaction(tx_data):
    copy_peers = peers.copy()

    if not tx_data.get('announced_node_addresses'):
        tx_data['announced_node_addresses'] = [get_node_address()]
        
    else:
        tx_data['announced_node_addresses'] = tx_data['announced_node_addresses'] + [get_node_address()]

    copy_peers.difference_update(tx_data['announced_node_addresses'])

    for peer in copy_peers:
        url = "{}/new_transaction".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(tx_data),
                      headers=headers)
