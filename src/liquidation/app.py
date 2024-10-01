from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from dotenv import load_dotenv

import json 
import os
from pathlib import Path
import time 
import logging
import sys

from helpers.getOffchainPriceHermes import get_offchain_data
from helpers.getOnchainPriceRedStone import get_onchain_price_redstone
from helpers.getOnchainPriceAngle import get_stusd_to_usdc_price

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# Configure logging so that it works in the docker container
LOG_DIR = os.getenv('LOG_DIR', BASE_DIR / 'logs') #either get the env variable from log_dir (in case of running it via dockers) or get the default value (when running it locally)
#create directory LOG_DIR when it does not exit (in case we download our github repo - and local logs folder won't be pushed)
os.makedirs(LOG_DIR, exist_ok=True)
log_path = Path(LOG_DIR) / 'liquidation.log'

#old absolute log path to run it just locally
#log_path = '/Users/cedric/D8X/D8X_Python_liquidation_script/logs/liquidation.log'

logging.basicConfig(
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    
    handlers=[
        logging.FileHandler(log_path, mode='w'),  # Log to file (overwrite)
        logging.StreamHandler(sys.stdout)  # Log to console (stdout)
    ],
    force=True  # Overwrite any existing logging config
)

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
          id = offchain_price_config[symbol]["id"]
          off_chain_price, publish_time, vaa_hex = get_offchain_data(id, config)
          #logging.info(f"Off-chain price for {symbol}: {off_chain_price}")
          return [off_chain_price, publish_time, vaa_hex, id]  
     
     elif any (part in ("WEETH") for part in symbol.split("-")):
          on_chain_price = get_onchain_price_redstone(on_chain_price_config[symbol], config)
          return [on_chain_price]
     
     else:
          on_chain_price = get_stusd_to_usdc_price(config)
          return [on_chain_price]  
     
    #the price construction logic
    perpetual_config = next(p for p in config["perpetuals"] if p["id"] == perpetual_id)
    # Initialize results dictionary
    prices = {}
    off_chain_price_info = []

    # Process s2 and s3 entries
    for key in ["s2", "s3"]:
        symbol_entries = perpetual_config[key]
        price = 1
        price_name = "" #better than none to build up the string
        
        #check if symbol entries are empty
        # check for the exception where s3 is empty i.e. quoteCurrency is the same as poolCurrency 
        if not symbol_entries:
            logging.info(f"PoolCurrency and quoteCurrency are the same for perpetual {perpetual_id}")
            price_name, price = None, None

        # Iterate through the symbol entries and apply operations
        for i in range(0, len(symbol_entries), 2):  # Step by 2 to skip over symbols after operations
            
            operation = symbol_entries[i]
            symbol = symbol_entries[i+1]
            fetched_price_info = fetch_price(symbol, config)

            if len(fetched_price_info) > 1: #in case of offchain price where we need vaa and publish time
                fetched_price, publish_time, vaa_hex, id = fetched_price_info[0], fetched_price_info[1], fetched_price_info[2], fetched_price_info[3]
                found = False
                for dict in off_chain_price_info:
                    if dict["id"] == id:
                        found = True
                        break
                if not found:
                    off_chain_price_info.append({"fetched_price":fetched_price,"publish_time":publish_time,"vaa_hex": vaa_hex, "id": id })    
            else:
                fetched_price = fetched_price_info[0]
            
            if operation == "/":
                price /= fetched_price
                if not price_name: #"" in python is considered false! if price_name="" then we enter the if statement
                    #below we only consider the symbol to create the price name as the price name is empty still 
                    price_name = symbol.split("-")[1] + "-" + symbol.split("-")[0]
                else:
                    #below we consider the first half of entry name in s2 (or s3) and then the first part of the second symbol i s2 or s3
                    price_name = price_name.split("-")[0] + "-" + symbol.split("-")[0]
            
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

    logging.info(f"Prices for perpetual {perpetual_id}: {prices}")
    #logging.info(f"Off-chain price info: {off_chain_price_info}")
    return prices["s2"], prices["s3"], off_chain_price_info

#3. connect to blockchain
def connect_to_blockchain(chain_name, config):
    chain_config = next(chain for chain in config["chains"] if chain["name"] == chain_name)
    web3 = Web3(Web3.HTTPProvider(chain_config["nodeURL"])) 
    if web3.is_connected:
        logging.info(f"Connected successfully to {chain_config['name']}")
        return web3
    else:
        logging.error(f"Failed to connect to {chain_config['name']}")
        raise ConnectionError(f"Failed to connect to {chain_config['name']}")

#4. identify and liquidate positions
def liquidate_positions(perpetual_id, config, web3, chain_name):
    """Fetch and liquidate positions for a given perpetual"""
    
    address = next(chain for chain in config["chains"] if chain["name"] == chain_name)["proxyAddr"]
    #abi_path = '/Users/cedric/D8X/D8X_Python_liquidation_script/abi/IPerpetualManager.json'
    abi_path = BASE_DIR / 'abi' / 'IPerpetualManager.json'
    with open(abi_path) as proxy_abi_file:
        proxy_abi = json.load(proxy_abi_file)
    
    perpetual_contract = web3.eth.contract(address=address, abi=proxy_abi)
    price1, price2, off_chain_price_info = get_prices(perpetual_id, config)

    # check for the exception where s3 is empty i.e. quoteCurrency is the same as poolCurrency 
    if price2[1] is None:
        price2 = (None, 0) 
    
    liquidatable_accounts = perpetual_contract.functions.getLiquidatableAccounts(
    perpetual_id, [abdk64x64_conversion(price1[1]), abdk64x64_conversion(price2[1])]
    ).call()

    logging.info(f"Accounts to be liquidated: {liquidatable_accounts}") 

    
    # Liquidate accounts -> send a signed transaction to the blockchain
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    publish_time_array = [int(dict["publish_time"]) for dict in off_chain_price_info]
    #logging.info(f"Publish time array: {publish_time_array}")
    vaa_array = [bytes.fromhex(dict["vaa_hex"]) for dict in off_chain_price_info]
    #logging.info(f"VAA array: {vaa_array}")
    
    logging.info("Liquidating positions...")

    for trader in liquidatable_accounts:
        liquidatorAddr = web3.eth.account.from_key(PRIVATE_KEY).address # without key: web3.eth.accounts[0]  # default account to call the function
        traderAddr = trader
        logging.info(f"Liquidating {traderAddr}...")
        updateData = vaa_array
        
        publishTimes = publish_time_array

        # Check balance
        balance = web3.eth.get_balance(liquidatorAddr)
        logging.info(f"Balance of liquidator: {web3.from_wei(balance, 'ether')} ETH")

        if balance < web3.to_wei(0.01, 'ether'):  # Adjust the threshold as needed
            logging.error(f"Insufficient balance to cover gas fees for {liquidatorAddr}")
            continue

        try:

            tx_hash = perpetual_contract.functions.liquidateByAMM(
                perpetual_id,
                liquidatorAddr,
                traderAddr,
                updateData,
                publishTimes
            ).transact({"from": liquidatorAddr, "gas": 10_000_000,  "value": len(publishTimes)}) # Adjust the gas limit as needed
        
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            logging.info(f"Liquidated {traderAddr}, transaction hash: {receipt.transactionHash.hex()}")
        
        except Exception as e:
            logging.error(f"Failed to liquidate {traderAddr}: {e}")

    logging.info("Liquidation of all undercollateralized traders complete")
    

def main():
    """Main function to run the
      script"""
    logging.info("Starting bot...")
    try:
        load_dotenv()

        #config_path = '/Users/cedric/D8X/D8X_Python_liquidation_script/config/config.json'
        config_path = BASE_DIR / 'config' / 'config.json'
        with open(config_path) as config_file:
            config = json.load(config_file)
    
        chain_name = "arbitrumSepolia" # outside or inside of while loop?

        web3 = connect_to_blockchain(chain_name, config)
        logging.info("Connected to blockchain")

        #add the signing middleware here
        private_key = os.getenv("PRIVATE_KEY")
        account = web3.eth.account.from_key(private_key)
        web3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        while True:
            try:
                logging.info("Entering the perpetual loop")
                for perpetual in config["perpetuals"]:
                
                    perpetual_id = perpetual["id"]
                    logging.info(f"Processing perpetual {perpetual_id}")
                    liquidate_positions(perpetual_id, config, web3, chain_name)
                    time.sleep(30)
                    logging.info(f"Sleeping for 30 seconds before processing next perpetual")

            except Exception as e:
                logging.error(f"An error in processing liquidations occured: {e}")
                break
                
    except Exception as e:
        logging.error(f"An error occured: {e}")
        

if __name__ == "__main__":
    main()