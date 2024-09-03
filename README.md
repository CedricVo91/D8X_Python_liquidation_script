# D8X Liquidation Script

## Overview
This repository contains a Python script developed by D8X for identifying and liquidating accounts that can be liquidated within their white-labeling software solution on the Arbitrum blockchain (both mainnet and testnet). The solution is built to facilitate third parties in constructing their own perpetual swap decentralized exchanges using the D8X platform.

The script is designed to be user-friendly, leveraging a configuration file (`config.json`) to simplify the process for Python developers, including beginners. This allows users to run the script without needing to worry about the complexities of different price feeds, addresses, and other technical details. The primary function of the script is to enable users to liquidate undercollateralized accounts and earn fees for this service.

## About D8X
D8X is an institutional-grade perpetual futures engine that revolutionizes on-chain trading by enabling decentralized perpetual futures with a robust financial engineering approach. The platform provides a decentralized BitMEX-like experience, customizable for white-labeling out of the box. D8X allows for perpetuals to be collateralized with nearly any ERC-20 token, including yield-bearing assets, providing flexible and adaptive trading solutions.

## Features
- **Multi-Network Support**: Operates on Arbitrum mainnet and testnet (Sepolia).
- **Flexible Pricing**: Integrates both on-chain and off-chain price feeds from sources like Angle, RedStone, and Pyth Network.
- **Beginner-Friendly**: Configurable via `config.json`, allowing for easy customization and deployment.
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
- **Running the script**:
  To execute the liquidation script, use the following command:
  ```bash
  python liquidate_positions_final.py
  ```

- **Configuration**:
  The script abstracts away a great deal of set-up complexities via the config file, so that beginner liquidators can focus on the actual liquidations.

- **Earning Fees**:
  When the script successfully liquidates an account, a portion of the liquidation fee is awarded to the user running the script. This fee is subtracted from the trader's margin.

## Configuration Details
The `config.json` file includes:

- **Chains**:
  Details about the blockchain networks (Arbitrum mainnet and Sepolia testnet) the script interacts with.
  Example:
  ```json
  {
    "name": "arbitrum",
    "chainId": 42161,
    "proxyAddr": "0x8f8BccE4c180B699F81499005281fA89440D1e95",
    "nodeURL": "https://arbitrum.llamarpc.com"
  }
  ```

- **Price Feeds**:
  On-chain and off-chain price feeds for various asset pairs.
  Example:
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

- **Perpetual Contracts**:
  Configurations for various perpetual contracts handled by the script.
  Example:
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
- `liquidate_positions_final.py`: The main script that identifies and liquidates undercollateralized accounts.
- `config.json`: Configuration file for setting up network details, price feeds, and perpetual contracts.
- `getOffchainPriceHermes.py`: Fetches off-chain prices from the Pyth network.
- `getOnchainPriceAngle.py`: Retrieves on-chain prices using Angle protocol oracles.
- `getOnchainPriceRedStone.py`: Fetches on-chain prices using RedStone oracles.
- `IPerpetualManager.json`: ABI file for interacting with the perpetual manager contract on Arbitrum.
- `RedStoneAbi.json`: ABI file for interacting with RedStone price oracles.

## Future Enhancements
- **Medium Article**: A comprehensive guide will be published on Medium, demonstrating how to set up and use the script to interact with D8X's white-labeling solution.
- **Additional Features**: Potential integration with other blockchains and enhanced UI for easier management.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with your changes. Ensure that your code follows the project's style guidelines and is thoroughly tested.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact
For any questions or support, please contact the D8X development team at support@d8x.io.
