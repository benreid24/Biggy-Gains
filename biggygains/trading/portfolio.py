import logging
import typing

logger = logging.getLogger('Portfolio')


"""
This is the primary class for storing positions. Currently only long equity
positions are supported. Negative share quantities could represent short
positions, but Portfolio does not support them
"""
class Position:
    def __init__(self, ticker, qty, avg_price, current_price):
        self.ticker = ticker
        self.qty = qty
        self.avg_price = avg_price
        self.current_price = current_price

    def value(self):
        return self.qty * self.current_price

    def cost(self):
        return self.qty * self.avg_price

    def pnl(self):
        return self.value() - self.cost()

    def _update_price(self, new_price):
        self.current_price = new_price

    def _sell(self, qty):
        self.qty -= qty

    def _buy(self, qty, price):
        new_cost = self.cost() + qty * price
        self.qty += qty
        self.avg_price = new_cost / self.qty


"""
This is the primary class for storing portfolio information locally. It can be
populated from remote data or manually constructed. It can be kept up to date
as the bot trades, and used to compute total value and pnl
"""
class Portfolio:
    def value(self):
        return self.cash + sum([pos.value() for pos in self.positions.values()])

    def pnl(self):
        return sum([pos.pnl() for pos in self.positions.values()])

    def __init__(self, cash, positions: typing.List[Position] = []):
        self.cash = cash
        self.positions = {}

    def _add_position(self, position: Position):
        if position.ticker not in self.positions:
            self.positions[position.ticker] = position
        else:
            logger.warning(f'Position for {position.ticker} already in portfolio')

    def _buy(self, ticker, qty, price):
        if ticker in self.positions:
            self.positions[ticker]._buy(qty, price)
        else:
            self.positions[ticker] = Position(ticker, qty, price, price)
        self.cash -= qty * price

    def _sell(self, ticker, qty, price):
        if ticker in self.positions:
            self.positions[ticker]._sell(qty)
            self.cash += qty * price
        else:
            logger.error(f'Cannot sell unowned position (shorting not supported). Ticker: {ticker}')

    def _update_price(self, ticker, price):
        if ticker in self.positions:
            self.positions[ticker]._update_price(price)
