import unittest

from biggygains.environment import portfolio as port


class PositionTests(unittest.TestCase):
    def test_cost_value_pnl(self):
        pos = port.Position('AAPL', 100, 300, 400)

        self.assertEqual(pos.ticker, 'AAPL')
        self.assertEqual(pos.qty, 100)
        self.assertEqual(pos.value(), 40000)
        self.assertEqual(pos.cost(), 30000)
        self.assertEqual(pos.pnl(), 10000)

    def test_buy(self):
        pos = port.Position('BEN', 100, 50, 100)
        pos.buy(100, 100)

        self.assertEqual(pos.qty, 200)
        self.assertEqual(pos.avg_price, 75)
        self.assertEqual(pos.cost(), 15000)
        self.assertEqual(pos.value(), 20000)
        self.assertEqual(pos.pnl(), 5000)

    def test_sell(self):
        pos = port.Position('BEN', 100, 50, 100)
        pos.sell(50)

        self.assertEqual(pos.cost(), 2500)
        self.assertEqual(pos.value(), 5000)
        self.assertEqual(pos.qty, 50)


class PortfolioTests(unittest.TestCase):
    def test_buy(self):
        pf = port.Portfolio(10000)
        pf.buy('BEN', 100, 50)

        self.assertEqual(pf.cash, 5000)
        self.assertEqual(pf.value(), 10000)

    def test_sell(self):
        pf = port.Portfolio(5000)
        pf.add_position(port.Position('BEN', 100, 50, 50))
        pf.sell('BEN', 50, 50)

        self.assertEqual(pf.cash, 7500)
        self.assertEqual(pf.value(), 10000)

    def test_pnl(self):
        pf = port.Portfolio(10000)
        pf.buy('A', 100, 50)
        pf.buy('B', 50, 100)

        pf.update_price('A', 100)
        pf.update_price('B', 75)

        self.assertEqual(pf.pnl(), 3750)
        self.assertEqual(pf.value(), 13750)
        self.assertEqual(pf.cash, 0)
