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


def get_borrowable_data(lending_pool, account):
    # https://docs.aave.com/developers/the-core-protocol/lendingpool#getuseraccountdata
    (
        total_collateral_eth_wei,
        total_debt_eth_wei,
        available_borrows_eth_wei,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth_wei, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth_wei, "ether")
    available_borrows_eth = Web3.fromWei(available_borrows_eth_wei, "ether")

    print(f"You have {total_collateral_eth} worth of ETH to deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed")
    print(f"You can borrow {available_borrows_eth} worth of ETH")
    return (float(available_borrows_eth), float(total_debt_eth))


def main():
    print(f"In network {network.show_active()}")
    account = get_account()
    weth_address = config["networks"][network.show_active()]["weth_token"]
    if is_forked_local(network.show_active()):
        deposit_weth()
    # Get Lending Pool
    lending_pool = get_lending_pool()
    # Approve ERC20 tokens
    approve_erc20(weth_address, lending_pool.address, AMOUNT, account)
    print(lending_pool)
    # Deposit to lending pool
    deposit_lending_pool(lending_pool, weth_address, AMOUNT, account)
    # Get borrowable data
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
