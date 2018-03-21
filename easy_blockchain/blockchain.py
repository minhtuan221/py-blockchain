from ecdsa import SigningKey
import ecdsa
import base64
import json
import hashlib
from datetime import datetime
from database import savetoFile, loadfromFile


class Block(object):
    """Block is simplely a list of transaction

    Arguments:
        add_transaction (dict) -- add one transaction to block

    Returns:
        transactions {dict} -- dictionary of transactions
    """

    def __init__(self, curve=ecdsa.SECP256k1):
        """create a block - a list of transactions

        Keyword Arguments:
            curve {algorithm} -- [crypto-algorithm in ecdsa] (default: {ecdsa.SECP256k1})
        """
        self.transactions = {}
        self.curve = curve
        self.senders = set()

    def add_transaction(self, transaction: dict):
        message = transaction
        signature = message.pop('signature', None)
        public_key = message['sender']
        message = json.dumps(message, sort_keys=True)
        if self.check_signature(public_key, signature, message):
            self.transactions[signature] = transaction
            self.senders.add(public_key)
            return True
        return False

    def check_signature(self, public_key, signature, message):
        # print('signature', signature)
        # print('public_key', public_key)
        # print('message', message)
        if public_key == '0':
            return True
        # convert public_key to byte then to hex()
        public_key = (base64.b64decode(public_key)).hex()
        # convert signature to byte type
        signature = base64.b64decode(signature)
        # create verifykey object from string of byte of public_key
        vk = ecdsa.VerifyingKey.from_string(
            bytes.fromhex(public_key), curve=self.curve)
        try:
            return(vk.verify(signature, message.encode()))
        except:
            return False

    def export(self):
        return self.transactions

    def clear(self):
        self.transactions = {}
        self.senders = set()


class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.lastblock = None
        self.INITIAL_COINS_PER_BLOCK = 50
        self.HALVING_FREQUENCY = 100000
        # Create the first (genesis) block
        firstblock = Block()
        self.add_block(firstblock, '0', previous_hash='1')

    def get_reward(self):
        # INITIAL_COINS_PER_BLOCK coins per block.
        # Reduce by haft every HALVING_FREQUENCY blocks
        index = len(self.chain)+1
        reward = self.INITIAL_COINS_PER_BLOCK
        if self.HALVING_FREQUENCY is not None:
            for i in range(1, (round(index / self.HALVING_FREQUENCY) + 1)):
                reward = reward / 2
        return reward

    def hash(self, block):
        # Make sure that the Dictionary is Ordered, or It'll be inconsistent hashing
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, block: Block, miner_address, proof=1,  previous_hash=None):
        # check if block have sender = '0'
        if "0" in block.senders:
            print(block.senders)
            return False
        for sender in block.senders:
            if not self.valid_sender(sender):
                return False
        reward_miner = {
            'sender': '0',
            'receiver': miner_address,
            'amount': self.get_reward(),
            'fee': 0,
            'message': 'reward_miner',
            'signature': '0'
        }
        block.add_transaction(reward_miner)
        block = block.export()
        return self.process_block(block, proof=proof, previous_hash=previous_hash)

    def process_block(self, block, proof=1, previous_hash=None):
        if self.valid_block(proof):
            newblock = {
                'index': len(self.chain) + 1,
                'timestamp': datetime.utcnow().isoformat(),
                'transactions': block,
                'proof': proof,
                'previous_hash': previous_hash or self.chain[-1]['hash'],
            }
            newblock['hash'] = self.hash(newblock)
            self.chain.append(newblock)
            self.lastblock = self.chain[-1]
            return True
        return False

    def valid_block(self, proof):
        if self.lastblock is None:
            return True
        last_proof = self.lastblock['proof']
        last_hash = self.lastblock['hash']
        return self.valid_proof(last_proof, proof, last_hash)

    def consensus(self, newchain: list):
        newlength = len(newchain)
        mylength = len(self.chain)
        if mylength < newlength and self.valid_chain(newchain):
            self.chain = newchain
            return True
        return False

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check if the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check if the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
                return False

            last_block = block
            current_index += 1

        return True

    def valid_sender(self, sender):
        return True

    def view_blockchain(self):
        return self.chain

    def get_history(self, address):
        history = {}
        for block in self.chain:
            transactions = block['transactions']
            for item in transactions:
                if transactions[item]["sender"] == address:
                    history[item] = {
                        'timestamp': block['timestamp'],
                        'amount': -transactions[item]["amount"],
                        'address': transactions[item]["receiver"]
                    }
                if transactions[item]["receiver"] == address:
                    history[item] = {
                        'timestamp': block['timestamp'],
                        'amount': transactions[item]["amount"],
                        'address': transactions[item]["sender"]
                    }
        return history
    
    def get_balance(self, address):
        history = self.get_history(address)
        balance = 0
        for trans in history:
            balance += history[trans]['amount']
        return balance

    def save_chain(self, file_Name='chain.db'):
        savetoFile(self.chain, file_Name=file_Name)

    def load_chain(self, file_Name='chain.db'):
        self.chain = loadfromFile(file_Name=file_Name)

    def mine_proof(self):
        """[summary]

        Arguments:
            lastblock {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        last_proof = self.lastblock['proof']
        last_hash = self.lastblock['hash']

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    def valid_proof(self, last_proof, proof, last_hash):
        """Check if proof is correct

        Arguments:
            last_proof {[type]} -- [description]
            proof {[type]} -- [description]
            last_hash {[type]} -- [description]

        Returns:
            boolean -- True if proof is correct, False if not correct
        """
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return self.valid_zero(guess_hash)

    def valid_zero(self, guess_hash):
        return guess_hash[:3] == "000"
