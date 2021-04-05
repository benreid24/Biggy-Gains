from __future__ import annotations # Non runtime type checking

import logging
import typing

if typing.TYPE_CHECKING:
    from environment.interface import Environment

logger = logging.getLogger('Bot.interface')


"""
This is the base class for each bot. It provides the interface that is used by the
active environment to control the bot.
"""
class Bot:
    def initialize(self, environment: Environment) -> bool:
        """
        Initialize the bot with the given environment. Return false on error
        """

        logger.error(f'initialize() is unimplemented in {type(self).__name__}')
        return False

    def shutdown(self, environment: Environment):
        """
        This is called when the bot is shutting down. This is the place to persist
        data needed for future runs
        """
        logger.warning(f'shutdown() is unimplemented in {type(self).__name__}')

    def update(self, environment: Environment):
        """
        Perform all update logic. Buy stocks, sell stocks, watch sentiment, etc.
        This is generally called once per minute but the period may be changed
        """

        logger.error(f'initialize() is unimplemented in {type(self).__name__}')
