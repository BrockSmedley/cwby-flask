const w3utils = require('web3-utils');

const api_host = "http://172.70.0.2:5000";
const CONTRACT_ADDRESS = "0x492934308E98b590A626666B703A6dDf2120e85e"; // cdev
// "0x731a10897d267e19B34503aD902d0A29173Ba4B1"; // OG CWBY

const startApp = function (web3) {
    // initialize web3

    if (typeof web3 !== 'undefined') {
        web3 = new Web3(web3.currentProvider);
    } else {
        // set the provider you want from Web3.providers
        web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
    }

    console.log("web3 initialized.");
};

// callback function to store value for Stripe dialog
const setAmount = function () {
    var box = document.getElementById("amountInput");
    _amount = parseInt(box.value, 10);
    //console.log("CWBY Tokens: " + _amount);
};

// gets amount entered in textbox
const getAmount = function () {
    // get latest value
    setAmount();
    if (_amount > 0) {
        return _amount;
    } else {
        return 0;
    }
};

const setAddress = function () {
    var box = document.getElementById("addressInput");
    _address = box.value;
    if (!isAddress(_address)) {
        console.log("Invalid address: " + _address);
    } else {
        console.log("Address is valid:" + _address);
    }
    $("#addressInput").redraw();
};

const getAddress = function () {
    // get latest value just in case
    setAddress();
    if (isAddress(_address)) {
        return _address;
    } else {
        return '0x0';
    }
};

const getAbi = function () {
    return [{
            "constant": false,
            "inputs": [{
                    "name": "_spender",
                    "type": "address"
                },
                {
                    "name": "_value",
                    "type": "uint256"
                }
            ],
            "name": "approve",
            "outputs": [{
                "name": "success",
                "type": "bool"
            }],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{
                "name": "",
                "type": "uint256"
            }],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{
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
            "outputs": [{
                "name": "success",
                "type": "bool"
            }],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [{
                "name": "_owner",
                "type": "address"
            }],
            "name": "balanceOf",
            "outputs": [{
                "name": "balance",
                "type": "uint256"
            }],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{
                    "name": "_to",
                    "type": "address"
                },
                {
                    "name": "_value",
                    "type": "uint256"
                }
            ],
            "name": "transfer",
            "outputs": [{
                "name": "success",
                "type": "bool"
            }],
            "payable": false,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [{
                    "name": "_owner",
                    "type": "address"
                },
                {
                    "name": "_spender",
                    "type": "address"
                }
            ],
            "name": "allowance",
            "outputs": [{
                "name": "remaining",
                "type": "uint256"
            }],
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
            "inputs": [{
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
            "inputs": [{
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
    ];
}

const getPrice = function () {
    return 420;
};

const getContractAddress = function () {
    return CONTRACT_ADDRESS;
    // TODO: pull this from oracle
    /*
    const Http = new XMLHttpRequest();
    const url = api_host + "/_contractAddress";
    Http.open("GET", url);
    Http.send();
    
    Http.onreadystatechange = (e) => {
        return Http.responseText;
    }
    */
}

// spend CWBY coins from user account
var spendTokens = function (cost) {
    showOverlay();
    // get user address
    const address = web3.eth.defaultAccount;
    const _cost = parseInt(cost);

    // contract address
    //const Contract = require('web3-eth-contract');
    var _contract = web3.eth.contract(getAbi(), {"from": address});
    var tokens = _contract.at(getContractAddress());

    // query user balance
    var balance = -1;
    return new Promise(resolve => tokens.balanceOf(address, function (error, result) {
        if (!error){
            console.log("balance: " + result);
            console.log("Cost: " + cost + " CWBY");
            balance = result;
            // attempt transaction
            if (balance >= _cost) {
                // spend the tokens
                resolve (tokens.transfer(_to=getContractAddress(), _value=_cost, function(error, result){
                    if (!error){
                        // log tx hash if transaction succeeded
                        hideOverlay();
                        console.log("txResult: " + result);
                        return result;
                    }
                    else {
                        console.error(error);
                        return 0;
                    }
                }));
            }
            else {
                console.log("Balance insufficient.");
                alert("Insufficient balance. Buy more CWBY to purchase this item!");
                return 0;
            }
        }
        else{
            console.error(error);
        }
    }));

    // return 0 if tx failed
    return 0;
}

window.startApp = startApp;
window.setAmount = setAmount;
window.setAddress = setAddress;
window.getAmount = getAmount;
window.getAddress = getAddress;
window.w3utils = w3utils;
window.getPrice = getPrice;
window.spendTokens = spendTokens;
window.getContractAddress = getContractAddress;
window.getAbi = getAbi;