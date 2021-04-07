import argparse
import json
import os

import praw

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reddit-key', type=str, default=os.environ.get('REDDIT_KEY'), help='The key id for accessing Reddit data')
    parser.add_argument('--reddit-secret', type=str, default=os.environ.get('REDDIT_SECRET'), help='The key secret for accessing Reddit data')
    parser.add_argument('--reddit-subs', type=str, default='wallstreetbets', help='Subreddits formatted as "sub1+sub2+sub3"')
    parser.add_argument('output_file', type=str, help='File to read existing comments from and save new comments to')
    args = parser.parse_args()

    if not args.reddit_key:
        print('Reddit key is required. Pass in or set env REDDIT_KEY')
        return
    if not args.reddit_secret:
        print('Reddit secret is required. Pass in or set env REDDIT_SECRET')
        return
    
    api = praw.Reddit(
        client_id=args.reddit_key,
        client_secret=args.reddit_secret,
        user_agent='Biggy-Gains by u/ilikecheetos42'
    )
    feed = api.subreddit(args.reddit_subs)

    comments = {}

    try:
        with open(args.output_file, 'r') as f:
            comments = json.loads(f.read())
    except:
        pass

    try:
        for comment in feed.stream.comments():
            if comment.id not in comments:
                comments[comment.id] = {
                    'body': comment.body,
                    'sentiment': 0
                }
            print(f'Captured {len(comments)} unique comments')
    finally:
        with open(args.output_file, 'w') as f:
            f.write(json.dumps(comments))
        print('Wrote file')



if __name__ == '__main__':
    main()
