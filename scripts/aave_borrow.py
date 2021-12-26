from scripts.helpers import get_account, is_forked_local
from scripts.get_weth import deposit_weth
from brownie import network, config, interface
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")


def aave_borrow():
    print(f"In network {network.show_active()}")
    account = get_account()
    weth_address = config["networks"][network.show_active()]["weth_token"]
    if is_forked_local(network.show_active()):
        deposit_weth()
    # Get Lending Pool
    lending_pool = get_lending_pool()
    print(lending_pool)
    # Deposit to lending pool
    deposit_lending_pool(lending_pool, weth_address, AMOUNT, account)
    # Get borrowable data
    borrowable_eth, _ = get_borrowable_data(lending_pool, account)

    dai_eth_price = get_asset_price_feed(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )

    # borrowable dai => 1/dai-eth * borrowable eth * 95%
    amount_dai_to_borrow = (1 / dai_eth_price) * borrowable_eth * 0.95
    print(amount_dai_to_borrow)
    dai_address = config["networks"][network.show_active()]["dai_token"]

    borrow_from_lending_pool(
        lending_pool,
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        "stable",
        account,
    )


def get_rate_mode_code(rate_mode):
    return 1 if rate_mode == "stable" else 2


def borrow_from_lending_pool(
    lending_pool, asset, amount_wei, rateMode, account, referralCode=0
):
    # https://docs.aave.com/developers/the-core-protocol/lendingpool#borrow
    borrow_tx = lending_pool.borrow(
        asset,
        amount_wei,
        get_rate_mode_code(rateMode),
        referralCode,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)


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
    # Approve ERC20 tokens
    approve_erc20(address, lending_pool.address, amount, account)
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


def get_asset_price_feed(price_feed_address):
    price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = price_feed.latestRoundData()[1]
    latest_price_from_wei = Web3.fromWei(latest_price, "ether")
    print(f"The latest Dai / Eth is {latest_price_from_wei}")
    return float(latest_price_from_wei)


def main():
    aave_borrow()
