from core.utxo import UTXOPool
from core.transaction import Transaction
from core.config import TRANSACTIONS_COUNT_PER_BLOCK, DIFFICULTY, SUBSIDY_HALVING_INTERVAL, ROUND_AMOUNT
from hashlib import sha256
import json


class Block:
    def __init__(self, index: int, transactions: list, timestamp: int, previous_hash: str, utxo_pool: UTXOPool, coinbase_beneficiary:str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.coinbase_beneficiary = coinbase_beneficiary
        self.nonce = nonce
        self.utxo_pool = utxo_pool
        self._set_hash()

    def _set_hash(self):
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_dict = self.to_json(include_hash=False)
        block_string = json.dumps(block_dict, sort_keys=True)

        generated_hash = sha256(block_string.encode()).hexdigest()
        return generated_hash
    
    @staticmethod
    def get_block_subsidy(index):
        halvings = index // SUBSIDY_HALVING_INTERVAL
        
        # Force block reward to zero when right shift is undefined.
        if halvings >= 64:
            return 0

        n_subsidy = 50
        # Subsidy is cut in half every 210,000 blocks which will occur approximately every 4 years.
        # n_subsidy >>= halvings
        if halvings != 0:
            n_subsidy /= 2**halvings
        return round(n_subsidy, ROUND_AMOUNT)
    
    def transactions_len(self):
        return len(self.transactions)
    
    def has_valid_size(self):
        return self.transactions_len() == TRANSACTIONS_COUNT_PER_BLOCK + 1
    
    def add_reward_transaction(self):
        reward_tx = Transaction("BLOCK_REWARD",
                                self.coinbase_beneficiary, 
                                Block.get_block_subsidy(self.index))

        self.transactions.append(reward_tx)
        self.utxo_pool.handle_block_reward_transaction(reward_tx)
        self._set_hash()

    def add_transaction(self, transaction):
        # Check tx validity with current block
        if not self.is_valid_transaction(transaction):
            return False
        self.transactions.append(transaction)
        self.utxo_pool.handle_transaction(transaction, self.coinbase_beneficiary)
        self._set_hash()
        return True

    def is_root(self):
        return self.previous_hash == 'root'

    def is_valid(self):
        return (self.is_root() or 
                (self.hash.startswith('0' * DIFFICULTY) and 
                 self.hash == self.compute_hash()))

    def is_valid_transaction(self, transaction):
        return (transaction.is_valid() and
                self.utxo_pool.is_valid_transaction(transaction))

    def to_json(self, include_hash=True):
        block_dict = {
            'index': self.index,
            'transactions': [tx.to_json() for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'coinbase_beneficiary': self.coinbase_beneficiary,
            'nonce': self.nonce,
            'utxo_pool': self.utxo_pool.to_json(),
        }

        if hasattr(self, 'hash') and include_hash:
            block_dict['hash'] = self.hash

        return block_dict