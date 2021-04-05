from __future__ import annotations # Non runtime type checking

import datetime
import enum
import typing

if typing.TYPE_CHECKING:
    from environment.interface import Environment


"""
A basic quote for a stock. Includes bid, ask, and mid prices, as well as current
volume and quote time
"""
class Quote:
    def __init__(self, bid, ask, volume, time: datetime.datetime):
        self.bid = bid
        self.ask = ask
        self.mid = (bid + ask) / 2
        self.volume = volume
        self.time = time


"""
Represents a past trading day for a particular stock. Holds information 
about the open and close, as well as the trade date
"""
class TradingDay:
    def __init__(self, date: datetime.date, open_: Quote, close: Quote):
        self.date = date
        self.open = open_
        self.close = close


"""
Represents metadata about a particular equity. Holds ticker, current quote,
historical quotes, past trading day information, and other metrics such as
volume, eps, p/e ratio, etc.
"""
class Stock:
    def __init__(self, ticker, quote: Quote, **kwargs):
        """
        Builds the stock info. Only ticker and current quote are required

        Optional keyword arguments:
            timeseries: List of quotes containing granular time and price info
            history: List of TradingDay for previous trading days
            pe: P/E ratio of the company
            eps: Earnings per share of the company
            low: 52 week low
            high: 52 week high
            avgvol: Average volume
        """
    
        self.ticker = ticker
        self.quote = quote
        self.timeseries = kwargs['timeseries'] if 'timeseries' in kwargs else [quote]
        self.history = kwargs['hist'] if 'hist' in kwargs else []
        self.pe = kwargs['pe'] if 'pe' in kwargs else 0
        self.eps = kwargs['eps'] if 'eps' in kwargs else 0
        self.low = kwargs['low'] if 'low' in kwargs else 0
        self.high = kwargs['high'] if 'high' in kwargs else 0
        self.avgvol = kwargs['avgvol'] if 'avgvol' in kwargs else 0





"""
Basic class representing an executed order. Objects of this class are emitted by
TradeInterface when orders are successfully executed and are processed by Environment
to keep local book information up to date
"""
class ExecutedOrder:
    def __init__(self, ticker, quantity, avg_price, is_buy):
        self.ticker = ticker
        self.quantity = quantity
        self.avg_price = avg_price
        self.is_buy = is_buy
        self.is_sell = not is_buy


"""
Basic enumeration representing supported order types
"""
class OrderType(enum.Enum):
    Market = 'market'
    Limit = 'limit'
    Stop = 'stop'
    StopLimit = 'stoplimit'
    # Add whatever else is supported


"""
Basic representation of an order that may be placed and executed
"""
class Order:
    def __init__(self, ticker, order_type: OrderType, quantity, is_buy, **kwargs):
        self.ticker = ticker
        self.order_type = order_type
        self.quantity = quantity
        self.is_buy = is_buy
        self.is_sell = not is_buy
        self.order_id = kwargs['order_id'] if 'order_id' in kwargs else None
        self.limit_price = kwargs['limit_price'] if 'limit_price' in kwargs else None
        self.stop_price = kwargs['stop_price'] if 'stop_price' in kwargs else None
