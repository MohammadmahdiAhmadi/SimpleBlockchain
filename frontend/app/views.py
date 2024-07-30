from flask import render_template, request

from app.nodes_connection import get_random_node_address, get_frontend_address
from app.config import CONNECTED_NODE_ADDRESSES
from app import app


@app.route('/')
def index():
    node_address = request.args.get('node_address')
    if node_address not in list(CONNECTED_NODE_ADDRESSES):
        node_address = None

    return render_template('index.html',
                           title='Blockchain Interface',
                           frontend_address=get_frontend_address(),
                           node_address=node_address if node_address else get_random_node_address(),
                           node_addresses=list(CONNECTED_NODE_ADDRESSES))

@app.route('/block')
def block_detail():
    index = request.args.get('index')
    if not index:
        return "Block index not provided", 400

    node_address = request.args.get('node_address')
    if node_address not in list(CONNECTED_NODE_ADDRESSES):
        node_address = None

    return render_template('block.html',
                           title=f'Block {index} Detail',
                           index=index,
                           frontend_address=get_frontend_address(),
                           node_address=node_address if node_address else get_random_node_address())

@app.route('/mempool')
def mempool_detail():
    node_address = request.args.get('node_address')
    if node_address not in list(CONNECTED_NODE_ADDRESSES):
        node_address = None

    return render_template('mempool.html',
                           title='Mempool (Unconfirmed Transactions)',
                           frontend_address=get_frontend_address(),
                           node_address=node_address if node_address else get_random_node_address())
