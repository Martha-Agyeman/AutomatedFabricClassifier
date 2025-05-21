// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GarmentScanner {
    struct ScanData {
        string scanId;
        uint256 timestamp;
        string fabricType;
        string garmentType;
        uint256 conditionScore;
        string recommendation;
    }
    
    mapping(string => ScanData) public scans;
    string[] public scanIds;
    
    event ScanStored(string indexed scanId, uint256 timestamp);
    
    function storeScanData(
        string memory _scanId,
        uint256 _timestamp,
        string memory _fabricType,
        string memory _garmentType,
        uint256 _conditionScore,
        string memory _recommendation
    ) public {
        scans[_scanId] = ScanData(
            _scanId,
            _timestamp,
            _fabricType,
            _garmentType,
            _conditionScore,
            _recommendation
        );
        scanIds.push(_scanId);
        emit ScanStored(_scanId, _timestamp);
    }
    
    function getScanCount() public view returns (uint256) {
        return scanIds.length;
    }
    
    function getScanById(string memory _scanId) public view returns (
        string memory,
        uint256,
        string memory,
        string memory,
        uint256,
        string memory
    ) {
        ScanData memory data = scans[_scanId];
        return (
            data.scanId,
            data.timestamp,
            data.fabricType,
            data.garmentType,
            data.conditionScore,
            data.recommendation
        );
    }
}