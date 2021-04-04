import logging
import json
import datetime
import typing
import re
import threading

import praw

from biggygains.environment.interface import Environment
from .interface import Sentiment, SentimentSource, SentimentAnalyzer

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
    _DATA_PERSIST_KEY = 'RedditSentimentSource_persistence_v1'

    def __init__(self, analyzer: SentimentAnalyzer, key: str, secret: str, subs: typing.List[str]):
        super().__init__()
        self.analyzer = analyzer
        self.key = key
        self.secret = secret
        self.subs = subs
        self.comments = DayComments(datetime.date.today())
        self.past_days = []
        self.env = None
        self.lock = threading.Lock()
        self.running = True

    def update(self, env: Environment):
        ts = {}
        self.lock.acquire()

        self.sentiment = {}
        for day_data in [self.comments.aggregate()] + self.past_days:
            for ticker, sentiment in day_data.items():
                if ticker in self.sentiment:
                    self.sentiment[ticker].append(sentiment)
                else:
                    self.sentiment[ticker] = [sentiment]
        
        self.lock.release()

    def initialize(self, env: Environment):
        self.env = env

        try:
            self.api = praw.Reddit(
                client_id=self.key,
                client_secret=self.secret,
                user_agent='Biggy-Gains by u/ilikecheetos42'
            )
            self.subreddit = self.api.subreddit('+'.join(self.subs))
            self.thread = threading.Thread(target=self._background_listener)

            stored_comments = env.datastore.retrieve_data(RedditSentimentSource._DATA_PERSIST_KEY)
            if stored_comments:
                self._load_from_store(stored_comments)
            else:
                self._load_from_reddit()

            self.update(env)
            self.thread.start()

        except Exception:
            logger.exception('Failed to initialize reddit feed')
            return False
        return True

    def _analyze_comment(self, comment: praw.models.Comment):
        ticker = self._extract_ticker(comment.body)
        if ticker:
            sentiment = self.analyzer.analyze(comment.body)
            agg = self.comments.add_comment(
                datetime.date.fromtimestamp(comment.created_utc),
                Comment(comment.id, comment.body, ticker, sentiment)
            )
            if agg: # new day
                self.past_days.insert(0, agg)
                self.past_days = self.past_days[0:5] # Keep 4 days + current

    def _load_from_store(self, stored):
        data = json.loads(stored)
        if 'past' in data:
            self.past_days = [
                {
                    ticker: Sentiment.from_dict(d)
                    for ticker, d in day.items()
                } for day in data['past']
            ]
        if 'today' in data:
            self.comments = DayComments.from_dict(data['today'])

    def _load_from_reddit(self):
        for post in self.subreddit.new(limit=500):
            for comment in post.comments.list():
                self._analyze_comment(comment)
    
    def _extract_ticker(self, comment: str):
        words = alnum.sub('', comment).split()
        possible = [word for word in words if word.isupper() and len(word) in [3, 4]]

        tickers = [ticker for ticker in possible if self.env.ticker_exists(ticker)]
        tickers = list(set(tickers))
        if len(tickers) == 1:
            return tickers[0]

        # See if maybe they included a ticker not capitalized
        maybe = [word for word in words if len(word) in [3, 4] and word not in possible]
        tickers = [ticker for ticker in maybe if self.env.ticker_exists(ticker.upper())]
        tickers = list(set(tickers))
        if len(tickers) == 1:
            return tickers[0].upper()

        # TODO - maybe consider searching for company names
        return None

    def shutdown(self, env: Environment):
        self.running = False
        self.thread.join()
        
        past_data = [
            {
                ticker: sentiment.to_dict()
                for ticker, sentiment in day.items()
            } for day in self.past_days
        ]
        data = {
            'past': past_data,
            'today': self.comments.to_dict()
        }
        env.datastore.store_data(RedditSentimentSource._DATA_PERSIST_KEY, json.dumps(data))

    def _background_listener(self):
        try:
            for comment in self.subreddit.stream.comments():
                if not self.running:
                    break

                try:
                    self.lock.acquire()
                    self._analyze_comment(comment)
                    self.lock.release()
                except Exception:
                    logger.exception(f'Error processing comment: {comment.body}')
        except Exception:
            logger.exception('Error streaming reddit comments')
