import json
import web3

from web3 import Web3, HTTPProvider, TestRPCProvider
from solc import compile_source
from web3.contract import ConciseContract

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

compiled_sol = compile_source(contract_src)
contract_io = compiled_sol['<stdin>:Greeter']

# web3.py instance
w3 = Web3(TestRPCProvider())

# instantiate and deploy contract
contract = w3.eth.contract(abi=contract_io['abi'], bytecode=contract_io['bin'])

# get tx hash from deployed contract
tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0], 'gas': 420000})

# get tx receipt from deployed contract
tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
contract_address = tx_receipt['contractAddress']

# contract instance in concise mode
abi = contract_io['abi']
contract_instance = w3.eth.contract(address=contract_address, abi=abi, ContractFactoryClass=ConciseContract)

# getters & setters for web3.eth.contract object
print('Contract value: {}'.format(contract_instance.greet()))
contract_instance.setGreeting('d\'herroo', transact={'from': w3.eth.accounts[0]})
print('Setting new greeting')
print('Contract value: {}'.format(contract_instance.greet()))