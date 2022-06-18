from time import time
import brownie
import pytest
from scripts.helpful_scripts import (
    get_account,
    LOCAL_BLOCKCHAIN_ENVIRONEMNTS,
    forward_chain_time,
)
from brownie import Token, TimeVault, chain, network
from scripts.deploy import deploy_token
from web3 import Web3

DAY = 0
MIN = 10
SEC = 0
LOCK_DURATION = DAY * 86400 + MIN * 60 + SEC


def test_deploy_timevault():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMNTS:
        pytest.skip()

    account = get_account()
    token = deploy_token()
    beneficiary = get_account(index=1)

    unlock_time = chain.time() + LOCK_DURATION

    with brownie.reverts("Unlock time cannot be before the current time"):
        TimeVault.deploy(chain.time() - 1, beneficiary, token, {"from": account})

    with brownie.reverts("Beneficiary cannot be address 0"):
        TimeVault.deploy(unlock_time, brownie.ZERO_ADDRESS, token, {"from": account})

    time_vault = TimeVault.deploy(unlock_time, beneficiary, token, {"from": account})

    assert time_vault.unlockTime() == unlock_time
    assert time_vault.token() == token
    assert time_vault.beneficiary() == beneficiary
    assert time_vault.funds() == 0


def test_timevault_unlock():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMNTS:
        pytest.skip()

    account = get_account()
    token = deploy_token()

    unlock_time = chain.time() + LOCK_DURATION
    time_vault = TimeVault.deploy(unlock_time, account, token, {"from": account})

    assert time_vault.unlocked() == False

    forward_chain_time(LOCK_DURATION - 1)
    assert time_vault.unlocked() == False

    forward_chain_time(1)
    assert time_vault.unlocked() == True


def test_timevault_withdraw_funds():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMNTS:
        pytest.skip()

    account = get_account()
    token = deploy_token()
    beneficiary = get_account(index=1)

    unlock_time = chain.time() + LOCK_DURATION
    time_vault = TimeVault.deploy(unlock_time, beneficiary, token, {"from": account})

    amount = Web3.toWei(2, "ether")
    time_vault.deposit({"from": account, "value": amount / 2})
    account.transfer(time_vault, amount / 2)

    assert time_vault.balance() == amount

    initial_balance = beneficiary.balance()

    with brownie.reverts("Vault Locked: Cannot be accessed before the unlock date"):
        time_vault.withdrawFunds({"from": account})

    forward_chain_time(LOCK_DURATION)

    assert time_vault.withdrawFunds({"from": account})
    assert time_vault.balance() == 0
    assert beneficiary.balance() == initial_balance + amount


def test_timevault_withdraw_token():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMNTS:
        pytest.skip()

    account = get_account()
    token = deploy_token()
    beneficiary = get_account(index=1)

    unlock_time = chain.time() + LOCK_DURATION
    time_vault = TimeVault.deploy(unlock_time, beneficiary, token, {"from": account})

    amount = Web3.toWei(2, "ether")
    token.transfer(time_vault, amount, {"from": account})

    assert token.balanceOf(time_vault) == amount
    assert token.balanceOf(beneficiary) == 0

    with brownie.reverts("Vault Locked: Cannot be accessed before the unlock date"):
        time_vault.withdrawTokens({"from": account})

    forward_chain_time(LOCK_DURATION)

    assert time_vault.withdrawTokens({"from": account})
    assert token.balanceOf(beneficiary) == amount
