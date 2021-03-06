import tkinter as tk
import argparse
import json
import re
import sys
import os

from alpaca_trade_api import REST as Alpaca

sys.path.insert(0, os.path.abspath('../../'))
from biggygains.components.sentiment.reddit import RedditSentimentSource

alnum = re.compile('[^a-zA-Z\d\s]+')
sentiments = [
    ('Very Positive', 2),
    ('Positive', 1),
    ('Neutral', 0),
    ('Negative', -1),
    ('Very Negative', -2)
]


class Dialog:
    Discarded = 'discard'
    Updated = 'update'
    Closed = 'close'
    Open = 'open'

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Label comment')
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.comment_label = tk.Label(self.root)
        self.comment_label.grid(row=0, column=0, columnspan=3)

        self.ticker_frame = tk.Frame(self.root, highlightbackground="black", highlightthickness=1)
        self.ticker_frame.grid(row=1, column=0)

        sentiment_frame = tk.Frame(self.root, highlightbackground="black", highlightthickness=1)
        self.sentiment = tk.IntVar()
        for s in sentiments:
            radio = tk.Radiobutton(sentiment_frame, text=s[0], variable=self.sentiment, value=s[1])
            radio.pack(anchor=tk.W)
        sentiment_frame.grid(row=1, column=1)

        button_frame = tk.Frame(self.root)
        but = tk.Button(button_frame, text='Save', command=self._save)
        but.pack()
        but = tk.Button(button_frame, text='Discard', command=self._discard)
        but.pack()
        button_frame.grid(row=1, column=2)

    def update(self, comment, remaining):
        self.comment = comment
        self.state = Dialog.Open
        text = comment['body']
        self.root.title(f'Label comment ({remaining} remaining)')
        self.comment_label.config(text=text)
        self.sentiment.set(comment['sentiment'] if 'sentiment' in comment else 0)

        words = alnum.sub('', text).split()
        tickers = [word for word in words if word.isupper() and len(word) in RedditSentimentSource._VALID_TICKER_LENGTHS]
        self.ticker = tk.StringVar(value=comment['ticker'] if 'ticker' in comment else '_other_')
        self.other_entry.delete(0, tk.END)
        self.other_entry.insert(0, self.ticker.get())

        for w in self.ticker_frame.winfo_children():
            w.destroy()

        ticker_label = tk.Label(self.ticker_frame, text='Ticker', borderwidth=1)
        ticker_label.pack(anchor=tk.NW)
        for ticker in tickers:
            radio = tk.Radiobutton(self.ticker_frame, text=ticker, variable=self.ticker, value=ticker)
            radio.pack(anchor=tk.W)
        radio = tk.Radiobutton(self.ticker_frame, text='Other', variable=self.ticker, value='_other_')
        radio.pack(anchor=tk.W)
        self.other_entry = tk.Entry(self.ticker_frame)
        self.other_entry.pack(anchor=tk.W)
        self.ticker_frame.grid(row=1, column=0)

    def _save(self):
        self.root.quit()
        self.comment['sentiment'] = self.sentiment.get()
        self.comment['ticker'] = self.ticker.get() if self.ticker.get() != '_other_' else self.other_entry.get()
        self.state = Dialog.Updated

    def _discard(self):
        self.root.quit()
        self.state = Dialog.Discarded

    def _on_close(self):
        self.root.destroy()
        self.state = Dialog.Closed

    def status(self):
        return self.state

    def prompt(self):
        self.root.mainloop()


class TickerFilter:
    def __init__(self, key, secret):
        self.api = Alpaca(key, secret, 'https://paper-api.alpaca.markets')
        self.cached_tickers = {}

    def ticker_exists(self, ticker):
        try:
            if ticker in self.cached_tickers:
                return self.cached_tickers[ticker]
            asset = self.api.get_asset(ticker)
            self.cached_tickers[ticker] = asset.tradable
            return asset.tradable
        except:
            self.cached_tickers[ticker] = False
            return False

    def filter_pass(self, comment):
        words = alnum.sub('', comment).split()
        tickers = [word for word in words if word.isupper() and len(word) in RedditSentimentSource._VALID_TICKER_LENGTHS]
        for word in words:
            if self.ticker_exists(word):
                return True
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='File to read existing comments from and write labeled comments to')
    parser.add_argument('--alpaca-key', type=str, default=os.environ.get('ALPACA_KEY'), help='The key id for interfacing with Alpaca')
    parser.add_argument('--alpaca-secret', type=str, default=os.environ.get('ALPACA_SECRET'), help='The key secret for interfacing with Alpaca')
    parser.add_argument('--skip-completed', default=False, action='store_true', help='Skips comments already labeled')
    parser.add_argument('--filter-no-ticker', default=False, action='store_true', help='True to filter out comments with no detected tickers')
    args = parser.parse_args()

    ticker_filter = None
    if args.filter_no_ticker:
        if not args.alpaca_key:
            print('--alpaca-key is required for --filter-no-ticker')
            return
        if not args.alpaca_secret:
            print('--alpaca-secret is required for --filter-no-ticker')
            return
        ticker_filter = TickerFilter(args.alpaca_key, args.alpaca_secret)

    comments = {}
    with open(args.input_file, 'r') as f:
        comments = json.loads(f.read())

    remaining = len(comments)
    dialog = Dialog()
    for comment_id in list(comments.keys()):
        remaining -= 1
        
        if args.skip_completed and 'ticker' in comments[comment_id]:
            continue
        if ticker_filter:
            if not ticker_filter.filter_pass(comments[comment_id]['body']):
                print(f'Filtering comment with no ticker: {comments[comment_id]["body"]}')
                comments.pop(comment_id, None)
                continue
        
        dialog.update(comments[comment_id], remaining)
        dialog.prompt()

        if dialog.status() == Dialog.Closed:
            break
        if dialog.status() == Dialog.Discarded:
            comments.pop(comment_id, None)

    with open(args.input_file, 'w') as f:
        f.write(json.dumps(comments))


if __name__ == '__main__':
    main()
