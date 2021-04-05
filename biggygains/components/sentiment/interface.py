from __future__ import annotations # Non runtime type checking

import typing
import logging

if typing.TYPE_CHECKING:
    from environment.interface import Environment

logger = logging.getLogger('SentimentSource.interface')


"""
Basic data pair class for storing sentiment on a ticker. Sentiment value
is in the range [-1, 1] with higher being more positive. Confidence is
intended to be the number of supporting data points but can be any value
to indicate confidence, so long as all confidence values are computed
in the same way
"""
class Sentiment:
    def __init__(self, ticker, value, confidence):
        self.ticker = ticker
        self.value = value
        self.confidence = confidence

    @staticmethod
    def from_dict(d: dict) -> Sentiment:
        return Sentiment(d['ticker'], d['value'], d['confidence'])

    def to_dict(self) -> dict:
        return {
            'ticker': self.ticker,
            'value': self.value,
            'confidence': self.confidence
        }

    def __cmp__(self, other):
        return cmp(self.value, other.value)


"""
Base class for sentiment sources (reddit, etc). Current sentiment is stored in
self.sentiment. Derived classes may store sentiment however necessary but must
ensure that self.sentiment remains up to date
"""
class SentimentSource:
    def __init__(self):
        self.sentiment = {}

    def initialize(self, environment: Environment) -> bool:
        """
        Initialize any resources the source needs. This method may not take any
        parameters. Required parameters should be passed in the child constructor
        """

        logger.warning(f'initialize() is unimplemented in {type(self).__name__}')
        pass

    def shutdown(self, environment: Environment):
        """
        This is called when the bot is shutting down. This is the place to persist
        data needed for future runs
        """
        logger.warning(f'shutdown() is unimplemented in {type(self).__name__}')

    def update(self, environment: Environment):
        """
        Update sentiment based on new data. This is called by the environment and
        is generally called at least once per minute
        """

        logger.warning(f'update() is unimplemented in {type(self).__name__}')
        pass

    def get_sentiment(self, ticker) -> typing.List[Sentiment]:
        """
        Returns sentiment for a given ticker, or None if no data. Entries in list represent
        past dates of data. Item 0 is today and each subsequent item is further in the past.
        Indices do not necessarily correspond to days
        """

        if ticker in self.sentiment:
            return self.sentiment[ticker]
        return None

    def get_all_sentiment(self) -> typing.Dict[str, typing.List[Sentiment]]:
        """
        Returns a map of all sentiment data over time
        """

        return self.sentiment


"""
Base class for different sentiment analysis engines
"""
class SentimentAnalyzer:
    def analyze(self, message: str) -> int:
        """
        Return -1 for negative sentiment, 0 for neutral, and 1 for positive
        """

        logger.warning(f'analyze is unimplemented in {type(self).__name__}')
        return 0
