from biggygains.environment.interface import Environment
from biggygains.trading.impl.alpaca import AlpacaPricingSource, AlpacaTradeInterface
from biggygains.components.sentiment.reddit import RedditSentimentSource
from biggygains.components.sentiment.interface import SentimentAnalyzer


"""
A live environment. Makes real (or paper) trades and gets data from the real
world. Runs in realtime. Components can still be changed via the Environment
"""
class LiveEnvironment(Environment):
    def __init__(self, reddit_key, reddit_secret, reddit_subs, alp_url, alp_key, alp_secret):
        self.set_trade_interface(AlpacaTradeInterface(alp_key, alp_secret, alp_url))
        self.set_pricing_source(AlpacaPricingSource(alp_key, alp_secret, alp_url))
        self.connect_sentiment_source(RedditSentimentSource(SentimentAnalyzer(), reddit_key, reddit_secret, reddit_subs))
        # TODO - Configure sentiment analyzer from args

    def _initialize(self):
        # Custom setup?
        return True
