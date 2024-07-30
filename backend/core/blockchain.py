import time

from core.config import COINBASE_BENEFICIARY, TRANSACTIONS_COUNT_PER_BLOCK, DIFFICULTY
from core.utxo import UTXOPool
from core.block import Block
from core import blockchain_mutex


class Blockchain:
    def __init__(self, chain=None, create_genesis_block=True):
        self.unconfirmed_transactions = []
        self.chain = chain
        if self.chain is None:
            self.chain = []
            if create_genesis_block:
                self.create_genesis_block()

    def to_json_unconfirmed_transactions(self):
        return [tx.to_json() for tx in self.unconfirmed_transactions]

    def to_json(self):
        return {
            'unconfirmed_transactions': self.to_json_unconfirmed_transactions(),
            'chain': [block.to_json() for block in self.chain]
        }

    def create_genesis_block(self):
        utxo_pool = UTXOPool()
        genesis_block = Block(0, [], int(time.time()), "0", utxo_pool, COINBASE_BENEFICIARY)
        genesis_block.add_reward_transaction()

        proof = self.proof_of_work(genesis_block)
        genesis_block.hash = proof

        self.chain.append(genesis_block)

    def set_genesis_block(self, block):
        if self.chain:
            self.chain[0] = block
        else:
            self.chain.append(block)

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

    def ready_to_mine(self):
        return len(self.unconfirmed_transactions) >= TRANSACTIONS_COUNT_PER_BLOCK

    def add_new_transaction_to_mempool(self, transaction):
        # Check Duplicate. __eq__ function
        if transaction in self.unconfirmed_transactions:
            return False
            
        # Check tx validity with last block
        if not self.last_block.is_valid_transaction(transaction):
            return False

        self.unconfirmed_transactions.append(transaction)
        self.unconfirmed_transactions.sort(key=lambda tx: tx.fee, reverse=True)

        return True
    
    def remove_transactions_from_mempool(self, transactions: list):
        self.unconfirmed_transactions = [item for item in self.unconfirmed_transactions if item not in transactions]

    def select_transactions_for_block(self, block):
        for i in range(len(self.unconfirmed_transactions)):
            tx = self.unconfirmed_transactions[i]
            
            # Add to block if valid
            if block.add_transaction(tx):
                if block.transactions_len() == TRANSACTIONS_COUNT_PER_BLOCK + 1:
                    break

    def add_block(self, block, proof):
        if not block.has_valid_size():
            return False

        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * DIFFICULTY):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * DIFFICULTY) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.ready_to_mine():
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=[],
                          timestamp=int(time.time()),
                          previous_hash=last_block.hash,
                          utxo_pool=last_block.utxo_pool.clone(),
                          coinbase_beneficiary=COINBASE_BENEFICIARY,)
        
        new_block.add_reward_transaction()
        self.select_transactions_for_block(new_block)

        proof = self.proof_of_work(new_block)
        
        with blockchain_mutex:
            if not self.add_block(new_block, proof):
                return False
            
            self.remove_transactions_from_mempool(new_block.transactions)

        return True
