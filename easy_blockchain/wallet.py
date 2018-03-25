from ecdsa import SigningKey
import ecdsa
import base64
import json
import hashlib
from datetime import datetime
from easy_blockchain.database import savetoJson, loadfromJson


class Wallet(object):
    def __init__(self, curve=ecdsa.SECP256k1):
        self.curve = curve
        self.history = {}
        # generate private key
        sk = ecdsa.SigningKey.generate(curve=curve)
        private_key = sk.to_string().hex() # convert sk object to string then to hex
        # generate public key object from private key
        vk = sk.get_verifying_key()  # this is verification key (public key)
        public_key = vk.to_string().hex() # convert vk object to string then to hex
        # assign to publich attributes
        self.private_key_hex = private_key # hex type
        self.public_key_hex = public_key # hex type
        self.private_key = base64.b64encode(
            bytes.fromhex(self.private_key_hex)).decode()  # string type
        self.public_key = base64.b64encode(
            bytes.fromhex(self.public_key_hex)).decode()  # string type
    
    def create_signature(self, message):
        # convert sk object from hex of private_key
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(self.private_key_hex), curve=self.curve)
        # signature object which can be checked verify by vk.verify(signature, message)
        signature = sk.sign(message.encode()) # convert message to byte 
        # convert signature to short type and decode() to opimal data for sending
        signature = base64.b64encode(signature).decode()
        return signature

    def getPublicKey(self):
        # make it shorter and decode to readable string
        return self.public_key
    
    def getPrivateKey(self):
         # make it shorter and decode to readable string
        return self.private_key

    def create_transaction(self, receiver, amount, fee=0, message={},sender=None):
        if sender is None:
            sender = self.getPublicKey()
        transaction = {
            'sender': sender,
            'receiver':receiver,
            'amount':amount,
            'message':message,
        }
        # print(json.dumps(transaction, sort_keys=True))
        signal = self.create_signature(json.dumps(transaction, sort_keys=True))
        transaction['signature'] = signal
        return transaction
    
    def recover_fromkey(self, private_key, curve=ecdsa.SECP256k1):
        self.private_key = private_key
        self.private_key_hex = (base64.b64decode(private_key)).hex()
        sk = ecdsa.SigningKey.from_string(
            bytes.fromhex(self.private_key_hex), curve=self.curve)
        # generate public key object from private key
        vk = sk.get_verifying_key()  # this is verification key (public key)
        public_key = vk.to_string().hex()  # convert vk object to string then to hex
        self.public_key_hex = public_key  # hex type
        self.public_key = base64.b64encode(
            bytes.fromhex(self.public_key_hex)).decode()  # string type
    
    def savetoJson(self):
        data = {
            'private_key':self.private_key,
            'private_key_hex': self.private_key_hex,
            'public_key': self.public_key,
            'public_key_hex':self.public_key_hex,
        }
        savetoJson(data,'wallet.txt')



    

