from __future__ import annotations # Non runtime type checking

import datetime
import logging
import enum
import typing

if typing.TYPE_CHECKING:
    from biggygains.environment.interface import Environment

logger = logging.getLogger(__name__)

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
Base class for equity pricing sources. An environment will have a single pricing
source that it gets data from
"""
class PricingSource:
    def initialize(self, environment: Environment) -> bool:
        """
        Initialize any internal resources and return true on success or false
        on error. Required arguments should be passed in the constructor
        """

        logger.warning(f'initialize() is unimplemented in {type(self).__name__}')
        return False

    def get_equity(self, ticker) -> Stock:
        """
        Fetch and return the entire metadata set for a given ticker. Additional
        keyword arguments may be passed to custom sources to get different 
        information, such as historical time ranges
        """

        logger.warning(f'get_equity() is unimplemented in {type(self).__name__}')
        pass

    def get_quote(self, ticker) -> Quote:
        """
        Fetch and return a single quote for the given ticker
        """

        logger.warning(f'get_quote() is unimplemented in {type(self).__name__}')
        pass


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
    Limit = 'Limit'
    Stop = 'stop'
    StopLimit = 'limit'
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
        self.order_id = None
        self.limit_price = kwargs['limit_price'] if 'limit_price' in kwargs else None
        self.stop_price = kwargs['stop_price'] if 'stop_price' in kwargs else None


"""
Provides the external interface to where trading is being done. Derived classes
should be constructed for each supported platform
"""
class TradeInterface:
    def initialize(self, environment: Environment) -> bool:
        """
        Load and set the current holdings in the Portfolio in environment.
        Open orders should also be read and queued to be handled in update()
        Required parameters should be passed into the derived constructors
        """

        logger.warning(f'initialize() is unimplemented in {type(self).__name__}')
        return False

    def update(self, environment: Environment):
        """
        Check the status of any outstanding orders and emit ExecutedOrder objects
        to the environment via notify_order_completed
        """

        logger.warning(f'update() is unimplemented in {type(self).__name__}')
        pass

    def place_order(self, order: Order) -> bool:
        """
        Place the given order. Return false if error on placement
        """

        logger.warning(f'place_order() is unimplemented in {type(self).__name__}')
        return False

    def market_open(self) -> bool:
        """
        Returns whether or not the market is open for trading
        """

        logger.warning(f'market_open() is unimplemented in {type(self).__name__}')
        return False

    def open_orders(self) -> typing.List[Order]:
        """
        Returns a list of all currently open orders
        """

        logger.warning(f'open_orders() is unimplemented in {type(self).__name__}')
        return []
