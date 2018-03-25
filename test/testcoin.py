from cython_npm.cythoncompile import require
Wallet = require('../easy_blockchain/wallet').Wallet
# from easy_blockchain.wallet import Wallet
Block = require('../easy_blockchain/blockchain').Block
BlockChain = require('../easy_blockchain/blockchain').BlockChain
# from easy_blockchain.blockchain import Block, BlockChain
from ecdsa import SigningKey
import ecdsa
import base64
import json
import hashlib


# Create the first user
wallet = Wallet()
user01 = wallet.getPublicKey()
trans01 = wallet.create_transaction('test01', 1, 0.5, 'user01 send 1')
trans02 = trans01.copy() # create a forgery attack
print('Check if a forgery attack have same as real transaction')
print('trans01 == trans02', trans01 == trans02)

# Create the second user
wallet02 = Wallet()
user02 = wallet02.getPublicKey()
trans03 = wallet02.create_transaction(user01, 1.5, 0.12,'user02 send to user01')

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
# create genesis block
genesis_block = Block()
genesis_tran01 = Wallet().create_transaction(user01,1000,0,'genesis to user01',sender='0')
genesis_tran02 = Wallet().create_transaction(
    user02, 1000, 0, 'genesis to user02', sender='0')

genesis_block.add_transaction(genesis_tran01)
genesis_block.add_transaction(genesis_tran02)

# create a blockchain and add the genesis block
coin = BlockChain(firstblock=genesis_block)
# mine a proof
proof = coin.mine_proof()
print('The first proof is:',proof)
# create the miner - user03
wallet03 = Wallet()
user03 = wallet03.getPublicKey()
x = coin.add_block(block,user03,proof=proof)
print('--------------------------------------')
print('Check if a block have been added to a blockchain:')
print(x) # will return true if successful create a new block
print('--------------------------------------')
print('The blockchain with 2 first blocks:')
print(json.dumps(coin.view_blockchain(), indent=2))


# create 2 more transaction for block 3
trans01 = wallet.create_transaction(user02, 1.3, 0.21, 'user01 send to user02')
trans02 = wallet02.create_transaction(user02, 10, 0.5, 'user02 send to user02, him self=> will be count as fee')
# create block 3 then add 2 transaction to it
block = Block()
block.add_transaction(trans01)
block.add_transaction(trans02)
print('--------------------------------------')
print('The block 3 have been created. Find the proof:')
# mine a proof
proof = coin.mine_proof()
coin.add_block(block, user03, proof=proof)
print('The proof is:', proof)
print('--------------------------------------')
print('The blockchain with 3 blocks:')
print(json.dumps(coin.view_blockchain(), indent=2))


# create 2 more transaction for block 4
trans01 = wallet.create_transaction(user02, 10000, 0.21, 'user01 send to user02')
trans02 = wallet02.create_transaction(
    user01, 10, 1000, 'user02 send to user01')
# create block 4 then add 2 transaction to it
block = Block()
t1 = block.add_transaction(trans01)
t2 = block.add_transaction(trans02)
print(t1,t2)
print('--------------------------------------')
print('The block 4 have been created. Find the proof:')
# mine a proof
proof = coin.mine_proof()
print('The proof is:', proof)
ok = coin.add_block(block, user03, proof=proof)
print('Block 4 will not be add because of the over-amount of user01 and user02:', ok)
print('--------------------------------------')
print('The blockchain with remain blocks:')
print(json.dumps(coin.view_blockchain(), indent=2))



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
# save blockchain to local database
coin.save_chain()
coin.load_chain()
wallet.savetoJson()
