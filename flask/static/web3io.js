const HTTP = new XMLHttpRequest();
const HOST = 'http://localhost:5000'
const PATH = '/js/egg'
const URL = HOST + PATH

const Web3 = require('web3');
var web3;

function startApp(web3){
    // initialize web3
    
    if (typeof web3 !== 'undefined') {
        web3 = new Web3(web3.currentProvider);
    } else {
        // set the provider you want from Web3.providers
        web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
    }

    console.log("web3 initialized.");
}

// use regex to test for valid address format
function isAddress(address){
    var rgx = new RegExp('^0x[A-Za-z0-9]{40}$');
    return rgx.test(address);
}