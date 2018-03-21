from ecdsa import SigningKey
import ecdsa
import base64
import json
import hashlib
from datetime import datetime
from database import savetoFile, loadfromFile

class Wallet(object):
    def __init__(self, curve=ecdsa.SECP256k1):
        self.curve = curve
        # generate private key
        sk = ecdsa.SigningKey.generate(curve=curve)
        private_key = sk.to_string().hex() # convert sk object to string then to hex
        # generate public key object from private key
        vk = sk.get_verifying_key()  # this is verification key (public key)
        public_key = vk.to_string().hex() # convert vk object to string then to hex
        # assign to publich attributes
        self.private_key = private_key # hex type
        self.public_key = public_key # hex type
    
    def create_signature(self, message):
        # convert sk object from hex of private_key
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(self.private_key), curve=self.curve)
        # signature object which can be checked verify by vk.verify(signature, message)
        signature = sk.sign(message.encode()) # convert message to byte 
        # convert signature to short type and decode() to opimal data for sending
        signature = base64.b64encode(signature).decode()
        return signature

    def getPublicKey(self):
        # make it shorter and decode to readable string
        return base64.b64encode(bytes.fromhex(self.public_key)).decode()
    
    def getPrivateKey(self):
         # make it shorter and decode to readable string
        return base64.b64encode(bytes.fromhex(self.private_key)).decode()

    def create_transaction(self, receiver, amount, fee=0, message={}):
        transaction = {
            'sender':self.getPublicKey(),
            'receiver':receiver,
            'amount':amount,
            'fee':fee,
            'message':message,
        }
        print(json.dumps(transaction, sort_keys=True))
        signal = self.create_signature(json.dumps(transaction, sort_keys=True))
        transaction['signature'] = signal
        return transaction



    
