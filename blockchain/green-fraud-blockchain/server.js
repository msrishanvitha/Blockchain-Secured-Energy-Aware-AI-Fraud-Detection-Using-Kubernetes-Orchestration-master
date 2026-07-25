const express = require('express');
const Web3 = require('web3');
const fs = require('fs');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// --- Configuration ---
// CORRECTED URL: Must be a plain string
const WEB3_PROVIDER = process.env.RPC_URL || 'http://127.0.0.1:7545';
const web3 = new Web3(WEB3_PROVIDER);
const abi = JSON.parse(fs.readFileSync('./abi.json', 'utf8'));

let CONTRACT_ADDRESS;

try {
    CONTRACT_ADDRESS = fs.readFileSync('./contractAddress.txt', 'utf8').trim();
    if (!web3.utils.isAddress(CONTRACT_ADDRESS)) {
        throw new Error("Invalid address format.");
    }
} catch (e) {
    console.error("CRITICAL ERROR: Failed to load contractAddress.txt. Did you run deployContract.js?");
    CONTRACT_ADDRESS = '0x0';
}

const contract = new web3.eth.Contract(abi, CONTRACT_ADDRESS);

// POST /log → write a fraud entry (Remains unchanged and confirmed working)
app.post('/log', async (req, res) => {
    try {
        if (CONTRACT_ADDRESS === '0x0') {
            return res.status(500).json({ error: "Server is not initialized. Please deploy the contract first." });
        }
        
        const { transactionID, isFraudulent, region, energySource, carbonSaved } = req.body;
        const accounts = await web3.eth.getAccounts();

        const receipt = await contract.methods
            .addRecord(transactionID, isFraudulent, region, energySource, carbonSaved || 0)
            .send({ from: accounts[0], gas: 3000000 });
            
        res.json({ status: 'ok', txHash: receipt.transactionHash });
        
    } catch (err) {
        console.error("POST /log error:", err.toString());
        res.status(500).json({ error: "Failed to post transaction. Ensure Ganache is running." });
    }
});


// GET /logs → DEBUGGING VERSION: ONLY READ TOTAL COUNT
// In server.js, REPLACE your current app.get('/logs', ...) with this:
app.get('/logs', async (req, res) => {
    try {
        const totalRecords = await contract.methods.getTotalRecords().call();
        const allRecords = [];

        for (let i = 0; i < totalRecords; i++) {
            const record = await contract.methods.getRecord(i).call();
            allRecords.push({
                transactionID: record[0],
                isFraudulent: record[1],
                region: record[2],
                energySource: record[3],
                carbonSaved: Number(record[4]),
                timestamp: Number(record[5])
            });
        }
        res.json({ records: allRecords });

    } catch (err) {
        console.error("GET /logs error:", err.toString());
        res.status(500).json({ error: "Failed to retrieve records." });
    }
});


app.get('/', (req, res) => res.send('Green Fraud Blockchain backend is up'));

const PORT = 3000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));