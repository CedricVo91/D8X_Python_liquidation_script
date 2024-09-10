# D8X Liquidation Script

## Overview
This repository contains a Python script designed for independent traders looking to earn a fee by liquidating undercollateralized accounts on the D8X exchange. The script automates the process of identifying and liquidating eligible accounts on the Arbitrum blockchain (mainnet and testnet), enabling users to earn fees for each successful liquidation.

The script is user-friendly, requiring minimal setup. A configuration file (`config/config.json`) simplifies the process by handling network connections, price feeds, and contract interactions, making it accessible even to those with basic Python knowledge. With this tool, you can capitalize on the opportunities offered by the D8X platform without worrying about the complexities involved.

## About D8X
D8X is an institutional-grade perpetual futures engine that revolutionizes on-chain trading by enabling decentralized perpetual futures with a robust financial engineering approach. The platform provides a decentralized BitMEX-like experience, customizable for white-labeling out of the box. D8X allows for perpetuals to be collateralized with nearly any ERC-20 token, including yield-bearing assets, providing flexible and adaptive trading solutions.

## Features
- **Multi-Network Support**: Operates on Arbitrum mainnet and testnet (Sepolia).
- **Flexible Pricing**: Integrates both on-chain and off-chain price feeds from sources like Angle, RedStone, and Pyth Network.
- **Beginner-Friendly**: Configurable via `config/config.json`, allowing for easy customization and deployment.
- **Automated Liquidation**: Identifies and liquidates accounts that can be liquidated, earning a fee in the process.

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/d8x-liquidation-script.git
   cd d8x-liquidation-script
   ```

2. Install dependencies: Ensure you have Python 3.8+ installed, then install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

## Usage
- **Running the script**: To execute the liquidation script, use the following command:
  ```bash
  python src/liquidation/app.py
  ```

- **Configuration**: The script abstracts away a great deal of set-up complexities via the config file, so that beginner liquidators can focus on the actual liquidations.

- **Earning Fees**: When the script successfully liquidates an account, a portion of the liquidation fee is awarded to the user running the script. This fee is subtracted from the trader's margin.

## Configuration Details
The `config/config.json` file includes:

- **Chains**: Details about the blockchain networks (Arbitrum mainnet and Sepolia testnet) the script interacts with. Example:
  ```json
  {
    "name": "arbitrum",
    "chainId": 42161,
    "proxyAddr": "0x8f8BccE4c180B699F81499005281fA89440D1e95",
    "nodeURL": "https://arbitrum.llamarpc.com"
  }
  ```

- **Price Feeds**: On-chain and off-chain price feeds for various asset pairs. Example:
  ```json
  {
    "onChain": {
      "WEETH-ETH": {
        "address": "0x119A190b510c9c0D5Ec301b60B2fE70A50356aE9",
        "get_latest_price_function": "latestRoundData",
        "price_index": 1,
        "decimals": 8,
        "source": "redstone"
      }
    },
    "offChain": {
      "ETH-USD": {
        "id": "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"  
      }
    }
  }
  ```

- **Perpetual Contracts**: Configurations for various perpetual contracts handled by the script. Example:
  ```json
  {
    "id": 200000,
    "poolSymbol": "WEETH",
    "baseCurrency": "ETH",
    "quoteCurrency": "USD",
    "s2": ["*", "ETH-USD"],
    "s3": ["*", "WEETH-ETH", "*", "ETH-USD"]
  }
  ```

## File Descriptions
- `src/liquidation/app.py`: The main script that identifies and liquidates undercollateralized accounts.
- `config/config.json`: Configuration file for setting up network details, price feeds, and perpetual contracts.
- `src/liquidation/helpers/getOffchainPriceHermes.py`: Fetches off-chain prices from the Pyth network.
- `src/liquidation/helpers/getOnchainPriceAngle.py`: Retrieves on-chain prices using Angle protocol oracles.
- `src/liquidation/helpers/getOnchainPriceRedStone.py`: Fetches on-chain prices using RedStone oracles.
- `contracts/IPerpetualManager.json`: ABI file for interacting with the perpetual manager contract on Arbitrum.
- `contracts/RedStoneAbi.json`: ABI file for interacting with RedStone price oracles.

## Future Enhancements
- **Medium Article**: A comprehensive guide will be published on Medium, demonstrating how to set up and use the script to interact with D8X's white-labeling solution.
- **Additional Features**: Potential integration with other blockchains and enhanced UI for easier management.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with your changes. Ensure that your code follows the project's style guidelines and is thoroughly tested.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
