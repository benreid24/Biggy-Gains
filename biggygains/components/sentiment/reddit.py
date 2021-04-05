import logging
import json
import datetime
import typing
import re
import threading

import praw

from biggygains.environment.interface import Environment
from .interface import Sentiment, SentimentSource, SentimentAnalyzer

logger = logging.getLogger('RedditSentimentSource')
alnum = re.compile('[^a-zA-Z\d\s]+')


"""
Storage class for a reddit comment and its sentiment. Ids are stored to
prevent duplication of comments
"""
class Comment:
    def __init__(self, id, comment, ticker, sentiment):
        self.id = id
        self.comment = comment
        self.ticker = ticker
        self.sentiment = sentiment

    @staticmethod
    def from_dict(d):
        return Comment(d['id'], d['comment'], d['ticker'], d['sentiment'])

    def to_dict(self):
        return {
            'id': self.id,
            'comment': self.comment,
            'ticker': self.ticker,
            'sentiment': self.sentiment
        }


"""
Container class for a days worth of comments. Comments for the active day are
used to evaluate current sentiment. Past days of sentiment only stored
aggregated. Today's comments are individually stored
"""
class DayComments:
    def __init__(self, date: datetime.date):
        self.date = date
        self.data = {}

    @staticmethod
    def from_dict(d):
        return DayComments(datetime.date.fromisoformat(d['date']), d['data'])

    def to_dict(self):
        data = {
            cid: comment.to_dict()
            for cid, comment in self.data.items()
        }
        return {
            'date': self.date.isoformat(),
            'data': data
        }

    def add_comment(self, date: datetime.date, comment: Comment) -> typing.Dict[str, Sentiment]:
        """
        Adds a comment to todays set. If the comment is from a future date the internal
        data is reset and the aggregated data for the day is returned
        """

        if date == self.date:
            self.data[comment.id] = comment
            return None
        elif self.date < date:
            logger.info(f'Comment from future date ({date}), clearing stored comments')
            aggregate = self.aggregate()
            self.data = {comment.id: comment}
            return aggregate

    def aggregate(self) -> typing.Dict[str, Sentiment]:
        """
        Returns a minified aggregation of comment data into sentiment data
        """

        sentiment = {}
        for comment in self.data.values():
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


"""
Collector and aggregator of reddit sentiment data
"""
class RedditSentimentSource(SentimentSource):
    _DATA_PERSIST_KEY = 'RedditSentimentSource_persistence_v1'
    _LOOKBACK_PERIOD = 5 # TODO - increase when not testing
    _VALID_TICKER_LENGTHS = [3, 4]

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
        logger.info('Initializing reddit sentiment source')
        self.env = env

        try:
            self.api = praw.Reddit(
                client_id=self.key,
                client_secret=self.secret,
                user_agent='Biggy-Gains by u/ilikecheetos42'
            )
            self.subreddit = self.api.subreddit('+'.join(self.subs))
            self.thread = threading.Thread(target=self._background_listener)
            logger.info('Connected to reddit api')

            logger.info('Loading stored comments')
            stored_comments = env.datastore.retrieve_data(RedditSentimentSource._DATA_PERSIST_KEY)
            if stored_comments:
                self._load_from_store(stored_comments)
            
            logger.info('Loading new reddit posts')
            self._load_from_reddit()

            self.update(env)
            self.thread.start()
            logger.info('Started background listener for new comments')

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
        def handle_comment(self, comment):
            if isinstance(comment, praw.models.MoreComments):
                for c in comment.comments():
                    handle_comment(c)
            else:
                self._analyze_comment(comment)

        for post in self.subreddit.new(limit=RedditSentimentSource._LOOKBACK_PERIOD):
            for comment in post.comments.list():
                handle_comment(self, comment)
    
    def _extract_ticker(self, comment: str):
        words = alnum.sub('', comment).split()
        possible = [word for word in words if word.isupper() and len(word) in RedditSentimentSource._VALID_TICKER_LENGTHS]

        tickers = [ticker for ticker in possible if self.env.ticker_exists(ticker)]
        tickers = list(set(tickers))
        if len(tickers) == 1:
            return tickers[0]
        if len(tickers) > 1:
            return None # No sense identifying lowercase tickers when many real uppercase

        # See if maybe they included a ticker not capitalized
        maybe = [word for word in words if len(word) in RedditSentimentSource._VALID_TICKER_LENGTHS]
        tickers = [ticker for ticker in maybe if self.env.ticker_exists(ticker.upper())]
        tickers = list(set(tickers))
        if len(tickers) == 1:
            return tickers[0].upper()

        # TODO - maybe consider searching for company names
        return None

    def shutdown(self, env: Environment):
        try:
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
        except Exception:
            logger.exception('Error cleaning up Reddit sentiment source')

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
