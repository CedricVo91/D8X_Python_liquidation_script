import requests
import json
def get_offchain_price(price_feed_id, config):
    
    url = config["priceFeeds"]["offChain"]["common"]["price_feed_url"]
    params = {"ids[]": price_feed_id}
    
    try:
        response = requests.get(url, params=params)
        price_data = response.json()
        prices = []
        for asset in price_data["parsed"]:
            prices.append(int(asset["price"]["price"]) * (10**asset["price"]["expo"]))
        if len(prices) == 1:
            return prices[0]
        else:
            return prices
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def get_publish_time(perpetual_id, config):
    perpetual_config = next(p for p in config["perpetuals"] if p["id"] == perpetual_id)
    url = config["priceFeeds"]["offChain"]["common"]["price_feed_url"] #more intelligent with if for if s3 has three or not. 
    
    if len(perpetual_config["s3"]) == 1:
        price_feed_ids = [config["priceFeeds"]["offChain"]["feeds"][perpetual_config["s2"][0]]["id"], config["priceFeeds"]["offChain"]["feeds"][perpetual_config["s3"][0]]["id"]]
    else: #in case of onchain price for s3    
        price_feed_ids = config["priceFeeds"]["offChain"]["feeds"][perpetual_config["s2"][0]]["id"] 

    params = {"ids[]": price_feed_ids}
    response = requests.get(url, params=params)
    response_data = response.json()
    publish_time = response_data["parsed"][0]["price"]["publish_time"]
    return publish_time

def get_vaa_from_pyth(perpetual_id, config):
    perpetual_config = next(p for p in config["perpetuals"] if p["id"] == perpetual_id)
    url = config["priceFeeds"]["offChain"]["common"]["price_feed_url"] #more intelligent with if for if s3 has three or not. 
    
    if len(perpetual_config["s3"]) == 1:
        price_feed_ids = [config["priceFeeds"]["offChain"]["feeds"][perpetual_config["s2"][0]]["id"], config["priceFeeds"]["offChain"]["feeds"][perpetual_config["s3"][0]]["id"]]
    else: #in case of onchain price for s3    
        price_feed_ids = config["priceFeeds"]["offChain"]["feeds"][perpetual_config["s2"][0]]["id"] 
    
    params = {"ids[]": price_feed_ids}
    response = requests.get(url, params=params)
    response_data = response.json()
    # Extract the VAA from the binary data section
    vaa_hex = response_data['binary']['data'][0]  # Assuming the VAA is the first item in the data list
    return vaa_hex
