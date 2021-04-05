import logging
from datetime import datetime, timedelta

from trading.interface import TradeInterface, PricingSource
from trading.stock import Order, OrderType, ExecutedOrder
from environment.interface import Environment
from trading.portfolio import Position

from alpaca_trade_api import REST as Alpaca

logger = logging.getLogger('AlpacaTradeInterface')


class AlpacaPricingSource(PricingSource):
    def __init__(self, key, secret, endpoint):
        self.api = Alpaca(key, secret, endpoint)

    def initialize(self, env: Environment):
        return True

    def get_equity(self, ticker):
        # TODO - fetch data and populate
        return None

    def get_quote(self, ticker):
        # TODO - fetch data and populate
        return None


class AlpacaTradeInterface(TradeInterface):
    def __init__(self, key, secret, endpoint):
        self.api = Alpaca(key, secret, endpoint)
        self.pending_orders = {}
        self.cached_tickers = {}

    def initialize(self, env: Environment):
        try:
            # Load cash balance
            account = self.api.get_account()
            env.get_portfolio().cash = float(account.cash) # We have margin but shouldn't use it

            # Load open orders
            orders = self.api.list_orders(status='open', limit=500)
            self.pending_orders = {
                order.id: Order(
                    order.symbol,
                    OrderType(order.order_type),
                    order.qty,
                    order.side == 'buy',
                    order_id=order.id,
                    limit_price=order.limit_price,
                    stop_price=order.stop_price
                )
                for order in orders
            }

            # Load open positions
            positions = self.api.list_positions()
            for pos in positions:
                env.get_portfolio()._add_position(Position(
                    pos.symbol,
                    pos.qty,
                    pos.avg_entry_price,
                    pos.current_price
                ))

        except Exception:
            logger.exception('Failed to pull current orders and cash balance')
            return False
        return True

    def update(self, env: Environment):
        orders = self.api.list_orders(status='closed', after=datetime.now() - timedelta(days=2), limit=500)
        for order in orders:
            if order['id'] in self.pending_orders:
                logger.info(f'Order {order.id} executed')
                env.notify_order_completed(ExecutedOrder(
                    order.symbol,
                    order.filled_qty,
                    order.filled_avg_price,
                    order.side == 'buy'
                ))

    def place_order(self, order: Order):
        logger.info(f'Placing order for {order.quantity} {order.ticker}')
        try:
            result = self.api.submit_order(
                order.ticker,
                order.quantity,
                'buy' if order.is_buy else 'sell',
                order.order_type.value,
                'day',
                limit_price=order.limit_price,
                stop_price=order.stop_price   
            )
            order.order_id = result.id
            self.pending_orders[result.id] = order
            return True

        except Exception:
            logger.exception(f'Failed to place order for {order.quantity} {order.ticker}')
            return False

    def cancel_order(self, order_id):
        logger.info(f'Canceling order {order_id}')
        try:
            self.api.cancel_order(order_id)
            self.pending_orders.pop(order_id, None)
            return True
        except Exception:
            logger.exception(f'Failed to cancel order {order_id}')
            return False

    def market_open(self):
        clock = self.api.get_clock()
        return clock.is_open # TODO - we also have open/close times. May want to avoid holding overnight

    def open_orders(self):
        return [order for order in self.pending_orders.values()]

    def ticker_exists(self, ticker):
        try:
            if ticker in self.cached_tickers:
                return self.cached_tickers[ticker]
            asset = self.api.get_asset(ticker)
            self.cached_tickers[ticker] = asset.tradable
            return asset.tradable
        except:
            self.cached_tickers[ticker] = False
            return False
