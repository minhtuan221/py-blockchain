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
        # cannot send amount < 0
        if transaction['amount']<0 or transaction['fee']<0:
            return False
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
    
    def __len__(self):
        return len(self.transactions)



class BlockChain(object):
    def __init__(self, firstblock=Block(), curve=ecdsa.SECP256k1):
        self.chain = []
        self.lastblock = None
        self.INITIAL_COINS_PER_BLOCK = 50
        self.HALVING_FREQUENCY = 100000
        self.MINBLOCK = 1
        self.curve = curve
        # Create the first (genesis) block
        firstblock = firstblock
        self.process_block(firstblock.export(), '0', proof=1, previous_hash='1')

    def get_reward(self, index):
        # INITIAL_COINS_PER_BLOCK coins per block.
        # Reduce by haft every HALVING_FREQUENCY blocks
        # index = len(self.chain)+1
        reward = self.INITIAL_COINS_PER_BLOCK
        if self.HALVING_FREQUENCY is not None:
            for i in range(1, (round(index / self.HALVING_FREQUENCY) + 1)):
                reward = min(reward / 2, 1)
        return reward
    
    def get_blockfee(self, trans):
        # trans = self.transactions
        fee = 0
        for item in trans:
            fee += trans[item]['fee']
        # print(fee)
        return fee

    
    def reward_signature(self, message, index):
        guess = f'{message}{index}'.encode()
        signature = hashlib.sha256(guess).hexdigest()
        return signature

    def hash(self, block):
        # Make sure that the Dictionary is Ordered, or It'll be inconsistent hashing
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, block: Block, miner_address, proof=1,  previous_hash=None):
        # check if block have sender = '0'
        if "0" in block.senders:
            # check if block already have a reward transactions
            return False
        # valid amount send in block:
        if not self.valid_sender_amount(block.transactions,block.senders):
            return False
        if len(block)<self.MINBLOCK and self.lastblock is not None:
            return False
        reward_amount = self.get_reward(
            len(self.chain)+1) + self.get_blockfee(block.transactions)
        reward_miner = {
            'sender': '0',
            'receiver': miner_address,
            'amount': reward_amount,
            'fee': 0,
            'message': 'reward_miner',
        }
        reward_miner_signature = self.reward_signature(
            json.dumps(reward_miner, sort_keys=True), len(self.chain)+1)
        reward_miner['signature'] = reward_miner_signature
        # print('reward_miner[signature]', reward_miner['signature'])
        block.add_transaction(reward_miner)
        block = block.export()
        return self.process_block(block, reward_miner_signature, proof=proof, previous_hash=previous_hash)

    def process_block(self, block, miner_address, proof=1, previous_hash=None):
        if self.valid_block(proof):
            newblock = {
                'index': len(self.chain) + 1,
                'timestamp': datetime.utcnow().isoformat(),
                'transactions': block,
                'proof': proof,
                'previous_hash': previous_hash or self.chain[-1]['hash'],
                'miner':miner_address,
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
            
            # Check if the miner reward is correct
            if not self.valid_miner(block['transactions'], current_index):
                return False
            
            # Check if any transaction in the block is correct
            if not self.valid_any_transaction(block['transactions'], block['miner']):
                return False

            last_block = block
            current_index += 1

        return True
    
    def valid_miner(self, transactions, current_index):
        # get the true reward of the block
        reward_amount = self.get_reward(
            current_index) + self.get_blockfee(transactions)
        reward_amount_real = 0
        for key in transactions:
            if transactions[key]['sender'] =='0':
                reward_amount_real += transactions[key]['amount']
        if reward_amount_real>=reward_amount:
            print('Reward amount is wrong:',
                  reward_amount_real, '>', reward_amount)
            return True
        return False
    
    def valid_any_transaction(self, block_trans:dict, miner):
        reward_miner = block_trans.pop(miner, None)
        if reward_miner is None:
            print('No miner reward transaction')
            return False
        block = Block()
        for key in block_trans:
            if not block.add_transaction(block_trans[key]):
                print('Transaction signature is wrong:', key)
                return False
        return True

    def valid_sender_amount(self, block, senders):
        # don't let any sender have below zero to send money
        amount = {}
        for signature in block:
            trans = block[signature]
            if not trans['sender'] in amount:
                amount[trans['sender']] = 0
            amount[trans['sender']] += trans['amount'] + trans['fee']
        for sender in senders:
            # get Sum amount of all transactions of one sender in block
            # print(self.get_balance(sender), amount[sender])
            if self.get_balance(sender)<amount[sender]:
                print('Transaction have not enough money:',sender)
                return False
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
                        'address': transactions[item]["receiver"],
                        'fee': transactions[item]["fee"],
                        'message': transactions[item]["message"],
                    }
                if transactions[item]["receiver"] == address:
                    history[item] = {
                        'timestamp': block['timestamp'],
                        'amount': transactions[item]["amount"],
                        'address': transactions[item]["sender"],
                        'fee': transactions[item]["fee"],
                        'message': transactions[item]["message"],
                    }
                if transactions[item]["sender"] == address and transactions[item]["receiver"] == transactions[item]["sender"]:
                    history[item] = {
                        'timestamp': block['timestamp'],
                        'amount': 0,
                        'address': transactions[item]["sender"],
                        'fee': transactions[item]["fee"],
                        'message': transactions[item]["message"],
                    }
        return history
    
    def get_balance(self, address):
        history = self.get_history(address)
        balance = 0
        for trans in history:
            balance += history[trans]['amount']-history[trans]['fee']
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
