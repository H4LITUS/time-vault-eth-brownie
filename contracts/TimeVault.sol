// SPDX-License-Identifier: MIT

pragma solidity ^0.8.13;

import "./Token.sol";

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract TimeVault {
    uint256 public creationTime;
    uint256 public unlockTime;
    uint256 public funds;
    address payable public beneficiary;

    IERC20 public token;

    event FundsDeposited(address indexed depositor, uint256 amount);
    event FundsWithdrawn(
        address indexed caller,
        address indexed beneficiary,
        uint256 amount
    );
    event TokensWithdrawn(
        address indexed caller,
        address indexed beneficiary,
        uint256 amount
    );

    modifier isUnlocked() {
        require(
            unlocked(),
            "Vault Locked: Cannot be accessed before the unlock date"
        );
        _;
    }

    constructor(
        uint256 _unlockTime,
        address _beneficiary,
        address _token
    ) {
        require(
            _unlockTime > block.timestamp,
            "Unlock time cannot be before the current time"
        );
        require(_beneficiary != address(0), "Beneficiary cannot be address 0");

        creationTime = block.timestamp;
        unlockTime = _unlockTime;
        beneficiary = payable(_beneficiary);
        token = IERC20(_token);
    }

    fallback() external payable {
        deposit();
    }

    function deposit() public payable {
        require(msg.value > 0);
        funds = funds + msg.value;
        emit FundsDeposited(msg.sender, msg.value);
    }

    function withdrawFunds() public isUnlocked returns (bool) {
        require(funds > 0, "You don't have any funds");
        uint256 amount = funds;
        funds = 0;
        (bool sent, ) = beneficiary.call{value: amount}("");
        emit FundsWithdrawn(msg.sender, beneficiary, amount);
        return sent;
    }

    function withdrawTokens() public isUnlocked returns (bool) {
        uint256 amount = token.balanceOf(address(this));
        bool sent = token.transfer(beneficiary, amount);
        emit TokensWithdrawn(msg.sender, beneficiary, amount);
        return sent;
    }

    function unlocked() public view returns (bool) {
        return block.timestamp >= unlockTime;
    }
}
