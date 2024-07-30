import json
from flask import request

from app import app
from core import peers, blockchain_mutex
from core import set_get_blockchain_instance
from core.block import Block
from core.transaction import Transaction
from core.utxo import UTXOPool
from core.crypto import CryptoTools
from core.consensus import announce_new_transaction


@app.route('/chain', methods=['GET'])
def get_serializable_chain():
    blockchain_dict = set_get_blockchain_instance().to_json()

    return json.dumps({"length": len(blockchain_dict['chain']),
                       "chain": blockchain_dict['chain'],
                       "peers": list(peers),
                       "unconfirmed_transactions": blockchain_dict['unconfirmed_transactions']})


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["input_public_key", "output_public_key", "amount", "signature"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404
        
    transaction = Transaction.from_json(tx_data)

    with blockchain_mutex:
        if not set_get_blockchain_instance().add_new_transaction_to_mempool(transaction):
            return "Failed", 400
    
    announce_new_transaction(tx_data)

    return "Success", 201


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    new_node_address = request.get_json()["new_node_address"]
    if not new_node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(new_node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_serializable_chain()


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    
    block = Block(block_data["index"],
                  Transaction.list_from_json(block_data["transactions"], calculate_fee=False),
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  UTXOPool.from_json(block_data["utxo_pool"]),
                  block_data["coinbase_beneficiary"],
                  block_data["nonce"])

    proof = block_data['hash']

    with blockchain_mutex:
        if set_get_blockchain_instance().add_block(block, proof):
            set_get_blockchain_instance().remove_transactions_from_mempool(block.transactions)
        else:
            return "The block was discarded by the node: ", 400

    return "Block added to the chain", 201

# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(set_get_blockchain_instance().to_json_unconfirmed_transactions())

@app.route('/peers')
def get_peers():
    return {"peers": list(peers)}


@app.route('/generate_wallet', methods=['GET'])
def generate_wallet():
    return CryptoTools.generate_pair()

@app.route('/sign_transaction', methods=['POST'])
def sign_transaction():
    data = request.get_json()
    required_fields = ["from", "to", "amount", "private_key"]

    for field in required_fields:
        if not data.get(field):
            return "Invalid transaction data", 404
        
    pre_tx = {
        "input_public_key": data["from"],
        "output_public_key": data["to"],
        "amount": float(data["amount"])
    }

    transaction = Transaction.from_json(pre_tx)
    signature = CryptoTools.sign(transaction.hash, data['private_key'])
    return signature