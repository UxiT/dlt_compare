from hashlib import sha256
import json
import time


from flask import Flask, request
import requests


class Block:

   

    def __init__(self, index, transactions, timestamp, previous_hash, nonce = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash 
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True) 
        return sha256(block_string.encode()).hexdigest()


class BlockChain:

    #Сложность PoW алгоритма

    difficulty = 2
    
    def __init__(self):
        self.unconfirmed_transactions = [] # Пока ещё не добавленные в блокчейн данные
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):

        genesis_block = Block(0, [], time.time(), '0')
        genesis_block.hash = genesis_block.compute_hash()

        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]


    def proof_of_work(self, block):
        

        block.nonce = 0

        compute_hash = block.compute_hash()
        
        while not compute_hash.startswith("0" + BlockChain.difficulty):
            block.nonce += 1
            compute_hash = block.compute_hash()

        return compute_hash

    def add_block(self, block, proof):
        """
        Функция, которая добавлят блок в блокчейн после проверки

        Проверка включает:
            1. 
        """

        previous_hash = self.last_block.hash

        if(previous_hash != block.previous_hash):
            return False

        if not BlockChain.is_valid_proof(block, proof):
            return False 

        block.hash = proof
        self.chain.append(block)

        return True

    
    @classmethod
    def is_valid_proof(self, block, block_hash):
        """
        Проверяет является ли block_hash действительно павильным хэшем блока и удовлетворяет ли 
        данный хэш критериям
        """

        return (block_hash.startswith('0' * BlockChain.difficulty) and block_hash == block.compute_hash())


    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):

        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(
            index=last_block.index +1,
            transactions = self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=last_block.hash()
        )

        proof  = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return new_block.index

# init Flask app

app = Flask(__name__)

# init Blockchain object

blockchain = BlockChain()
blockchain.create_genesis_block()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]


    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid Transaction data", 404

    tx_data["timestamp"] = time.time()
    blockchain.add_new_transaction(tx_data)

    return "Success", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)


    return json.dumps({"length": len(chain_data), "chain": chain_data})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "Отсутствуют транзакции для вычисления"
    else:
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):   
            announce_new_block(blockchain.last_block)
        return "Блок #{} вычислен.".format(blockchain.last_block.index)



@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


#Содержит адреса других участников  сети
peers = set()

@app.route("/register_with", methods=['POST'])
def register_with_existing_node():
    node_address = request.get_json()["node_address"]

    if not node_address:
        return 'Invalid data', 404


    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    #Создание запроса, чтобы зарегистрировать удалённый узел и получить информацию

    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), 
                             headers=headers)


    if response.status_code == 200:
        global blockchain
        global peers

        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)

        peers.update(response.json()["peers"])
        return "Регистрация успешна", 200

    else:
        return response.content, response.status_code

    
def create_chain_from_dump(chain_dump):
    blockchain = BlockChain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(
                        block_data["index"],
                        block_data["transactions"],
                        block_data["timestamp"],
                        block_data["previous_hash"]
                     )

        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  
            blockchain.chain.append(block)
    return blockchain

@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "Блок был отклонён узлом", 400

    return "Блок добавлен с цепь", 201


def consensus():
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get("{}chain".format(node))
        lenght = response.json()['lenght']
        chain = response.json()["chain"]

        if lenght > current_len and blockchain.check_chain_validity(chain):
            current_len = lenght
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    Оповещает сеть о том, что новый блок был рассчитан.
    Остальные блоки могут подтвердить подлинность.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)

app.run(debug=True, port=8000)