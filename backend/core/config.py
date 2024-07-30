import os


DIFFICULTY = 4 # Difiiculty of PoW algorithm
FEE_PER_TRANSACTION = 0.01  # 0.01% of amount
COINBASE_BENEFICIARY = os.environ.get('COINBASE_BENEFICIARY', '1ad4154a06f1126a504737f501fd05e1e76eecd9538ae1f497ca31144e9ec96aa59d4fe155888a07af75321ad45309596fd8dd48ef59414bb134968b6b0d7f42') # Wallet of the current miner

### Do Not Change These ###
TRANSACTIONS_COUNT_PER_BLOCK = 3 # Number of transaction per block + Block reward transaction
RANGE_BLOCK_SIZE_B = 2048  # 2048 Bytes
MAX_TRANSACTION_AMOUNT = 21000000 # Transaction safety
SUBSIDY_HALVING_INTERVAL = 2 # To calculate block subsidy
ROUND_AMOUNT = 8 # To round float numbers
