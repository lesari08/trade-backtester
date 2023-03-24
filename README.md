# backtesterPy

backtesterPy is a Python library that allows users to backtest trading strategies on historical market data. It provides an easy-to-use interface for loading historical data, defining trading rules, and evaluating the performance of the strategy.

## Features
- Supports multiple asset classes including stocks, futures, and currencies
- Built on top of the popular pandas library for data manipulation and analysis
- Customizable trading rules that can be defined in Python code
- User-defined risk management rules to limit drawdown and manage capital
- Multiple performance metrics including Sharpe ratio, Maximum Drawdown, and Cumulative Return
- Visualizations of performance metrics and trading signals

## Installation
backtesterPy can be installed via pip:

`pip install backtesterPy`

## Usage
To use backtesterPy, you first need to import the Backtest class:

`$ from backtester import Backtest `

Then, you can create a new backtest object and specify the trading strategy:



`bt = Backtest(strategy=my_strategy)`

Finally, you can run the backtest:



`bt.run()`

The results of the backtest will be stored in the results attribute of the Backtest object.

## Examples
For examples of how to use backtesterPy, please see the examples directory. (Coming soon)

## License
backtesterPy is licensed under the MIT License. See the LICENSE file for details.
