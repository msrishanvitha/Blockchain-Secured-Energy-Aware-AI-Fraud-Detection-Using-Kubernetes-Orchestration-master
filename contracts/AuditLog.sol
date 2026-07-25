// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AuditLog {
    
    // This struct is enhanced (Item 3)
    struct LogEntry {
        uint256 timestamp;
        string transactionId;
        string nodeRegion;
        bool isFraud;
        int256 aiConfidenceScore; // AI confidence score
        uint256 carbonIntensity; // gCO2eq/kWh
    }

    LogEntry[] public allLogs;

    // This function is enhanced (Item 3)
    function addLog(
        string memory _transactionId,
        string memory _nodeRegion,
        bool _isFraud,
        int256 _aiConfidenceScore,
        uint256 _carbonIntensity
    ) public {
        allLogs.push(
            LogEntry({
                timestamp: block.timestamp,
                transactionId: _transactionId,
                nodeRegion: _nodeRegion,
                isFraud: _isFraud,
                aiConfidenceScore: _aiConfidenceScore,
                carbonIntensity: _carbonIntensity
            })
        );
    }

    // Add read functions (Item 3)
    function getLogCount() public view returns (uint256) {
        return allLogs.length;
    }

    function getLog(uint256 _index) public view returns (LogEntry memory) {
        require(_index < allLogs.length, "Index out of bounds");
        return allLogs[_index];
    }
}
