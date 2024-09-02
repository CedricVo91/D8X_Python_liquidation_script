from web3 import Web3
from decimal import Decimal

def get_stusd_to_usdc_price(config):
    # Define the ABI for IERC4626 and ITransmuter contracts
    ierc4626ABI = [{"constant": True, "inputs": [{"name": "assets", "type": "uint256"}], "name": "previewMint", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}]
    iTransmuterABI = [{"constant": True, "inputs": [{"name": "amountOut", "type": "uint256"}, {"name": "toToken", "type": "address"}, {"name": "fromToken", "type": "address"}], "name": "quoteOut", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}]

    # Contract addresses
    STUSD = Web3.to_checksum_address("0x0022228a2cc5E7eF0274A7Baa600d44da5aB5776")  # stUSD, savings
    USDC = Web3.to_checksum_address("0xaf88d065e77c8cC2239327C5EDb3A432268e5831")  # native USDC, 6 decimals
    USDA = Web3.to_checksum_address("0x0000206329b97DB379d5E1Bf586BbDB969C63274")  # USDA on Arbitrum, 18 decimals
    transmuterAddr = Web3.to_checksum_address("0xD253b62108d1831aEd298Fc2434A5A8e4E418053")  # for USDA, arbitrum

    # Initialize the Web3 provider
    mainnet_config = next(chain for chain in config["chains"] if chain["name"] == "arbitrum")
    provider = Web3(Web3.HTTPProvider(mainnet_config["nodeURL"]))
    if not provider.is_connected():
        raise ConnectionError("Failed to connect to the mainnet")

    # Create contract instances
    ierc4626Contract = provider.eth.contract(address=STUSD, abi=ierc4626ABI)
    iTransmuterContract = provider.eth.contract(address=transmuterAddr, abi=iTransmuterABI)

    # Define the amount of 1 stUSD in wei (18 decimals)
    ONE_STUSD = Web3.to_wei(1, 'ether')
    
    # Call previewMint to get amountUSDA
    amount_usda = ierc4626Contract.functions.previewMint(ONE_STUSD).call()
    
    # Call quoteOut to get amountUSDC
    amount_usdc = iTransmuterContract.functions.quoteOut(amount_usda, USDC, USDA).call()

    # Convert and return the price of 1 stUSD in USDC
    return float(Decimal(amount_usdc) / Decimal(10**6))

# Example usage in main.py:
# Define the mainnet configuration
"""
mainnet_config = {
    "nodeURL": "https://arb1.arbitrum.io/rpc",  # Replace with your RPC URL
}

# Fetch the on-chain price of stUSD in USDC
latest_stusd_usdc_price = get_stusd_to_usdc_price(mainnet_config)
print(f"The price of 1 stUSD in USDC is: {latest_stusd_usdc_price}")
"""