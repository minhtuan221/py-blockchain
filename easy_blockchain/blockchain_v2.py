from ecdsa import SigningKey
import ecdsa
import base64
import json
import hashlib
from datetime import datetime
from easy_blockchain.database import savetoJson, loadfromJson

class Trans(object):
    def __init__(self, private_key_hex, curve):
        self.input = dict()
        self.output = dict()
        self.curve = curve
        self.private_key_hex = private_key_hex

    def add_output(self, receiver, amount, message):
        self.output = {
            'receiver': receiver,
            'amount': amount,
            'message': message
        }
        # z = {**x, **y} merge two dictionary

    def add_input(self, previous_tx, sender, signature):
        transaction = {
            'previous_tx': previous_tx,
            'sender': sender,
            'receiver': self.output['receiver'],
            'amount': self.output['amount'],
            'message': self.output['message'],
        }
        # print(json.dumps(transaction, sort_keys=True))
        signal = self.create_signature(json.dumps(transaction, sort_keys=True))
        newInput = {
            'previous_tx': previous_tx,
            'sender': sender,
            'signature': signal,
        }
        self.input[previous_tx] = newInput

    def export(self):
        transaction = {
            'input': self.input,
            'output': self.output,
            'timestamp': datetime.utcnow().isoformat(),
        }
        return transaction

    def create_signature(self, message):
        # convert sk object from hex of private_key
        sk = ecdsa.SigningKey.from_string(
            bytes.fromhex(self.private_key_hex), curve=self.curve)
        # signature object which can be checked verify by vk.verify(signature, message)
        signature = sk.sign(message.encode())  # convert message to byte
        # convert signature to short type and decode() to opimal data for sending
        signature = base64.b64encode(signature).decode()
        return signature
