from __future__ import annotations # Non runtime type checking

import typing
import logging

if typing.TYPE_CHECKING:
    from biggygains.environment.interface import Environment

logger = logging.getLogger(__name__)


"""
Basic data pair class for storing sentiment on a ticker. Sentiment value
is in the range [-1, 1] with higher being more positive. Confidence is
intended to be the number of supporting data points but can be any value
to indicate confidence, so long as all confidence values are computed
in the same way
"""
class Sentiment:
    def __init__(self, ticker, value, confidence, source: SentimentSource):
        self.ticker = ticker
        self.value = value
        self.confidence = confidence
        self.source = source

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

    def update(self, environment: Environment):
        """
        Update sentiment based on new data. This is called by the environment and
        is generally called at least once per minute
        """

        logger.warning(f'update() is unimplemented in {type(self).__name__}')
        pass

    def get_sentiment(self, ticker) -> Sentiment:
        """
        Returns sentiment for a given ticker, or None if no data
        """

        if ticker in self.sentiment:
            return self.sentiment[ticker]
        return None

    def get_all_sentiment(self) -> typing.Dict[str, Sentiment]:
        """
        Returns a map of all sentiment data
        """

        return self.sentiment
