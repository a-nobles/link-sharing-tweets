#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 10:09:16 2020

@author: anobles
"""
import argparse
import logging
import gzip
import jsonlines
import requests

def _confirm_org(tweet):
    # ensure tweet is not a RT or QT
    if 'retweeted_status' not in tweet.keys() and tweet['is_quote_status'] == False:
        return True
    else:
        return False


def read_tweets_gz(tweet_file):
    # read input tweets
    tweets = []
    with jsonlines.Reader(gzip.open(tweet_file)) as reader:
        count = 0
        for tweet in reader.iter(skip_empty=True, skip_invalid=True):
            # confirm that the tweet is org
            if _confirm_org(tweet) == True:
                tweets.append(tweet)
            count+=1
            if count % 10000 == 0:
                logging.info('succesfully made it through tweets: %d', count)
    return tweets


def extract_urls(tweet):
    # extract urls
    if tweet['expanded_urls'] != []:
        # find urls that don't contain twitter.com
        no_twitter_urls = [url for url in tweet['expanded_urls'] if "twitter.com" not in url]
        if no_twitter_urls != []:
            return no_twitter_urls
    else:
        return []


def extract_ids_urls(tweets):
    # extract tweet ids
    processed_data = []
    for tweet in tweets:
        processed_tweet = {}
        # check to see if there is a field for urls
        if tweet['entities']['urls'] != []:
            # if so, grab all of the expanded urls that are not twitter.com
            expanded_urls = [url['expanded_url'] for url in tweet['entities']['urls'] if "twitter.com" not in url['expanded_url']]
            # if we have anything leftover, save out the ids and urls
            if expanded_urls != []:
                processed_tweet['id_str'] = tweet['id_str']
                processed_tweet['urls'] = expanded_urls
                processed_data.append(processed_tweet)
    count = len(processed_data)
    logging.info('succesfully found tweets with urls: %d', count)
    return processed_data


def request_urls(processed_data):
    # request urls
    # loop through the list of dictionaries containing processed results
    count = 0
    for data in processed_data:
        # put i a request to get the full url
        status_codes = []
        return_request_urls = []
        for entry_url in data['urls']:
            try:
                # get the url and status code
                r = requests.head(entry_url, timeout=10, allow_redirects=True)
                status_codes.append(r.status_code)
                return_request_urls.append(r.url)
            except:
                status_codes.append('error')
                return_request_urls.append('error')
        data['status_codes'] = status_codes
        data['return_request_urls'] = return_request_urls
        count+=1
        if count % 1000 == 0:
            logging.info('succesfully made it through data points: %d', count)
    return processed_data


def save_results(processed_data, out_fn):
    # save results
    with open(out_fn, 'w') as fout:
        for entry in processed_data:
            fout.write((json.dumps(entry) + '\n'))
    logging.info('succesfully wrote files')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", metavar="logging file",
                        help="Path to logging file")
    parser.add_argument("in_tweet_file", metavar="tweet-input-file",
                        help="Path to tweets input file. Accepts json.gz.")
    parser.add_argument("out_results_file", metavar="tweet-output-file",
                        help="Path to results output file. Outputs json.")
    return parser.parse_args()



if __name__ == "__main__":
    # parse the args
    args = parse_arguments()

    # set up logging
    logging.basicConfig(filename=args.log_file, format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)

    # read tweets
    tweets = read_tweets_gz(args.in_tweet_file) # server

    # extract urls and ids
    processed_data = extract_ids_urls(tweets)

    # get requested urls and status codes
    processed_data = request_urls(processed_data)

    # save the results
    save_results(processed_data, args.out_results_file)
