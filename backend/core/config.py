import os


DIFFICULTY = 4 # Difiiculty of PoW algorithm
FEE_PER_TRANSACTION = 0.01  # 0.01% of amount
COINBASE_BENEFICIARY = os.environ.get('COINBASE_BENEFICIARY', 'b3b6eedc5d6967c94aa2d65f9e0b77f34d9a7cde2b699d2b9039776cc92519900ee89b76732fc210ee91120b0dece9cef9518ad30d906c0b8f78919b6e87219c') # Wallet of the current miner

### Do Not Change These ###
TRANSACTIONS_COUNT_PER_BLOCK = 3 # Number of transaction per block + Block reward transaction
RANGE_BLOCK_SIZE_B = 2048  # 2048 Bytes
MAX_TRANSACTION_AMOUNT = 21000000 # Transaction safety
SUBSIDY_HALVING_INTERVAL = 2100000 # To calculate block subsidy
ROUND_AMOUNT = 8 # To round float numbers
