from web3 import Web3
import json
from pathlib import Path

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
print(BASE_DIR)

def get_onchain_price_redstone(price_feed, config):
    # Instantiate the contract
    mainnet_config = next(chain for chain in config["chains"] if chain["name"] == "arbitrum")
    mainnet_web3 = Web3(Web3.HTTPProvider(mainnet_config["nodeURL"]))
    if not mainnet_web3.is_connected():
        raise ConnectionError("Failed to connect to Arbitrum mainnet")
    
    address = price_feed["address"]
     #on chain price oracle
    abi_path = BASE_DIR / 'abi' / 'RedStoneAbi.json'
    with open(abi_path, "r") as redstone_abi_file:
        redstone_abi = json.load(redstone_abi_file)

    redstone_contract = mainnet_web3.eth.contract(address=address, abi=redstone_abi)

    # Call the specified function
    function_name = price_feed["get_latest_price_function"]
    price_index = price_feed["price_index"]
    
    latest_round_data = redstone_contract.functions[function_name]().call()
    decimals = price_feed["decimals"]

    # Return the price
    return latest_round_data[price_index] / (10**decimals)

# Example usage in main.py:
# latest_weeth_eth_price = get_onchain_price(web3, perpetual_config["priceFeed"])
