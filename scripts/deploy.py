from scripts.helpful_scripts import get_account
from brownie import Token, TimeVault, network, chain, config, accounts
import time
from web3 import Web3

DAY = 0
MIN = 5
SEC = 0
LOCK_DURATION = DAY * 86400 + MIN * 60 + SEC


def deploy_token():
    account = get_account()
    token = Token.deploy(
        "Token",
        "TK",
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed Token")
    return token


def deploy_timevault():
    account = get_account()
    token = deploy_token()
    unlock_time = chain.time() + LOCK_DURATION
    beneficiary = accounts.add(config["wallets"]["from_key_2"])

    time_vault = TimeVault.deploy(
        unlock_time,
        account,
        token,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed TimeVault")

    print_timevault(token, time_vault)

    amount = Web3.toWei(0.01, "ether")
    tx = token.transfer(time_vault, amount)
    tx.wait(1)
    print("Token transferred\n")

    tx = time_vault.deposit({"from": account, "value": amount})
    tx.wait(1)
    print("Eth transferred\n")

    print_timevault(token, time_vault)

    print(f"Account balance of {account.address}: {account.balance()} ETH")
    print(f"Token Balance of {account.address}: {token.balanceOf(account)}\n")

    print("Waiting......................")
    while not time_vault.unlocked():
        pass
    print("Vault unlocked...............\n")

    tx = time_vault.withdrawFunds({"from": account})
    tx.wait(1)
    tx = time_vault.withdrawTokens({"from": account})
    tx.wait(1)

    print(f"Account balance of {account.address}: {account.balance()} ETH")
    print(f"Token Balance of {account.address}: {token.balanceOf(account)}\n")

    print_timevault(token, time_vault)


def print_timevault(token, time_vault):
    token_balance = token.balanceOf(time_vault)
    timevault_eth = time_vault.balance()
    unlock_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(time_vault.unlockTime())
    )
    print(
        f"TimeVault details: \nTokens: {token_balance} TK \nEther: {timevault_eth} ETH \nUnlock Time: {unlock_time}\n"
    )


def main():
    deploy_timevault()
