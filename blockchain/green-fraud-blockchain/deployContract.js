const Web3 = require("web3");
const fs = require("fs");

// *** This line must be a simple string: "http://127.0.0.1:8545" ***
const web3 = new Web3("http://127.0.0.1:7545"); 
const abi = JSON.parse(fs.readFileSync("./abi.json"));
const bytecode = '0x' + fs.readFileSync('./bytecode.txt').toString().trim(); 

async function deploy() {
    const accounts = await web3.eth.getAccounts();
    console.log("Deploying from:", accounts[0]);

    const contract = new web3.eth.Contract(abi);
    const deployed = await contract
        .deploy({ data: bytecode })
        .send({ from: accounts[0], gas: 3000000 });

    const newAddress = deployed.options.address;
    
    // Writes the new address to a file for server.js to read
    fs.writeFileSync('./contractAddress.txt', newAddress);
    
    console.log("Contract deployed at:", newAddress);
    console.log("Address saved to contractAddress.txt");
}

deploy().catch(console.error); 