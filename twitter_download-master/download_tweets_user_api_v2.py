import sys
import os
import time
import datetime
import argparse
import io

from twitter import *

parser = argparse.ArgumentParser(description="downloads tweets")
parser.add_argument('--partial', dest='partial', default=None)
parser.add_argument('--dist', dest='dist', default=None, type=argparse.FileType('r'), required=True)
parser.add_argument('--output', dest='output')
parser.add_argument('--user', dest='output_user', action='store_true')

args = parser.parse_args()
partial = None
output = io.open(args.output + "_semeval_tweets.txt", 'w', encoding='UTF-8')
if args.partial != None:
    partial = io.open(args.partial + "_semeval_tweets.txt", 'r', encoding='UTF-8')
partial_user = None
if args.output_user:
    output_user = io.open(args.output + "_semeval_userinfo.txt", 'w', encoding='UTF-8')
    if args.partial != None:
        partial_user = io.open(args.partial + "_semeval_userinfo.txt", 'r', encoding='UTF-8')

CONSUMER_KEY = 'JEdRRoDsfwzCtupkir4ivQ'
CONSUMER_SECRET = 'PAbSSmzQxbcnkYYH2vQpKVSq2yPARfKm0Yl6DrLc'

MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
if not os.path.exists(MY_TWITTER_CREDS):
    oauth_dance("Semeval sentiment analysis", CONSUMER_KEY, CONSUMER_SECRET, MY_TWITTER_CREDS)
oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
t = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

cache = {}
user_cache = {}
if partial != None:
    for line in partial:
        fields = line.strip().split("\t")
        text = fields[-1]
        sid = fields[0]
        cache[sid] = text
    partial.close()
if partial_user != None:
    for line in partial_user:
        fields = line.strip().split("\t")
        sid = fields[0]
        user_cache[sid] = line
    partial_user.close()


files = [
    'twitter-2013train-A.txt',
    'twitter-2014sarcasm-A.txt',
    'twitter-2014test-A.txt',
    'twitter-2015test-A.txt',
    'twitter-2015train-A.txt',
    'twitter-2016dev-A.txt',
    'twitter-2016devtest-A.txt',
    'twitter-2016test-A.txt',
    'twitter-2016train-A.txt'
]

for filename in files:
    with open('4-English_train_dev/Subtask_A/' + filename) as f:
        dist_lines = f.readlines()

    # dist_lines = args.dist.readlines()
    ids = [line.split()[0] for line in dist_lines]

    def batches(ids, size=100):
        start, stop = 0, size
        while True:
            try:
                ids[start]
            except IndexError:
                return
            else:
                yield ids[start:stop]
        # while stop < len(ids):
        #     yield ids[start:stop]
            start = stop
            stop += size

    from itertools import izip_longest

    def grouper(iterable, n, fillvalue=None):
        "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    results = []

    for batch in batches(ids):

        try:
            response = t.statuses.lookup(_id=','.join(batch))
            results.extend(response)
            for item in response:
                print item

            with open(filename + '-output.txt', 'a') as f:
                print>>f, repr(list(response))
            # for status, _ in zip(response, ids):
                # text = status['text'].replace('\n', ' ').replace('\r', ' ')
                # cache[sid] = text
                # if args.output_user:
                #     user = status['user']
                #     user_string = sid + '\t' + user['id_str'] + '\t' + (str(user['followers_count']) or '') + '\t' + (
                #         str(user['statuses_count']) or '') + '\t"' + (user['description'] or '') + '"\t' + (
                #                       str(user['friends_count']) or '') + '\t"' + (user['location'] or '') + '"\t' + (
                #                       user['lang'] or '') + '\t"' + (user['name'] or '') + '" \t' + (
                #                       user['time_zone'] or '') + '\t'
                #     user_cache[sid] = user_string

        except TwitterError as e:
            if e.e.code == 429:
                rate = t.application.rate_limit_status()
                reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
                now = datetime.datetime.today()
                future = datetime.datetime.fromtimestamp(reset)
                seconds = (future - now).seconds + 1
                if seconds < 10000:
                    sys.stderr.write("Rate limit exceeded, sleeping for %s seconds until %s\n" % (seconds, future))
                    time.sleep(seconds)
            else:
                cache[sid] = 'Not Available'
                user_cache[sid] = 'Not Available'
    #
    # for line in args.dist:
    #     fields = line.strip().split('\t')
    #     sid = fields[0]
    #     uid = fields[1]


        #
        # while not sid in cache or not sid in user_cache:
        #     try:
        #         status = t.statuses.show(_id=sid)
        #         text = status['text'].replace('\n', ' ').replace('\r', ' ')
        #         cache[sid] = text
        #         if args.output_user:
        #             user = status['user']
        #             user_string = sid + '\t' + user['id_str'] + '\t' + (str(user['followers_count']) or '') + '\t' + (
        #             str(user['statuses_count']) or '') + '\t"' + (user['description'] or '') + '"\t' + (
        #                           str(user['friends_count']) or '') + '\t"' + (user['location'] or '') + '"\t' + (
        #                           user['lang'] or '') + '\t"' + (user['name'] or '') + '" \t' + (
        #                           user['time_zone'] or '') + '\t'
        #             user_cache[sid] = user_string
        #
        #     except TwitterError as e:
        #         if e.e.code == 429:
        #             rate = t.application.rate_limit_status()
        #             reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
        #             now = datetime.datetime.today()
        #             future = datetime.datetime.fromtimestamp(reset)
        #             seconds = (future - now).seconds + 1
        #             if seconds < 10000:
        #                 sys.stderr.write("Rate limit exceeded, sleeping for %s seconds until %s\n" % (seconds, future))
        #                 time.sleep(seconds)
        #         else:
        #             cache[sid] = 'Not Available'
        #             user_cache[sid] = 'Not Available'
        #
        # text = cache[sid]
        # output.write(unicode("\t".join(fields + [text])) + '\n')
        # if args.output_user:
        #     user_string = user_cache[sid]
        #     output_user.write(unicode(user_string) + '\n')
    # output.close()
    # if output_user != None:
    #     output_user.close()

    with open(filename + '-full.txt', 'w') as f:
        print>>f, repr(results)

    from ast import literal_eval
