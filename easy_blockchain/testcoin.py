from wallet import Wallet
from blockchain import Block, BlockChain
from ecdsa import SigningKey
import ecdsa
import base64
import json
import hashlib
# sk = SigningKey.generate()  # uses NIST192p
# print('sk',sk.to_string().hex())
# # print('sk', sk.to_pem())
# vk = sk.get_verifying_key()
# print('vk',vk.to_string().hex())
# # print('vk', vk.to_pem())
# mes = "message".encode() # encode message to byte
# signature = sk.sign(mes)
# print('signature', signature.hex())
# print('type of signature', type(signature))
# check = vk.verify(signature, mes)
# print(check)

# print(base64.b64encode(bytes.fromhex(pb)).decode())
# mes = 'this is a test'
# mysign, abc = wallet.create_signature(mes)
# block = Block()
# x = block.check_signature(pb,mysign,mes)

wallet = Wallet()
print('wallet.getPublicKey():')
print(wallet.getPublicKey())
print('wallet.getPrivateKey():')
print(wallet.getPrivateKey())
pb = wallet.getPublicKey()
trans01 = wallet.create_transaction('test01', 1, 0, 'one message')
trans02 = trans01.copy() # check forgery attack
print(trans01 == trans02)

# print(x)
# print(trans01)
# add transactions to a block
block = Block()
block.add_transaction(trans01)
block.add_transaction(trans02)
# print(x)
print(block.transactions)

coin = BlockChain()
# mine a proof
proof = coin.mine_proof()
print(proof)
x = coin.add_block(block,'abc',proof=proof)
print(x)
trans03 = wallet.create_transaction('test03', 3, 0, 'the third message')
block = Block()
# block.add_transaction(trans02)
block.add_transaction(trans03)

proof = coin.mine_proof()
print(proof)
x = coin.add_block(block, 'abc', proof=proof)

for block in coin.view_blockchain():
    print(json.dumps(block, indent=4))

mycoin = coin.get_balance(pb)
print(mycoin)
mycoin = coin.get_balance('abc')
print(mycoin)
coin.save_chain()
coin.load_chain()
mycoin = coin.get_history(pb)
print(json.dumps(mycoin, indent=4))
mycoin = coin.get_history('test01')
print(json.dumps(mycoin, indent=4))
