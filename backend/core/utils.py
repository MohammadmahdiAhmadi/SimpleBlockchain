import requests
import sys
import json
import time
import signal
import atexit

from core import set_get_blockchain_instance
from core.blockchain import Blockchain
from core.block import Block
from core.transaction import Transaction
from core.utxo import UTXOPool
from core.consensus import consensus_new_block, announce_new_block
from core import peers
from core.config import SUBSIDY_HALVING_INTERVAL, ROUND_AMOUNT
from node_config import NODE_ADDRESS, SEED_NODE, chain_file_name, is_seed_node, get_node_address


def mining_loop():

    while True:
        is_consensus = False
        result = set_get_blockchain_instance().mine()
        if result:
            print(f'Mine Process. len blockchain: {len(set_get_blockchain_instance().chain)}')
            # Making sure we have the longest chain before announcing to the network
            chain_length = len(set_get_blockchain_instance().chain)
            consensus_new_block()
            is_consensus = True
            if chain_length == len(set_get_blockchain_instance().chain):
                # announce the recently mined block to the network
                announce_new_block(set_get_blockchain_instance().last_block)
        
        if not is_consensus:
            consensus_new_block()
            is_consensus = True

        time.sleep(2)


def create_chain_from_dump(chain_dump, skip_genesis_block=False):
    generated_blockchain = Blockchain(create_genesis_block=False)
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      Transaction.list_from_json(block_data["transactions"], calculate_fee=False),
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      UTXOPool.from_json(block_data["utxo_pool"]),
                      block_data["coinbase_beneficiary"],
                      block_data["nonce"],)

        # Why Skip genesis block?!
        if idx == 0:
            if skip_genesis_block:
                continue  # skip genesis block
            else:
                generated_blockchain.set_genesis_block(block)
                continue
        proof = block_data['hash']
        generated_blockchain.add_block(block, proof)
    return generated_blockchain


def register_with_seed_node() -> bool:
    global NODE_ADDRESS
    global SEED_NODE

    data = {"new_node_address": get_node_address()}
    headers = {'Content-Type': "application/json"}
    url = "{}/register_node".format(SEED_NODE)
    response = requests.post(url,
                             data=json.dumps(data), headers=headers)
    
    if response.status_code == 200:
        global peers

        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        set_get_blockchain_instance(blockchain) 

        peers.update({SEED_NODE})

        existing_node_peers = response.json().get('peers', [])
        if NODE_ADDRESS in existing_node_peers:
            existing_node_peers.remove(NODE_ADDRESS)
        peers.update(existing_node_peers)

        print("register node successfuly")
        return True
    else:
        return False

def get_chain():
    blockchain_dict = set_get_blockchain_instance().to_json()

    return {"length": len(blockchain_dict['chain']),
                       "chain": blockchain_dict['chain'],
                       "peers": list(peers),
                       "unconfirmed_transactions": blockchain_dict['unconfirmed_transactions']}

def save_chain():
    if chain_file_name is not None:
        with open(chain_file_name, 'w') as chain_file:
            chain_file.write(json.dumps(get_chain(), indent=4))

def exit_from_signal(signum, stack_frame):
    sys.exit(0)

def store_seed_node():
    if not is_seed_node():
        return False
    
    atexit.register(save_chain)
    signal.signal(signal.SIGTERM, exit_from_signal)
    signal.signal(signal.SIGINT, exit_from_signal)

    data = None
    try:
        with open(chain_file_name, 'r') as chain_file:
            raw_data = chain_file.read()
            if raw_data is None or len(raw_data) == 0:
                data = None
            else:
                data = json.loads(raw_data)
    except FileNotFoundError:
        print(f"Error: The file '{chain_file_name}' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    if data is None:
        # the node's copy of blockchain
        blockchain = Blockchain()
        set_get_blockchain_instance(blockchain)
        save_chain()
    else:
        blockchain = create_chain_from_dump(data['chain'])
        set_get_blockchain_instance(blockchain)
        peers.update(data['peers'])

    return True
