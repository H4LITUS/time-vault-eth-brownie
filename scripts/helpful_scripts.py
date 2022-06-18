from brownie import accounts, config, network, chain

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONEMNTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index is not None:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONEMNTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key_1"])


def forward_chain_time(forward_time_by):
    chain.sleep(forward_time_by)
    chain.mine()
