// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FraudLog
 * @dev A smart contract to log green energy transactions and flag potential fraud.
 * It now includes an event to notify listeners when a new record is added.
 */
contract FraudLog {
    
    // An event is a signal the contract emits. Applications can listen for these.
    // This event signals that a new record was successfully added to the blockchain.

    struct FraudRecord {
        string transactionID;
        bool isFraudulent;
        string region;
        string energySource;
        uint256 carbonSaved;
        uint256 timestamp;
    }

    FraudRecord[] public records;

    /**
     * @dev Adds a new transaction record to the blockchain.
     * Emits a RecordAdded event upon successful addition.
     */
    function addRecord(
        string memory _transactionID,
        bool _isFraudulent,
        string memory _region,
        string memory _energySource,
        uint256 _carbonSaved
    ) public {
        // The new record is added to the storage array
        records.push(FraudRecord({
            transactionID: _transactionID,
            isFraudulent: _isFraudulent,
            region: _region,
            energySource: _energySource,
            carbonSaved: _carbonSaved,
            timestamp: block.timestamp
        }));

        // After adding the record, the contract emits the event to notify the outside world.
        // We pass the index of the newly added record (records.length - 1).
        emit RecordAdded(
            records.length - 1,
            _transactionID,
            _region,
            _carbonSaved,
            block.timestamp
        );
    }

    /**
     * @dev Returns the total number of records stored.
     * @return A uint256 representing the total count.
     */
    function getTotalRecords() public view returns (uint256) {
        return records.length;
    }

    /**
     * @dev Retrieves a specific record by its index.
     * @param index The index of the record to retrieve.
     * @return A tuple containing all the fields of the FraudRecord struct.
     */
    function getRecord(uint256 index) public view returns (
        string memory,
        bool,
        string memory,
        string memory,
        uint256,
        uint256
    ) {
        require(index < records.length, "FraudLog: Invalid record index");
        FraudRecord storage rec = records[index];
        return (
            rec.transactionID,
            rec.isFraudulent,
            rec.region,
            rec.energySource,
            rec.carbonSaved,
            rec.timestamp
        );
    }
}