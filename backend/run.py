import threading

from core.consensus import consensus_new_peers
from core.utils import store_seed_node, register_with_seed_node, mining_loop
from node_config import NODE_PORT, is_seed_node

from app import app


if __name__ == '__main__':
    if is_seed_node():
        store_seed_node()
    else:
        if not register_with_seed_node():
            print("Couldn't register node")
            exit(0)

        # Create a thread for the consensus_new_peers
        consensus_new_peers_thread = threading.Thread(target=consensus_new_peers)
        consensus_new_peers_thread.start()

    # Create a thread for the mining loop
    mining_thread = threading.Thread(target=mining_loop)
    mining_thread.start()

    app.run(port=NODE_PORT)
