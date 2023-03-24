#!/usr/bin/python
# -*- coding: utf-8 -*-
# data.py
from __future__ import print_function
from abc import ABCMeta, abstractmethod
import datetime
import os, os.path
import numpy as np
import pandas as pd
from event import MarketEvent

class DataHandler(object):
	"""
	DataHandler is an abstract base class providing an interface for
	all subsequent (inherited) data handlers (both live and historic).
	The goal of a (derived) DataHandler object is to output a generated
	set of bars (OHLCVI) for each symbol requested.
	This will replicate how a live strategy would function as current
	market data would be sent "down the pipe". Thus a historic and live
	system will be treated identically by the rest of the backtesting suite.
	"""
	
	__metaclass__ = ABCMeta
	@abstractmethod
	def get_latest_bar(self, symbol):
		"""
		Returns the last bar updated.
		"""
		raise NotImplementedError("Should implement get_latest_bar()")
	@abstractmethod
	def get_latest_bars(self, symbol, N=1):
		"""
		Returns the last N bars updated.
		"""
		raise NotImplementedError("Should implement get_latest_bars()")
	@abstractmethod
	def get_latest_bar_datetime(self, symbol):
		"""
		Returns a Python datetime object for the last bar.
		(e.g. a date for daily bars or a minute-resolution object
		for minutely bars
		"""
		raise NotImplementedError("Should implement get_latest_bar_datetime()")
	@abstractmethod
	def get_latest_bar_value(self, symbol, val_type):
		"""
		Returns one of the Open, High, Low, Close, Volume or OI
		from the last bar.
		convenience methods used to retrieve individual values from a particular bar. For
		instance if a strategy is only interested in closing prices, we can use these methods
		to return a list of floating point values representing the closing prices of previous
		bars, rather than having to obtain it from the list of bar objects. This generally 
		increases efficiency of strategies that utilise a "lookback window", such as those 
		involving regressions.
		"""
		raise NotImplementedError("Should implement get_latest_bar_value()")
	@abstractmethod
	def get_latest_bars_values(self, symbol, val_type, N=1):
		"""
		Returns the last N bar values from the
		latest_symbol list, or N-k if less available.
		"""
		raise NotImplementedError("Should implement get_latest_bars_values()")
	@abstractmethod
	def update_bars(self):
		"""
		Pushes the latest bars to the bars_queue for each symbol
		in a tuple OHLCVI format: (datetime, open, high, low,
		close, volume, open interest).
		The final method, update_bars, provides a "drip feed" mechanism 
		for placing bar information on a new data structure that strictly
		prohibits lookahead bias. This is one of the key differences 
		between an event-driven backtesting system and one based on 
		vectorisation.
		"""
		raise NotImplementedError("Should implement update_bars()")
		
		
class HistoricCSVDataHandler(DataHandler):
	"""
	HistoricCSVDataHandler is designed to read CSV files for
	each requested symbol from disk and provide an interface
	to obtain the "latest" bar in a manner identical to a live
	trading interface.
	Multiple CSV (comma separated variable) files that will be potentially large
	A good candidate for making a DataHandler class would
	be to couple it with a Securities Master Databse. But currently
	the focus is getting the backtester up and running. In future
	versions we'll add the boilerplate  code of connecting to a db
	and retrieving the data via SQL queries
	"""
	def __init__(self, events, csv_dir, symbol_list):
		"""
		Initialises the historic data handler by requesting
		the location of the CSV files and a list of symbols.
		It will be assumed that all files are of the form
		'symbol.csv', where symbol is a string in the list.
		Parameters:
		events - The Event Queue.
		csv_dir - Absolute directory path to the CSV files.
		symbol_list - A list of symbol strings.
		"""
		self.events = events
		self.csv_dir = csv_dir
		self.symbol_list = symbol_list
		self.symbol_data = {}
		self.latest_symbol_data = {}
		self.continue_backtest = True
		self._open_convert_csv_files()
		
	def _open_convert_csv_files(self):
		"""
		Opens the CSV files from the data directory, converting
		them into pandas DataFrames within a symbol dictionary.
		For this handler it will be assumed that the data is
		taken from Yahoo. Thus its format will be respected.
		*But format can be modified for other data feeds as needed
		"""
		comb_index = None
		for s in self.symbol_list:
			# Load the CSV file with no header information, indexed on date
			self.symbol_data[s] = pd.io.parsers.read_csv(
			os.path.join(self.csv_dir, '%s.csv' % s),
			header=0, index_col=0, parse_dates=True,
			names=[
			'datetime', 'open', 'high',
			'low', 'close', 'adj_close', 'volume'
			]
			).sort_values('datetime')
			# Initialize a key with a default value for each symbol in symbol_list
			self.latest_symbol_data[s] = []
    		
			# Initialize a key with a default value for each symbol in symbol_list
    		#
		print(self.latest_symbol_data)
		# Combine the index to pad forward values
		"""
		One of the benefits of using pandas as a datastore internally within the HistoricCSVData-
		Handler is that the indexes of all symbols being tracked can be merged together. This allows
		missing data points to be padded forward, backward or interpolated within these gaps such that
		tickers can be compared on a bar-to-bar basis. This is necessary for mean-reverting strategies,
		for instance. Notice the use of the union and reindex methods when combining the indexes for
		all symbols:
		"""
		if comb_index is None:
			comb_index = self.symbol_data[s].index
		else:
			comb_index.union(self.symbol_data[s].index)
			# Set the latest symbol_data to None
			self.latest_symbol_data[s] = []
		# Reindex the dataframes
		for s in self.symbol_list:
			self.symbol_data[s] = self.symbol_data[s].\
			reindex(index=comb_index, method='pad').iterrows()

	def _get_new_bar(self, symbol):
		"""
		Returns the latest bar from the data feed.
		"""
		"""
		The _get_new_bar method creates a generator to provide a new bar. 
		This means that subsequent calls to the method will yield a new bar 
		until the end of the symbol data is reached
		"""
		for b in self.symbol_data[symbol]:
			yield b
	
	#abstract method overrides
	# 
	
	def get_latest_bar(self, symbol):
		"""
		Returns the last bar from the latest_symbol list.
		"""
		try:
			bars_list = self.latest_symbol_data[symbol]
		except KeyError:
			print("That symbol is not available in the historical data set.")
			raise
		else:
			return bars_list[-1]
	def get_latest_bars(self, symbol, N=1):
		"""
		Returns the last N bars from the latest_symbol list,
		or N-k if less available.
		"""
		try:
			bars_list = self.latest_symbol_data[symbol]
		except KeyError:
			print("That symbol is not available in the historical data set.")
			raise
		else:
			return bars_list[-N:]


	def get_latest_bar_datetime(self, symbol):
		"""
		Returns a Python datetime object for the last bar.
		"""
		"""
		queries the latest bar for a datetime object
		representing the "last market price"
		"""
		try:
			bars_list = self.latest_symbol_data[symbol]
		except KeyError:
			print("That symbol is not available in the historical data set.")
			raise
		else:
			return bars_list[-1][0]
			
	def get_latest_bar_value(self, symbol, val_type):
		"""
		Returns one of the Open, High, Low, Close, Volume or OI
		values from the pandas Bar series object.
		"""
		try:
			bars_list = self.latest_symbol_data[symbol]
		except KeyError:
			print("That symbol is not available in the historical data set.")
			raise
		else:
			return getattr(bars_list[-1][1], val_type)

	def get_latest_bars_values(self, symbol, val_type, N=1):
		"""
		Returns the last N bar values from the
		latest_symbol list, or N-k if less available.
		"""
		
		"""
		Both methods make use of the Python getattr function, which queries an object to see if a par-
		ticular attribute exists on an object. Thus we can pass a string such as "open" or "close" to
		getattr and obtain the value direct from the bar, thus making the method more flexible. This
		stops us having to write methods of the type get_latest_bar_close, for instance:
		"""
		try:
			bars_list = self.get_latest_bars(symbol, N)
		except KeyError:
			print("That symbol is not available in the historical data set.")
			raise
		else:
			return np.array([getattr(b[1], val_type) for b in bars_list])
			
	def update_bars(self):
		"""
		Pushes the latest bar to the latest_symbol_data structure
		for all symbols in the symbol list.
		"""
		
		"""
		The final method, update_bars, is the second abstract method from DataHandler. It simply
		generates a MarketEvent that gets added to the queue as it appends the latest bars to the
		latest_symbol_data dictionary:
		"""
		for s in self.symbol_list:
			try:
				bar = next(self._get_new_bar(s))
			except StopIteration:
				self.continue_backtest = False
			else:
				if bar is not None:
					self.latest_symbol_data[s].append(bar)
		self.events.put(MarketEvent())
		
		
#sanity check 	
print("im like hey whats up hellooo... from data.py")



















