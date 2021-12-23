from scripts.helpers import get_account
from brownie import interface, config, network


def deposit_weth():
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Received 0.1 wETH")
    return tx


def main():
    deposit_weth()
