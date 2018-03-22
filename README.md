# Easy-blockchain
A blockchain, coin or building tools for human. It doesn't include servers.

## Getting Started

Installation:
```
pip install easy_blockchain
```

Create your first wallet and add your first transaction:
```
from easy_blockchain.wallet import Wallet
from easy_blockchain.blockchain import Block, BlockChain

# Create the first user
wallet = Wallet()
user01 = wallet.getPublicKey()
trans01 = wallet.create_transaction('test01', 1, 0.5, 'one message')
trans02 = trans01.copy() # create a forgery attack
print('Check if a forgery attack have same as real transaction')
print('trans01 == trans02', trans01 == trans02)

# Create the second user
wallet02 = Wallet()
user02 = wallet02.getPublicKey()
trans03 = wallet02.create_transaction(user01, 1.5, 0.12,'user02 send to user01')
```

In miner side, the miner receive your transaction, add it to blockchain and mining:

```
# add transactions to a block
block = Block()
block.add_transaction(trans01)
block.add_transaction(trans02)  # check adding a forgery attack
block.add_transaction(trans03)

# check how many transactions were added
print('--------------------------------------')
print('The block 1 have 2 real transaction:')
print(json.dumps(block.transactions, indent=2))
# create a blockchain and become an miner
coin = BlockChain()
# mine a proof
proof = coin.mine_proof()
print('The first proof is:',proof)
# save blockchain to local database
coin.save_chain()
```

The blockchain also provides balance and history of trading:

```
print('--------------------------------------')
print('The transaction history and the balance of users:')
mycoin = coin.get_history(user01)
print('User: user01 balance:', coin.get_balance(user01))
print(json.dumps(mycoin, indent=4))

mycoin = coin.get_history(user02)
print('User: user02 balance:', coin.get_balance(user02))
print(json.dumps(mycoin, indent=4))

mycoin = coin.get_history(user03)
print('User: user03 balance:', coin.get_balance(user03))
print(json.dumps(mycoin, indent=4))
```
