import json
import web3
import sys
import time
import asyncio

from web3 import Web3, HTTPProvider, TestRPCProvider
from solc import compile_source
from web3.contract import ConciseContract
import requests


# TEST API ACCOUNT INFO
# Private key: a5fd26e449e7068059d4e139465205963d3355ee2a9f45d9e7d4635b4524cda3
# Public key:  a074c22e55610001e52b567f887dddd62b1874981a46d6cf1db0e7f2fba00a91a62576bd96fab6e558a1a05b114d06e92996f14bcf244d3232ffd297fa951856
# Address:     0x85D519832Eee2ea676419F896B6E0A1e83a28CEA

# infura kovan endpoint
HTTP_ENDPOINT = 'https://kovan.infura.io/v3/1da93ca6751b45cdac2af62a4e5b464c'
WSS_ENDPOINT = 'wss://kovan.infura.io/ws/v3/1da93ca6751b45cdac2af62a4e5b464c'

# token address; must be already deployed
# CONTRACT_ADDRESS = '0x492934308E98b590A626666B703A6dDf2120e85e' # local
CONTRACT_ADDRESS = '0x3041EfE098e2cde8420DD16c9fBF5bde630f6168'  # kovan
# '0x731a10897d267e19B34503aD902d0A29173Ba4B1'

# address of API (this thing)
API_ADDRESS = '0x85D519832Eee2ea676419F896B6E0A1e83a28CEA'
API_ADDRESS = Web3.toChecksumAddress(API_ADDRESS.lower())


def getProvider():
    # return TestRPCProvider()
    # httpHost = "http://10.0.0.128"# brock's laptop

    return Web3.HTTPProvider(HTTP_ENDPOINT, request_kwargs={'timeout': 10})


def getWsProvider():
    return Web3.WebsocketProvider(WSS_ENDPOINT)


def ABI():
    return '''
		[
    {
      "constant": false,
      "inputs": [
        {
          "name": "spender",
          "type": "address"
        },
        {
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "approve",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "totalSupply",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "from",
          "type": "address"
        },
        {
          "name": "to",
          "type": "address"
        },
        {
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "transferFrom",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "spender",
          "type": "address"
        },
        {
          "name": "addedValue",
          "type": "uint256"
        }
      ],
      "name": "increaseAllowance",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "owner",
          "type": "address"
        }
      ],
      "name": "balanceOf",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "account",
          "type": "address"
        }
      ],
      "name": "addMinter",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [],
      "name": "renounceMinter",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "spender",
          "type": "address"
        },
        {
          "name": "subtractedValue",
          "type": "uint256"
        }
      ],
      "name": "decreaseAllowance",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "to",
          "type": "address"
        },
        {
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "transfer",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "account",
          "type": "address"
        }
      ],
      "name": "isMinter",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "owner",
          "type": "address"
        },
        {
          "name": "spender",
          "type": "address"
        }
      ],
      "name": "allowance",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "account",
          "type": "address"
        }
      ],
      "name": "MinterAdded",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "account",
          "type": "address"
        }
      ],
      "name": "MinterRemoved",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "from",
          "type": "address"
        },
        {
          "indexed": true,
          "name": "to",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Transfer",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": true,
          "name": "spender",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Approval",
      "type": "event"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "to",
          "type": "address"
        },
        {
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "mint",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
		'''


def getContract(provider=None):
    # get web3 interface
    if (provider == None):
        provider = getProvider()
    w3 = Web3(provider)

    return w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI())


# sends coins from API_ADDRESS to address_receiver
# this means API_ADDRESS must be stocked with coins
def orderCoins(numCoins, address_receiver):
    # get web3 interface
    provider = getProvider()
    w3 = Web3(provider)

    # convert receiver address to checksum address
    RECEIVER_ADDRESS = Web3.toChecksumAddress(address_receiver.lower())

    # read private key from secret file
    keyfile = open('.ethkey', 'r')
    PRIVATE_KEY_API = keyfile.readline().strip('\n')
    keyfile.close()

    # sender account's nonce
    nonce = w3.eth.getTransactionCount(API_ADDRESS)

    # sanity check
    # print ("Contract address: %s" % CONTRACT_ADDRESS, file=sys.stderr)
    # print ("Recipient address: %s" % RECEIVER_ADDRESS, file=sys.stderr)
    # print ("API address: %s" % API_ADDRESS, file=sys.stderr)
    # print ("Nonce: %s" % str(nonce), file=sys.stderr)
    # print ("Coins: %s" % numCoins, file=sys.stderr)

    # convert numCoins to int
    coins = int(numCoins)

    # get contract instance
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI())

    # build transaction
    tx = contract.functions.transfer(RECEIVER_ADDRESS, coins).buildTransaction(
        {'chainId': None,
         'gas': 70000,
         # w3.toWei('1', 'wei'), #TODO: use estimateGas(?)
         'gasPrice': 4,
         'from': API_ADDRESS, 'nonce': nonce,
         }
    )

    # sign tx locally
    signed_tx = w3.eth.account.signTransaction(tx, private_key=PRIVATE_KEY_API)
    result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    return result.hex()


def paymentFilter(contract, customerAddress, block, amount):
    return contract.events.Transfer.createFilter(
        fromBlock=hex(block), argument_filters={'from': customerAddress, 'to': CONTRACT_ADDRESS, 'value': int(amount)})


# return payment logs from infura
# use external filter for efficiency (no recurring garbage collection)
def paymentLogs(customerAddress, block, wsProvider, contract, _filter):
    if (_filter == None):
        filt = paymentFilter(contract, customerAddress, block)
    else:
        filt = _filter

    res = filt.get_all_entries()

    # send it
    return res


# wait for payment confirmation from customerAddress
def handlePayment(customerAddress, amount):
    httpProvider = getProvider()
    wsProvider = getWsProvider()
    contract = getContract(wsProvider)
    w3 = Web3(httpProvider)

    block = w3.eth.blockNumber
    print(block)

    filt = paymentFilter(contract, customerAddress, block, amount)

    payments = []
    while (len(payments) == 0):
        payments = paymentLogs(customerAddress, block,
                               wsProvider, contract, filt)

    print(payments)

    return payments
