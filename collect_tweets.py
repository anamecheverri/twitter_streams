#!/usr/bin/env python
""" Collect Tweets
collect twitters and push to CSV file
"""
import urllib2
import oauth2
import settings_mine as settings
from query import query_url, query

# add authentication tokens
OAUTH_TOKEN = oauth2.Token(key=settings.access_token_key, secret=settings.access_token_secret)
OAUTH_CONSUMER = oauth2.Consumer(key=settings.api_key, secret=settings.api_secret)

# add signature method
SIGNATURE_METHOD = oauth2.SignatureMethod_HMAC_SHA1()

# create handlers
HANDLER_HTTP  = urllib2.HTTPHandler()
HANDLER_HTTPS = urllib2.HTTPSHandler()

def main():
    tweets = get_twitters(query_url)
    for tweet in tweets:
        write_to_csv(tweet)

def get_twitters(twitter_url, parameters=[]):
    # create the request object
    request = oauth2.Request

    # add the consumer and token to the request
    request = request.from_consumer_and_token(
        OAUTH_CONSUMER,
        token=OAUTH_TOKEN,
        http_method='POST',
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
    return url_director.open(twitter_url, 'track={}'.format(query))

def write_to_csv(tweet):
    print tweet


if __name__ == "__main__":
    main()

