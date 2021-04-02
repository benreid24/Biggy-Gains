from __future__ import annotations # Non runtime type checking

import typing
import logging
import datetime
import time

if typing.TYPE_CHECKING:
    from .sentiment.interface import Sentiment, SentimentSource
    from .stock import Order, ExecutedOrder
    from .trading.interface import TradeInterface, PricingSource
    from biggygains.bots.interface import Bot

from .portfolio import Portfolio

logger = logging.getLogger(__name__)


"""
This is the base class for each environment a bot can run in. It provides
the set of methods used by the bot to interact with the world.
"""
class Environment:
    ##################################################################
    #                 Methods to be used by bots                     #
    ##################################################################

    def market_open(self) -> bool:
        """
        Returns whether or not the market is open for trading
        """
        return self.trade_interface.market_open()

    def now(self) -> datetime.datetime:
        """
        Returns the current time. Override for historical environments to
        simulate past times and elapsing of said time
        """
        return datetime.datetime.now()

    def get_portfolio(self) -> Portfolio:
        """
        Returns the current portfolio. Trading must be done through the
        environment, the returned Portfolio should be read only
        """
        return self.portfolio

    def get_sentiment(self, ticker) -> typing.List[Sentiment]:
        """
        Returns a list of all sentiment data for the given ticker
        """
        result = []
        for source in self.sentiment_sources:
            s = source.get_sentiment(ticker)
            if s:
                result.append(s)
        return result

    def get_all_sentiment(self) -> typing.List[typing.Dict[str, Sentiment]]:
        """
        Returns all sentiment data as a list. One item per source. Inner dict
        is keyed on ticker
        """
        return [source.get_all_sentiment() for source in self.sentiment_sources]

    def place_order(self, order: Order) -> bool:
        """
        Places an order. The order will not reflect in portfolio until it is executed
        """
        return self.trade_interface.place_order(order)

    def open_orders(self) -> typing.List[Order]:
        """
        Returns a list of all currently open orders
        """
        return self.trade_interface.open_orders()

    ##################################################################
    #           Methods to be used by custom environments            #
    ##################################################################

    def __init__(self):
        self.sentiment_sources = []
        self.bot = None
        self.price_source = None
        self.trade_interface = None
        self.portfolio = Portfolio(0)
        self.update_period_seconds = 60

    def connect_sentiment_source(self, source: SentimentSource):
        self.sentiment_sources.append(source)

    def set_pricing_source(self, source: PricingSource):
        self.price_source = source

    def set_trade_interface(self, interface: TradeInterface):
        self.trade_interface = interface

    def _initialize(self) -> bool:
        """
        Custom environment initialization goes here
        """

        logger.error(f'_initialize() is unimplemented by {type(self).__name__}')
        return False

    ##################################################################
    #         Methods to be used by environment components           #
    ##################################################################

    def notify_order_completed(self, order: ExecutedOrder):
        """
        This should be called by TradeInterfaces when an open order is executed
        """
        if order.is_buy:
            self.portfolio.buy(order.ticker, order.quantity, order.avg_price)
        else:
            self.portfolio.sell(order.ticker, order.quantity, order.avg_price)

    ##################################################################
    #            Methods to be used by global setup code             #
    ##################################################################

    def run(self):
        while True:
            self.trade_interface.update(self)
            for source in self.sentiment_sources:
                source.update(self)
            self.bot.update(self)
            time.sleep(self.update_period_seconds)

    def initialize(self) -> bool:
        for sentiment_source in self.sentiment_sources:
            if not sentiment_source.initialize(self):
                logger.error(f'Failed to initialize SentimentSource {type(sentiment_source).__name__}')
                return False
        if not self.trade_interface.initialize(self):
            logger.error('Failed to initialize trading interface')
            return False
        if not self.price_source.initialize(self):
            logger.error('Failed to initialize pricing source')
            return False
        if not self._initialize():
            logger.error(f'Failed to initialize custom environment: {type(self).__name__}')
        if not self.bot.initialize(self):
            logger.error('Failed to initialize bot')
            return False
        return True

    def connect_bot(self, bot: Bot):
        self.bot = bot
