document.addEventListener('DOMContentLoaded', () => {
    const logForm = document.getElementById('logForm');
    const logsContainer = document.getElementById('logsContainer');
    const API_URL = 'http://localhost:3000'; // Your server's address

    // Function to fetch and display all logs
    async function fetchLogs() {
        const response = await fetch(`${API_URL}/logs`);
        const data = await response.json();

        // NOTE: This assumes your /logs endpoint returns the full records.
        // You will need to update your server.js for this to work!
        logsContainer.innerHTML = ''; // Clear old logs
        data.records.forEach(log => {
            const logElement = document.createElement('p');
            logElement.textContent = `ID: ${log.transactionID}, Region: ${log.region}, Carbon Saved: ${log.carbonSaved}`;
            logsContainer.appendChild(logElement);
        });
    }

    // Function to handle form submission
    logForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent page reload

        const newLog = {
            transactionID: document.getElementById('txID').value,
            isFraudulent: false, // Or add a checkbox for this
            region: document.getElementById('region').value,
            energySource: document.getElementById('energySource').value,
            carbonSaved: parseInt(document.getElementById('carbonSaved').value)
        };

        await fetch(`${API_URL}/log`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newLog)
        });

        fetchLogs(); // Refresh the list after submitting
        logForm.reset();
    });

    fetchLogs(); // Load logs when the page first opens
});