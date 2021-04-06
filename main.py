import argparse
import logging
import os
import enum

from biggygains.bots.interface import Bot
from biggygains.bots.ben_sentiment import BenSentimentBot
from biggygains.environment.interface import Environment
from biggygains.environment.live import LiveEnvironment
from biggygains.datastore.memory import InMemoryDatastore


"""
Enum storing available bot types for argument parsing
"""
class BotType(enum.Enum):
    BenSentimentBot = 'ben_sentiment_bot'
    # More

    def __str__(self):
        return self.value


"""
Enum storing available environments for argument parsing
"""
class EnvironmentType(enum.Enum):
    Live = 'live'
    # More

    def __str__(self):
        return self.value


"""
Enum storing available datastores
"""
class DatastoreType(enum.Enum):
    InMemory = 'memory'
    # More. Maybe distributed Redis?

    def __str__(self):
        return self.value


def main():
    """
    This is the main entrypoint of the bot utility. It will read command line
    arguments to select the desired bot and environment to start. Secrets may
    be read from the system environment, TBD.
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('env_type', type=EnvironmentType, choices=list(EnvironmentType), help='The name of the environment to run in')
    parser.add_argument('bot_type', type=BotType, choices=list(BotType), help='The name of the bot to run')
    parser.add_argument('datastore', type=DatastoreType, choices=list(DatastoreType), help='Underlying datastore to use to persist runtime data')

    parser.add_argument('--reddit-key', type=str, default=os.environ.get('REDDIT_KEY'), help='The key id for accessing Reddit data')
    parser.add_argument('--reddit-secret', type=str, default=os.environ.get('REDDIT_SECRET'), help='The key secret for accessing Reddit data')
    parser.add_argument('--reddit-subs', type=str, default='wallstreetbets', help='Subreddits formatted as "sub1+sub2+sub3"')
    parser.add_argument('--alpaca-url', type=str, default=os.environ.get('ALPACA_URL'), help='The Alpaca endpoint to trade through (paper vs live)')
    parser.add_argument('--alpaca-key', type=str, default=os.environ.get('ALPACA_KEY'), help='The key id for interfacing with Alpaca')
    parser.add_argument('--alpaca-secret', type=str, default=os.environ.get('ALPACA_SECRET'), help='The key secret for interfacing with Alpaca')

    # TODO - datastore parameters (connection info etc)

    parser.add_argument('--clear-datastore', default=False, action='store_true', help='Clear the datastore of all data before starting the bot')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Logging verbosity')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=args.log_level)
    logger = logging.getLogger('main')

    datastore = None
    if args.datastore == DatastoreType.InMemory:
        datastore = InMemoryDatastore()
    if not datastore:
        logger.critical('Failed to initialize datastore from options')
        return
    
    env = None
    if args.env_type == EnvironmentType.Live:
        if not args.reddit_key:
            print('--reddit-key is required for live environment')
        if not args.reddit_secret:
            print('--reddit-secret is required for live environment')
        if not args.alpaca_url:
            print('--alpaca-url is required for live environment')
        if not args.alpaca_key:
            print('--alpaca-key is required for live environment')
        if not args.alpaca_secret:
            print('--alpaca-secret is required for live environment')

        env = LiveEnvironment(
            args.reddit_key,
            args.reddit_secret,
            args.reddit_subs,
            args.alpaca_url,
            args.alpaca_key,
            args.alpaca_secret
        )
    if not env:
        logger.critical('Failed to initialize environment from options')
        return

    bot = None
    if args.bot_type == BotType.BenSentimentBot:
        bot = BenSentimentBot()
    if not bot:
        logger.critical('Failed to initialize bot from options')
        return

    env.set_datastore(datastore)
    env.connect_bot(bot)
    if not env.initialize(args.clear_datastore):
        logger.error('Failed to run environment initialization, exiting')
        return
    env.run()


if __name__ == '__main__':
    main()
