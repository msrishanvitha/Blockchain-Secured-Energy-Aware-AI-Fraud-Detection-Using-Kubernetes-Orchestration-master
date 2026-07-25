const Web3 = require('web3');

const web3 = new Web3('http://127.0.0.1:8545');

(async () => {
  try {
    const accounts = await web3.eth.getAccounts();
    console.log('Connected! Accounts:', accounts);
  } catch (err) {
    console.error('Connection error:', err);
  }
})();
