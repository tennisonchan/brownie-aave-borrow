from scripts.helpers import get_account, is_forked_local
from scripts.get_weth import deposit_weth
from brownie import network, config, interface


def aave_borrow():
    account = get_account
    weth_address = config["networks"][network.show_active()]["weth_token"]
    if is_forked_local(network.show_active()):
        deposit_weth()


def get_lending_pool():
    # ABI
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        # Address
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    # Address
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)

    return lending_pool


def main():
    account = get_account
    weth_address = config["networks"][network.show_active()]["weth_token"]
    if is_forked_local(network.show_active()):
        deposit_weth()
    lending_pool = get_lending_pool()
    print(lending_pool)
