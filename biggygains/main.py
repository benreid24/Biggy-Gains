import argparse
import logging
import sys
import enum

from bots.interface import Bot
from environment.interface import Environment


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


def main():
    """
    This is the main entrypoint of the bot utility. It will read command line
    arguments to select the desired bot and environment to start. Secrets may
    be read from the system environment, TBD.
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('env_type', type=EnvironmentType, choices=list(EnvironmentType), help='The name of the environment to run in')
    parser.add_argument('bot_type', type=BotType, choices=list(BotType), help='The name of the bot to run')
    args = parser.parse_args()


if __name__ == '__main__':
    main()
