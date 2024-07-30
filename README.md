# Simple Blockchain Project

## Overview
This project is a simple blockchain implementation featuring basic functionalities such as signing transactions, creating transactions, a robust UI, transaction fees, block rewards for miners, consensus across all nodes, simple UTXO management, and a maximum coin supply of 21 million. The project includes both a frontend (user interface) and a backend.

## Features
- Robust UI
- Sign and Create transactions
- Transaction fee
- Block reward for miners
- Consensus among all nodes
- Simple UTXO management
- Maximum coin supply of 21 million
- `get_block_subsidy` function similar to Bitcoin

## Frontend
The frontend is built using Flask, HTML, CSS, and JavaScript. It includes the following pages:
### Home page
- Sign and create transactions
- View chain of blocks
- View peers
- Generate wallet on the home page
- Connect to random blockchain nodes (user can choose node IP)
### Block page
- View block details
### Mempool Page
- View mempool on the mempool page

## Backend
The backend is structured as follows:
- **app directory**: Contains necessary APIs with Flask.
- **run.py**: Main program that restores seed node data and registers new nodes with seed nodes. It also runs two threads: one for the mining loop and one for consensus with new peers.
- **node_config.py**: Configuration file for node settings.
- **core directory**: Contains classes for blockchain, block, transaction, consensus, config and UTXO management.
- **consensus.py**: Functions for consensus and announcing blocks, transactions, and peers.
- **config.py**: Configuration file for blockchain settings.

## Directory Structure
.
├── backend
│ ├── run.py
│ ├── node_config.py
│ ├── app
│ │ ├── init.py
│ │ └── routes.py
│ ├── core
│ │ ├── init.py
│ │ ├── block.py
│ │ ├── blockchain.py
│ │ ├── config.py
│ │ ├── consensus.py
│ │ ├── crypto.py
│ │ ├── transaction.py
│ │ ├── utils.py
│ │ └── utxo.py
│ └── tests
│ ├── data
│ │ └── chain_bkp.json
├── frontend
│ ├── run.py
│ ├── app
│ │ ├── init.py
│ │ ├── config.py
│ │ ├── views.py
│ │ ├── nodes_connection.py
│ │ ├── templates
│ │ │ ├── base.html
│ │ │ ├── block.html
│ │ │ ├── index.html
│ │ │ └── mempool.html
└── requirements.txt
├── Makefile
├── Dockerfile.backend
├── Dockerfile.frontend
├── compose.yaml
└── README.md

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/simple-blockchain.git
   cd simple-blockchain
   ```

2. Build and run the project using Docker Compose:
    ```sh
    make rebuild-up
    ```

### Configuration
The backend node config is set in compose.yaml (key: default):
```yaml
SEED_NODE: http://127.0.0.1:8000 # Seed node that help new nodes to register
NODE_IP: 127.0.0.1 # Current node ip
NODE_PORT: 8000 # Current node port
chain_file_name: ./data/chain_bkp.json # File path to store backup of seed node
COINBASE_BENEFICIARY: 1ad4154a06f1126a504737f501fd05e1e76eecd9538ae1f497ca31144e9ec96aa59d4fe155888a07af75321ad45309596fd8dd48ef59414bb134968b6b0d7f42
```

The backend core config is set in baackend/core/config.py (key: default):
```python
DIFFICULTY = 4 # Difiiculty of PoW algorithm
FEE_PER_TRANSACTION = 0.01  # 0.01% of amount
```

### Usage
Access the frontend at http://localhost:5000. The following pages are available:

- Home: Sign and create transactions, view chain of blocks, view peers, generate wallet.
- Block: View block details.
- Mempool: View mempool.

## Development
### Build the frontend and backend separately:
```sh
make build-frontend
make build-backend
```
### Start the services:
```sh
make up
```
### Stop the services:
```sh
make down
```
### Restart the services:
```sh
make restart
```
### Down/Rebuild/Up the services:
```
make rebuild-up
```

## ToDo:
- Bitcoin-like UTXO
- Propagate tx in frontend
- 