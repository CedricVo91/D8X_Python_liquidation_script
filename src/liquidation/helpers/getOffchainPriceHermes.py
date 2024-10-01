import requests
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log to console (stdout)
    ]
)

def get_offchain_data(price_feed_id, config):
    
    url = config["priceFeeds"]["offChain"]["common"]["price_feed_url"]
    params = {"ids[]": price_feed_id}
    
    try:
        response = requests.get(url, params=params)
        response_data = response.json()
        price = int(response_data["parsed"][0]["price"]["price"]) * (10**response_data["parsed"][0]["price"]["expo"])
        publish_time = response_data["parsed"][0]["price"]["publish_time"]
        vaa_hex = response_data["binary"]["data"][0]
        id = response_data["parsed"][0]["id"]
        #logging.info(f"id:{id}, price: {price}, publish_time: {publish_time}, vaa_hex: {vaa_hex}")
        return price, publish_time, vaa_hex
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

"""
config_path = '/Users/cedric/D8X/D8X_Python_liquidation_script/config/config.json'
with open(config_path, "r") as f:
    config = json.load(f)
get_offchain_data("0xa995d00bb36a63cef7fd2c287dc105fc8f3d93779f062f09551b0af3e81ec30b",config)
print("------------------------------------------------------------------------------------")
get_offchain_data("0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",config)
"""
