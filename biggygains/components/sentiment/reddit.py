import logging
import json
import datetime
import typing
import re

import praw

from biggygains.environment.interface import Environment
from .interface import Sentiment, SentimentSource

logger = logging.getLogger(__name__)
alnum = re.compile('[^a-zA-Z\d\s]+')


class Comment:
    def __init__(self, id, comment, ticker, sentiment):
        self.id = id
        self.comment = comment
        self.ticker = ticker
        self.sentiment = sentiment

    @classmethod
    def from_dict(d):
        return Comment(d['id'], d['comment'], d['ticker'], d['sentiment'])

    def to_dict(self):
        return {
            'id': self.id,
            'comment': self.comment,
            'ticker': self.ticker,
            'sentiment': self.sentiment
        }


class DayComments:
    def __init__(self, date: datetime.date, data: dict=None):
        self.date = date
        self.data = {}
        if data:
            self.data = {
                key: Comment.from_dict(value)
                for key, value in data.items()
            }

    @classmethod
    def from_dict(d):
        return DayComments(d['date'], d['data'])

    def to_dict(self):
        return {
            'date': self.date,
            'data': self.data
        }

    def add_comment(self, date: datetime.date, comment: Comment) -> typing.Dict[str, Sentiment]:
        if date == self.date:
            self.data[comment.id] = comment
            return None
        elif self.date < date:
            logger.info(f'Comment from future date ({date}), clearing stored comments')
            aggregate = self.aggregate()
            self.data = {comment.id: comment}
            return aggregate

    def aggregate(self) -> typing.Dict[str, Sentiment]:
        sentiment = {}
        for comment in self.data:
            if comment.ticker in sentiment:
                sentiment[comment.ticker]['value'] += comment.sentiment
                sentiment[comment.ticker]['count'] += 1
            else:
                sentiment[comment.ticker] = {
                    'value': comment.sentiment,
                    'count': 1
                }
        return {
            ticker: Sentiment(ticker, val['value'] / val['count'], val['count'])
            for ticker, val in sentiment.items()
        }


class RedditSentimentSource(SentimentSource):
    def __init__(self, key, secret):
        super().__init__()
        self.key = key
        self.secret = secret
        self.comments = DayComments(datetime.date.today())
        self.past_days = []
        self.env = None

    def update(self, env: Environment):
        ts = {}
        for day_data in [self.comments.aggregate()] + self.past_days:
            pass # TODO - merge in self.sentiment

    def initialize(self, env: Environment):
        self.env = env

        try:
            self.api = praw.Reddit(
                client_id=self.key,
                client_secret=self.secret,
                user_agent='Biggy-Gains by u/ilikecheetos42'
            )
            # TODO - subscribe and setup callback

            # TODO - load comments from datastore and init with aggregate()
            stored_comments = env.datastore.retrieve_data('reddit_comments')
            if stored_comments:
                self._load_from_store(stored_comments)
            else:
                self._load_from_reddit()

            self.update(env)

        except Exception:
            logger.exception('Failed to initialize reddit feed')
            return False
        return True

    def _load_from_store(self, stored):
        pass

    def _load_from_reddit(self):
        pass

    def _analyze_comment(self, comment: praw.models.Comment):
        # callback. on add_comment handle past days aggregate
        pass
    
    def _extract_ticker(self, comment: str):
        words = alnum.sub('', comment).split()
        possible = [word for word in words if word.isupper() and len(word) in [3, 4]]

        tickers = [ticker for ticker in possible if self.env.ticker_exists(ticker)]
        tickers = set(tickers)
        if len(tickers) == 1:
            return tickers[0]

        # See if maybe they included a ticker not capitalized
        maybe = [word for word in words if len(word) in [3, 4] and word not in possible]
        tickers = [ticker for ticker in maybe if self.env.ticker_exists(ticker.upper())]
        tickers = set(tickers)
        if len(tickers) == 1:
            return tickers[0].upper()

        # TODO - maybe consider searching for company names
        return None
