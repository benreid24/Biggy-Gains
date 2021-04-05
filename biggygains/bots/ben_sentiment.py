import logging

from .interface import Bot
from environment.interface import Environment

logger = logging.getLogger('BenSentimentBot')


class BenSentimentBot(Bot):
    def initialize(self, env: Environment):
        logger.info('Initializing the bot')
        return True

    def update(self, env: Environment):
        logger.info('Updating the bot')

    def shutdown(self, env: Environment):
        logger.info('Bot is shutting down')
