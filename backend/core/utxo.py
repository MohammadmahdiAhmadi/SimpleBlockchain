import copy
from core.config import ROUND_AMOUNT


class UTXO:
    def __init__(self, public_key, amount):
        self.public_key = public_key
        self.amount = round(float(amount), ROUND_AMOUNT)

    def __repr__(self):
        return f"UTXO(public_key={self.public_key}, amount={self.amount})"

class UTXOPool:
    def __init__(self, utxos=None):
        self.utxos = utxos or {}

    def to_json(self):
        return {
            k: {
                'public_key': v.public_key,
                'amount': v.amount
            } for k, v in self.utxos.items()
        }

    @classmethod
    def from_json(cls, data):
        utxos = {k: UTXO(**v) for k, v in data.items()}
        return cls(utxos)

    def add_utxo(self, public_key, amount):
        if public_key in self.utxos:
            self.utxos[public_key].amount = round(self.utxos[public_key].amount + amount, ROUND_AMOUNT)
        else:
            utxo = UTXO(public_key, amount)
            self.utxos[public_key] = utxo

    def handle_transaction(self, transaction, fee_receiver):
        if not self.is_valid_transaction(transaction):
            return False

        input_utxo = self.utxos[transaction.input_public_key]
        input_utxo.amount = round(input_utxo.amount - (transaction.amount + transaction.fee), ROUND_AMOUNT)

        if input_utxo.amount == 0:
            del self.utxos[transaction.input_public_key]

        self.add_utxo(transaction.output_public_key, transaction.amount)
        self.add_utxo(fee_receiver, transaction.fee)
        return True

    def handle_block_reward_transaction(self, transaction):
        if transaction.input_public_key != "BLOCK_REWARD":
            return False
        
        self.add_utxo(transaction.output_public_key, transaction.amount)

    def is_valid_transaction(self, transaction):
        utxo = self.utxos.get(transaction.input_public_key)
        return utxo is not None and utxo.amount >= (transaction.amount + transaction.fee)

    def clone(self):
        return UTXOPool(copy.deepcopy(self.utxos))
