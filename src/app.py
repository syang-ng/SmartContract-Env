#!/usr/bin/python3

import os
import socketserver
import time

from base64 import b64decode, b64encode
from binascii import hexlify, unhexlify
from collections import defaultdict
from hashlib import sha1

import requests

from ethereum import utils
from solc import compile_source
from web3 import Web3

from config import *


my_ipc = Web3.WebsocketProvider('wss://ropsten.infura.io/ws/v3/{}'.format(INFURA_PROJECT_ID))
assert my_ipc.isConnected()
w3 = Web3(my_ipc)

flag = open(FLAG_PATH).read()
source = open(SOURCE_PATH).read()
session = defaultdict(lambda : 'No address for this token')

start_block = w3.eth.blockNumber - 86400
compiled_contract = compile_source(source)['<stdin>:{}'.format(CONTRACT_NAME)]
base_contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])

# random
def random_prefix():
    return hexlify(os.urandom(3)).decode('utf8')


def random_token():
    session_id = os.urandom(32)
    return session_id


def random_addr():
    priv = utils.sha3(os.urandom(4096))
    addr = utils.checksum_encode(utils.privtoaddr(priv))
    return priv.hex(), addr


# web3
def get_nonce(address):
    return w3.eth.getTransactionCount(Web3.toChecksumAddress(address))


def get_ETH(address):
    url = "https://faucet.metamask.io/"
    headers = {
        'Content-Type': "text/plain",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Host': "faucet.metamask.io",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "42",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }
    while True:
        try:
            response = requests.post(url, data=address, headers=headers)
            if 'error' not in response.text:
                break
        except:
            pass
    return response.text


def deploy_challenge(contract):
    # get random address
    privkey, address = random_addr()
    # get some ETH
    tx_hash = get_ETH(address)

    print(tx_hash)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    # deploy contract
    c = w3.eth.contract(
        abi=contract['abi'],
        bytecode=contract['bin']
    )
    tx = c.constructor().buildTransaction({'nonce': get_nonce(address)})
    signed_tx = w3.eth.account.signTransaction(tx, privkey)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(tx_hash)
    while True:
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        if tx_receipt != None:
            break
        time.sleep(1)
    return tx_receipt['contractAddress']


def complie_challenge():
    # junk_code
    cnt = int(hexlify(os.urandom(1)), 16) % 64
    junk_code = '\n'.join(['uint v{} = {};'.format(i, int(hexlify(os.urandom(32)), 16))  for i in range(cnt)])
    # code generate
    contract_pos = source.index(CONTRACT_NAME)
    try:
        next_contract_pos = source.index('contract', contract_pos)
    except:
        next_contract_pos = len(source)
    insert_pos = next_contract_pos - source[contract_pos:next_contract_pos][::-1].index('}') - 1
    code = source[:insert_pos] + junk_code + source[insert_pos:]

    contracts = compile_source(code)
    return contracts['<stdin>:{}'.format(CONTRACT_NAME)]


def new_challenge():
    contract = complie_challenge()
    return deploy_challenge(contract)


def get_flag(address):
    event = getattr(base_contract.events, EVENT_NAME)
    f = event.createFilter(fromBlock=start_block, address=address)
    return flag if len(f.get_all_entries()) > 0 else 'No flag For you'


# challenge
def PoW(request):
    while True:
        prefix = random_prefix()
        request.sendall('hashlib.sha1(input).hexdigest() == "{}"\r\n> '.format(prefix).encode('utf-8'))
        input = request.recv(1024).strip()
        if sha1(input).hexdigest()[:6] == prefix:
            break
        request.sendall('invalid PoW, please retry\r\n'.encode('utf-8'))


def menu():
    return """------------------------
Smart Contract Challenge
------------------------
1. Deploy The Challenge 
2. Get Flag
\r\n> """


class ChallengeTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        PoW(self.request)
        self.request.sendall(menu().encode('utf-8'))
        option = self.request.recv(1024).strip()
        try:
            option = int(option)
            if option == 1:
                session_id = random_token()
                self.request.sendall('Your token is: {}\r\n'.format(b64encode(session_id).decode('utf-8')).encode('utf-8'))
                self.request.sendall('Deploy challenge for you...\r\n'.encode('utf-8'))
                address = new_challenge()
                session[session_id] = Web3.toChecksumAddress(address)
                self.request.sendall('OK~ Your address is: {}'.format(address).encode('utf-8'))
            elif option == 2:
                self.request.sendall('Give me your token: \r\n> '.encode('utf-8'))
                token = b64decode(self.request.recv(1024).strip())
                if Web3.isChecksumAddress(session[token]):
                    self.request.sendall(get_flag(session[token]).encode('utf-8'))
                else:
                    self.request.sendall(session[token].encode('utf-8'))
            else:
                raise('')
        except Exception as e:
            print(e)
            self.request.sendall('wrong, bye~~'.encode('utf-8')) 

# main
def main():
    print('Server Listen to: {}:{}'.format(HOST, PORT))
    server = socketserver.ThreadingTCPServer((HOST, PORT), ChallengeTCPHandler) 
    server.serve_forever()


if __name__ == "__main__":
    main()