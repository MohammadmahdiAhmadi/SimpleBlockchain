import os

CONNECTED_NODE_ADDRESSES = {os.environ.get('CONNECTED_NODE_ADDRESS')}
if not CONNECTED_NODE_ADDRESSES:
    CONNECTED_NODE_ADDRESSES = {"http://127.0.0.1:8000"}

FRONTEND_ADDRESS = os.environ.get('FRONTEND_ADDRESS')
if not FRONTEND_ADDRESS:
    FRONTEND_ADDRESS = "http://127.0.0.1:5000"