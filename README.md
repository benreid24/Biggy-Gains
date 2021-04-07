# Biggy Gains
Biggy Gains is a trading bot being developed by myself and my friend Chris just for fun. This repository contains the environment layer used by the
bots to interact with their world, as well as the bots themselves. Live trading and live paper trading will be done with [Alpaca](https://alpaca.markets/).

## Setup
Create virtual environment:
```
virtualenv venv
```
Activate your virtual environment:
```
# Windows
source venv/Scripts/activate
```
```
# Linux/OSX
source venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Run tests:
```
python -m unittest discover -s tests
```
## Running
Biggy Gains is organized into two main components; `Environment` and `Bot`. `Environment` is the main interaction point between the `Bot` and the
real world. This allows historical back-testing, live paper trading, and live trading to all be done without any code change in the bot being used.
All that needs to be done is swap the Environment. Both the `Environment` and `Bot` are specified as command line options. 

### Configuration
The following options are able to be set through environment variables or the command line. Values passed in via the command line always override
values in environment variables.

- `REDDIT_KEY` (`--reddit-key`): Key id used to connect to Reddit. Required for `LiveEnvironment`
- `REDDIT_SECRET` (`--reddit-secret`): Key secret used to connect to Reddit. Required for `LiveEnvironment`
- `ALPACA_URL` (`--alpaca-url`): Endpoint to make trades through. Paper or live. Required for `LiveEnvironment`
- `ALPACA_KEY` (`--alpaca-key`): Key id to connect to Alpaca with. Required for `LiveEnvironment`
- `ALPACA_SECRET` (`--alpaca-secret`): Key secret to connect to Alpaca with. Required for `LiveEnvironment`

Run `python main.py --help` for full configuration options.

### Starting Biggy Gains
Biggy gains may be ran with the following command:
```
python main.py [configuration parameters] <environment> <bot> <datastore>
```
Environment is one of:
- `live`: Live environment. Connects to Reddit and Alpaca and supports both real and paper trading
- More to come...

Bot is one of:
- `ben_sentiment_bot`: Gathers sentiment data from Reddit and trades the most positive securities
- More to come...

Datastore is one of:
- `memory`: In memory datastore with no persistence. Good for testing
- More to come...

## Tools
Due to the need for labeled data sets and trained models several tools are contained within this repository. Implemented so far are:
- [Reddit Comment Collector](tools/reddit/collector.py): Collects Reddit comments in realtime and saves them to a JSON file. Run with `python collector.py [options]`
- [Reddit Comment Labeler](tools/reddit/labeler.py): Takes collected comments and prompts the user for ticker and sentiment information. Run with `python labeler.py <comment file>`
