from scripts.helpers import get_account, is_forked_local
from scripts.get_weth import deposit_weth
from brownie import network, config, interface
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")


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


def approve_erc20(erc20_address, sender, amount, account):
    print("Approving ERC20 token ...")
    # ABI
    # Address
    erc20_contract = interface.IERC20(erc20_address)
    tx = erc20_contract.approve(sender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def deposit_lending_pool(lending_pool, address, amount, account):
    print("Depositing ...")
    tx = lending_pool.deposit(address, amount, account, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    return tx


def main():
    print(f"In network {network.show_active()}")
    account = get_account()
    weth_address = config["networks"][network.show_active()]["weth_token"]
    if is_forked_local(network.show_active()):
        deposit_weth()
    lending_pool = get_lending_pool()
    # Approve ERC20 tokens
    approve_erc20(weth_address, lending_pool.address, AMOUNT, account)
    print(lending_pool)
    # Deposit to lending pool
    deposit_lending_pool(lending_pool, weth_address, AMOUNT, account)
