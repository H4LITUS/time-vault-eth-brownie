import pytest
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONEMNTS
from brownie import Token, TimeVault, chain, network, accounts, config
from web3 import Web3

DAY = 0
MIN = 3
SEC = 0
LOCK_DURATION = DAY * 86400 + MIN * 60 + SEC


def test_deploy_timevault():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONEMNTS:
        pytest.skip()

    account = get_account()
    token = Token.deploy("Token", "TK", {"from": account})
    beneficiary = accounts.add(config["wallets"]["from_key_2"])
    unlock_time = chain.time() + LOCK_DURATION
    amount = Web3.toWei(0.05, "ether")
    beneficiary_initial_balance = beneficiary.balance()

    time_vault = TimeVault.deploy(unlock_time, beneficiary, token, {"from": account})

    assert time_vault.token() == token
    assert time_vault.beneficiary() == beneficiary
    assert time_vault.funds() == 0
    assert time_vault.unlocked() == False
    assert time_vault.unlockTime() == unlock_time

    time_vault.deposit({"from": account, "value": amount / 2})
    account.transfer(time_vault, amount / 2)
    token.transfer(time_vault, amount, {"from": account})

    assert time_vault.funds() == amount
    assert time_vault.balance() == amount
    assert token.balanceOf(time_vault) == amount

    while not time_vault.unlocked():
        pass

    assert time_vault.withdrawFunds({"from": account})
    assert beneficiary.balance() == amount + beneficiary_initial_balance
    assert time_vault.withdrawTokens({"from": account})
    assert token.balanceOf(beneficiary) == amount
