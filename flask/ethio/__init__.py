import json
import web3
import sys
import time

from web3 import Web3, HTTPProvider, TestRPCProvider
from solc import compile_source
from web3.contract import ConciseContract


# TEST API ACCOUNT INFO
# Private key: a5fd26e449e7068059d4e139465205963d3355ee2a9f45d9e7d4635b4524cda3
# Public key:  a074c22e55610001e52b567f887dddd62b1874981a46d6cf1db0e7f2fba00a91a62576bd96fab6e558a1a05b114d06e92996f14bcf244d3232ffd297fa951856
#Address:     0x85D519832Eee2ea676419F896B6E0A1e83a28CEA

def compileTestContract():
    # Solidity source code
    contract_src = '''
		pragma solidity ^0.4.0;

		contract Greeter {
				string public greeting;

				function Greeter(){
						greeting = "Howdy";
				}

				function setGreeting(string _greeting) public {
						greeting = _greeting;
				}

				function greet() constant returns (string) {
						return greeting;
				}
		}
		'''

    return compile_source(contract_src)

# compiles and deploys a test contract
# only works on testRPC b/c transactions need to be signed


def buildTestContract():
    PROVIDER = TestRPCProvider()

    compiled_sol = compileTestContract()
    contract_io = compiled_sol['<stdin>:Greeter']

    # web3.py instance
    w3i = Web3(PROVIDER)

    # instantiate and deploy contract
    contract = w3i.eth.contract(
        abi=contract_io['abi'], bytecode=contract_io['bin'])

    # get tx hash from deployed contract
    tx_hash = contract.deploy(
        transaction={'from': w3i.eth.accounts[0], 'gas': 420000})

    # get tx receipt from deployed contract
    tx_receipt = w3i.eth.getTransactionReceipt(tx_hash)
    contract_address = tx_receipt['contractAddress']

    # contract instance in concise mode
    abi = contract_io['abi']
    contract_instance = w3i.eth.contract(
        address=contract_address, abi=abi, ContractFactoryClass=ConciseContract)

    # getters & setters for web3.eth.contract object
    print('Contract value: {}'.format(contract_instance.greet()))
    contract_instance.setGreeting(
        'd\'herroo', transact={'from': w3i.eth.accounts[0]})
    print('Setting new greeting')
    return('Contract value: {}'.format(contract_instance.greet()))


# TODO: Implement parity host in Docker; don't expose this to host network in prod!
def getProvider(host=None):
    # return TestRPCProvider()
    # httpHost = "http://10.0.0.128"# brock's laptop
    if (host):
        httpHost = host
    else:
        httpHost = "http://172.70.0.3"
    return Web3.HTTPProvider(httpHost+":8545", request_kwargs={'timeout': 10})


def abi():
    return '''
		[
	{
		"constant": false,
		"inputs": [
			{
				"name": "_spender",
				"type": "address"
			},
			{
				"name": "_value",
				"type": "uint256"
			}
		],
		"name": "approve",
		"outputs": [
			{
				"name": "success",
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
				"name": "_from",
				"type": "address"
			},
			{
				"name": "_to",
				"type": "address"
			},
			{
				"name": "_value",
				"type": "uint256"
			}
		],
		"name": "transferFrom",
		"outputs": [
			{
				"name": "success",
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
				"name": "_owner",
				"type": "address"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"name": "balance",
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
				"name": "_to",
				"type": "address"
			},
			{
				"name": "_value",
				"type": "uint256"
			}
		],
		"name": "transfer",
		"outputs": [
			{
				"name": "success",
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
				"name": "_owner",
				"type": "address"
			},
			{
				"name": "_spender",
				"type": "address"
			}
		],
		"name": "allowance",
		"outputs": [
			{
				"name": "remaining",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"name": "_from",
				"type": "address"
			},
			{
				"indexed": true,
				"name": "_to",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "_value",
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
				"name": "_owner",
				"type": "address"
			},
			{
				"indexed": true,
				"name": "_spender",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "_value",
				"type": "uint256"
			}
		],
		"name": "Approval",
		"type": "event"
	}
]
		'''


def orderCoins(numCoins, address_receiver, provider=None):
    # get web3 interface
    provider = getProvider(provider)
    w3 = Web3(provider)

    # convert receiver address to checksum address
    RECEIVER_ADDRESS = Web3.toChecksumAddress(address_receiver.lower())

    # address of token
    CONTRACT_ADDRESS = '0x731a10897d267e19B34503aD902d0A29173Ba4B1'

    # read private key from secret file
    keyfile = open('.ethkey', 'r')
    PRIVATE_KEY_API = keyfile.readline().strip('\n')
    keyfile.close()

    # address of API (this thing)
    API_ADDRESS = '0x85D519832Eee2ea676419F896B6E0A1e83a28CEA'
    API_ADDRESS = Web3.toChecksumAddress(API_ADDRESS.lower())

    # sender account's nonce
    nonce = w3.eth.getTransactionCount(API_ADDRESS)

    # sanity check
    #print ("Contract address: %s" % CONTRACT_ADDRESS, file=sys.stderr)
    #print ("Recipient address: %s" % RECEIVER_ADDRESS, file=sys.stderr)
    #print ("API address: %s" % API_ADDRESS, file=sys.stderr)
    #print ("Nonce: %s" % str(nonce), file=sys.stderr)
    #print ("Coins: %s" % numCoins, file=sys.stderr)

    # convert numCoins to int
    coins = int(numCoins)

    # get contract instance
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi())

    # build transaction
    tx = contract.functions.transfer(RECEIVER_ADDRESS, coins).buildTransaction(
        {'chainId': None,
         'gas': 70000,
         # w3.toWei('1', 'wei'), #TODO: use estimateGas(?)
         'gasPrice': 1,
         'value': w3.toHex(w3.toWei('0', 'ether')),
         'from': API_ADDRESS, 'nonce': nonce,
         }
    )
    #print (tx, file=sys.stderr)

    # sign tx locally
    signed_tx = w3.eth.account.signTransaction(tx, private_key=PRIVATE_KEY_API)
    result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    return result.hex()
