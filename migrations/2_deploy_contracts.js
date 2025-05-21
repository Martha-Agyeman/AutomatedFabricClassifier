const GarmentScanner = artifacts.require("../contracts/GarmentScanner.sol");

module.exports = function (deployer) {
  deployer.deploy(GarmentScanner);
};