
# Long-Short Crypto Statistical Arbitrage Portfolio

## Overview

This project implements a daily long-short statistical arbitrage strategy in the cryptocurrency market. It capitalizes on the high correlation and cointegration among crypto assets, enabling the identification of mean-reverting spreads and the execution of profitable arbitrage opportunities.

## Features

- **Data Acquisition**: Asynchronous retrieval of market data.
- **Backtesting**: Evaluation of strategy performance using historical data.
- **Order Management**: Execution and management of trades.
- **Automation**: Deployment-ready with Docker for streamlined operations.

## Getting Started

### Prerequisites

- Docker installed on your system.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/zanyev/cripto.git
   cd cripto
   ```

2. Build the Docker image:

   ```bash
   docker build -t cripto-arbitrage .
   ```

3. Run the Docker container:

   ```bash
   docker run -d --name cripto-arbitrage cripto-arbitrage
   ```

## Project Structure

- `async_get_data.py`: Handles asynchronous data fetching.
- `back_test.ipynb`: Jupyter notebook for backtesting the strategy.
- `email_sender.py`: Sends notifications or reports via email.
- `get_data.ipynb`: Jupyter notebook for data exploration and analysis.
- `lambda_handler.py`: Entry point for AWS Lambda deployment.
- `oms.py`: Order Management System for executing trades.
- `Dockerfile`: Defines the Docker image configuration.
- `requirements.txt`: Lists Python dependencies.

## Usage

1. **Data Collection**: Fetch the latest market data using `async_get_data.py`.
2. **Backtesting**: Evaluate strategy performance with `back_test.ipynb`.
3. **Deployment**: Use `lambda_handler.py` for AWS Lambda deployment or run the Docker container for local execution.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.
