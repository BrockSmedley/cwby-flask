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

// send request to API server with CC info and ETH address
function requestTokens(){
    // get user address
    var userAddress = web3.eth.defaultAccount;
    console.log("user address: " + userAddress);
    
    // send request to API server
    HTTP.open("GET", URL);
    HTTP.send();

    HTTP.onreadystatechange= (e) => {
        if (HTTP.responseText && HTTP.responseText != ''){
            console.log("API Response:\n" + HTTP.responseText);
        }
    }

    console.log("Tokens requested. Awaiting API server response.");
}