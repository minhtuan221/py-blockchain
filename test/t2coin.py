from cython_npm.cythoncompile import require
Wallet = require('../easy_blockchain/wallet').Wallet
# from easy_blockchain.wallet import Wallet
Block = require('../easy_blockchain/blockchain').Block
BlockChain = require('../easy_blockchain/blockchain').BlockChain
# from easy_blockchain.blockchain import Block, BlockChain# Create the first user
wallet = Wallet()
user01 = wallet.getPublicKey()
user01
trans01 = wallet.create_transaction('test01', 1, 0.5, 'user01 send 1')
trans02 = trans01.copy()  # create a forgery attack
print('Check if a forgery attack have same as real transaction')
print('trans01 == trans02', trans01 == trans02)
