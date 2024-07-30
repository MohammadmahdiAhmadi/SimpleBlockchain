import hashlib
import time

from core.config import ROUND_AMOUNT, FEE_PER_TRANSACTION, MAX_TRANSACTION_AMOUNT
from core.crypto import CryptoTools


class Transaction:
    def __init__(self, input_public_key, output_public_key, amount, signature=None, timestamp=None, fee=0.0):
        self.input_public_key = input_public_key
        self.output_public_key = output_public_key
        self.amount = round(float(amount), ROUND_AMOUNT)  # Convert amounts to satoshi

        if input_public_key == "BLOCK_REWARD":
            self.fee = float(0)
        else:
            if fee:
                self.fee = round(float(fee), ROUND_AMOUNT)
            else:
                self.fee = round(float(self.amount * FEE_PER_TRANSACTION), ROUND_AMOUNT)
                self.amount = round(self.amount - self.fee, ROUND_AMOUNT)

        self.signature = signature
        self.timestamp = timestamp if timestamp else int(time.time())
        self._set_hash()

    def __eq__(self, other):
        return self.signature == other.signature and self.input_public_key == other.input_public_key

    def _set_hash(self):
        self.hash = self._calculate_hash()

    def _calculate_hash(self):
        data = f"{self.input_public_key}{self.output_public_key}{self.amount}{self.fee}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def has_valid_signature(self):
        return (
            self.signature is not None and
            CryptoTools.verify_signature(self.hash, self.signature, self.input_public_key)
        )

    def has_valid_amount(self):
        return 0 <= self.amount + self.fee <= MAX_TRANSACTION_AMOUNT
    
    def is_valid(self):
        return self.has_valid_amount() and self.has_valid_signature()
    
    def to_json(self) -> dict:
        return {
            'input_public_key': self.input_public_key,
            'output_public_key': self.output_public_key,
            'amount': self.amount,
            'fee': self.fee,
            'signature': self.signature,
            'hash': self.hash,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_json(cls, transaction, calculate_fee=True):
        return cls(
            transaction['input_public_key'],
            transaction['output_public_key'],
            transaction['amount'],
            transaction.get('signature'),
            transaction.get('timestamp'),
            0.0 if calculate_fee else transaction.get('fee'),
        )

    @classmethod
    def list_from_json(cls, transactions, calculate_fee=True) -> list:
        tx_list = []
        for tx in transactions:
            tx_list.append(cls.from_json(tx, calculate_fee))
        
        return tx_list