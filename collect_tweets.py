#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Collect Tweets
collect twitters and push to CSV file
"""
import os
import urllib2
import oauth2
import json
import datetime

from csv import DictWriter, QUOTE_MINIMAL


# this is to turn on my settings.
import settings_mine as settings
#import settings
# these are tc14 queries (included)
import query_tc14 as query
#import query

# Mon Sep 15 23:10:29 +0000 2014
DATETIME_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'
DATETIME_FORMAT_OUT = '%m/%d/%Y %H:%M:%S'
# turn on or off DEBUG
DEBUG = False

# add authentication tokens
OAUTH_TOKEN = oauth2.Token(key=settings.access_token_key, secret=settings.access_token_secret)
OAUTH_CONSUMER = oauth2.Consumer(key=settings.api_key, secret=settings.api_secret)

# add signature method
SIGNATURE_METHOD = oauth2.SignatureMethod_HMAC_SHA1()

# create handlers
HANDLER_HTTP = urllib2.HTTPHandler(debuglevel=DEBUG)
HANDLER_HTTPS = urllib2.HTTPSHandler(debuglevel=DEBUG)

def main():
    print "Collecting tweets for {track}".format(**query.track)
    tweets = get_twitters(query.twitter_url, parameters=query.track)

    # the filename is set in the query.py settings
    # write headers if the file does not exist
    write_headers = True
    write_opts = 'wb'

    if os.path.isfile(query.filename):
        write_headers = False
        write_opts = 'ab'
    csv_writer = None

    for tweet in tweets:
        tweet = json.loads(tweet)
        #todo: add the csv writer and json to row
        row = flatten_json(tweet)

        # setup CSV writer if is DNE
        if csv_writer is None:
            csv_writer = DictWriter(open(query.filename, write_opts), fieldnames=row.keys(), quoting=QUOTE_MINIMAL)
        # write header row
        if write_headers:
            csv_writer.writeheader()
            write_headers = False
        csv_writer.writerow(row)


def get_twitters(twitter_url, parameters=[], http_method='POST'):
    # create the request object
    request = oauth2.Request()

    # add the consumer and token to the request
    request = request.from_consumer_and_token(
        OAUTH_CONSUMER,
        token=OAUTH_TOKEN,
        http_method=http_method,
        http_url=twitter_url,
        parameters=parameters
        )

    # add signature to method    
    request.sign_request(SIGNATURE_METHOD, OAUTH_CONSUMER, OAUTH_TOKEN)

    # make sure to grab headers!
    headers = request.to_header()

    # now make the request
    request_url = request.to_url()

    # create url directors
    url_director = urllib2.OpenerDirector()

    # add the HANDLERS
    url_director.add_handler(HANDLER_HTTP)
    url_director.add_handler(HANDLER_HTTPS)

    # return the url director, after opening
    return url_director.open(twitter_url, request.to_postdata())

def flatten_json(json_in):
    row = {}
    for key, element in json_in.items():
        if type(element) is list: continue
        if type(element) is dict: continue
        row[key] = element

    # now add geo location
    geo = {'latitude': None, 'longitude': None}
    if json_in['geo'] is not None:
        # make sure we even have coordinates
        if json_in['geo'].has_key('coordinates'):
            coordinates = json_in['geo']['coordinates']
            geo['latitude'] = coordinates[0]
            geo['longitude'] = coordinates[1]

    # remove the geo
    if row.has_key('geo'): del row['geo']

    # add the geo coordinates to the row
    row.update(geo)

    # fix created at, turn it from locale to something Tableau works well with
    row['created_at'] = datetime.datetime.strptime(row['created_at'], DATETIME_FORMAT).strftime(DATETIME_FORMAT_OUT)

    # make sure text does not contain EOLs
    row['text'] = row['text'].replace('\n', ' ').replace('\r', ' ')

    bad_rows = ['source']
    # be sure to remove bad rows
    for bad_row in bad_rows:
        del row[bad_row]

    # uber-pro-tip: convert dictionary to unicode to escape all unicode issues
    uni_row = {unicode(k).encode('utf-8'): unicode(v).encode('utf8') for k, v in row.items()}


    return uni_row

if __name__ == "__main__":
    main()

