import json 
from web3 import Web3

from getOffchainPriceHermes import get_offchain_price, get_vaa_from_pyth, get_publish_time 
from getOnchainPriceRedStone import get_onchain_price_redstone
from getOnchainPriceAngle import get_stusd_to_usdc_price

#helper functions:
#1. helper function to convert to required format
def abdk64x64_conversion(number):
    # Convert a floating-point number to ABDK64x64 format
    return int(number * 2**64)
#2. get prices function
def get_prices(perpetual_id, config):
    #fetch the prices depending on symbol (on or off chain or both)
    def fetch_price(symbol, config):
     offchain_price_config = config["priceFeeds"]["offChain"]["feeds"]
     on_chain_price_config = config["priceFeeds"]["onChain"]
     if not any (part in ("WEETH", "STUSD")for part in symbol.split("-")):
          off_chain_price = get_offchain_price(offchain_price_config[symbol]["id"], config)
          return off_chain_price
     
     elif any (part in ("WEETH") for part in symbol.split("-")):
          on_chain_price = get_onchain_price_redstone(on_chain_price_config[symbol], config)
          return on_chain_price
     
     else:
          on_chain_price = get_stusd_to_usdc_price(config)
          return on_chain_price  
     
    #the price construction logic
    perpetual_config = next(p for p in config["perpetuals"] if p["id"] == perpetual_id)
    # Initialize results dictionary
    prices = {}

    # Process s2 and s3 entries
    for key in ["s2", "s3"]:
        symbol_entries = perpetual_config[key]
        price = 1
        price_name = "" #better than none to build up the string
        # Iterate through the symbol entries and apply operations
        for i in range(0, len(symbol_entries), 2):  # Step by 2 to skip over symbols after operations
            operation = symbol_entries[i]
            symbol = symbol_entries[i+1]
            
            fetched_price = fetch_price(symbol, config)

            if operation == "/":
                price /= fetched_price
                if not price_name: #"" in python is considered false!
                    price_name = symbol.split("-")[1] + "-" + symbol.split("-")[0]
                else:
                    price_name = price_name.split("-")[1] + "-" + symbol.split("-")[0]
            
            elif operation == "*":
                price *= fetched_price
                if not price_name:
                    price_name = symbol
                else:
                    price_name = price_name.split("-")[0] + "-" + symbol.split("-")[1]

            else:
                raise ValueError(f"Unrecognized operation: {operation}")
    
        # Save the calculated price
        prices[key] = (price_name,price)
    
    return prices["s2"], prices["s3"]

#3. connect to blockchain
def connect_to_blockchain(chain_name, config):
    chain_config = next(chain for chain in config["chains"] if chain["name"] == chain_name)
    web3 = Web3(Web3.HTTPProvider(chain_config["nodeURL"])) 
    if web3.is_connected:
        print(f"Connected successfully to {chain_config['name']}")
        return web3
    else:
        raise ConnectionError(f"Failed to connect to {chain_config['name']}")
#4. identify and liquidate positions
def liquidate_positions(perpetual_id, config, web3, chain_name):
    """Fetch and liquidate positions for a given perpetual"""
    
    address = next(chain for chain in config["chains"] if chain["name"] == chain_name)["proxyAddr"]
    with open("IPerpetualManager.json") as proxy_abi_file:
        proxy_abi = json.load(proxy_abi_file)
    
    perpetual_contract = web3.eth.contract(address=address, abi=proxy_abi)
    price1, price2 = get_prices(perpetual_id, config)

    liquidatable_accounts = perpetual_contract.functions.getLiquidatableAccounts(
        perpetual_id, [abdk64x64_conversion(price1[1]), abdk64x64_conversion(price2[1])]
    ).call()

    print("accounts to be liquidated: ", liquidatable_accounts)

    for trader in liquidatable_accounts:
        liquidatorAddr = web3.eth.accounts[0]  # default account to call the function
        traderAddr = trader
        updateData = [bytes.fromhex(get_vaa_from_pyth(perpetual_id, config))]
        publishTimes = [get_publish_time(perpetual_id, config)]
        
        tx_hash = perpetual_contract.functions.liquidateByAMM(
            perpetual_id,
            liquidatorAddr,
            traderAddr,
            updateData,
            publishTimes
        ).transact({"from": liquidatorAddr})
        
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Liquidated {traderAddr}, transaction hash: {receipt.transactionHash.hex()}")


def main():
    """Main function to run the script"""
    with open("config.json") as config_file:
        config = json.load(config_file)
    
    perpetual_id = 100000
    chain_name = "arbitrumSepolia"
    
    web3 = connect_to_blockchain(chain_name, config)
    liquidate_positions(perpetual_id, config, web3, chain_name)

if __name__ == "__main__":
    main()