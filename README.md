# py-blockchain
A blockchain for human

## Getting Started

Installation:
```
pip install easy_blockchain
```

Create your first wallet and add your first transaction:
```
from easy_blockchain.wallet import Wallet
from easy_blockchain.blockchain import Block, BlockChain

wallet = Wallet()
# wallet will auto gen your private and publickey
print('wallet.getPublicKey():')
print(wallet.getPublicKey())
print('wallet.getPrivateKey():')
print(wallet.getPrivateKey())
pb = wallet.getPublicKey()
trans01 = wallet.create_transaction('test01', 1, 0, 'one message')
```

In miner side, the miner receive your transaction, add it to blockchain and mining:

```
# add transactions to a block
block = Block()
block.add_transaction(trans01)

coin = BlockChain()
# mine a proof
proof = coin.mine_proof()
x = coin.add_block(block,'abc',proof=proof) # 'abc' is the miner address
# the block have been added
print(x)
coin.save_chain()
```

The nodes provides get_balance and get_history also:

```
mycoin = coin.get_history(pb)
print(json.dumps(mycoin, indent=4))
mycoin = coin.get_history('test01')
print(json.dumps(mycoin, indent=4))
```
