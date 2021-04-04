from __future__ import annotations # Non runtime type checking

import logging
import typing

if typing.TYPE_CHECKING:
    from biggygains.environment.interface import Environment

logger = logging.getLogger(__name__)


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

    def cancel_order(self, order_id) -> bool:
        """
        Cancels an open order and returns True if canceled, False if unable or not found
        """

        logger.warning(f'cancel_order() is unimplemented in {type(self).__name__}')
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

    def ticker_exists(self, ticker) -> bool:
        """
        Tests whether the given ticker is valid
        """
        
        logger.warning(f'ticker_exists() is unimplemented in {type(self).__name__}')
        return ticker.upper() in ['GME', 'AMC', 'AAPL']
