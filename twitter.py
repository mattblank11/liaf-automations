# Import packages
from settings import *
from google_sheets import (
    update_csv,
)

'''
twitter.py

Summary:
- Handles tasks associated with retrieving data from Twitter API

Methods:
- authorize_account()
- get_follower_count()
- get_tweet_count()
- get_tweet_impression()
'''

'''
Method: instantiate_api()

Summary: Returns an instance of the Twitter API
'''
def instantiate_api():
    # Define API variables
    consumer_key = os.environ['twitter_consumer_key']
    consumer_secret = os.environ['twitter_consumer_secret']
    access_token_key = os.environ['twitter_access_token_key']
    access_token_secret = os.environ['twitter_access_token_secret']

    # Authorize Twitter API
    auth = tweepy.OAuthHandler(
        consumer_key,
        consumer_secret,
    )

    auth.set_access_token(
        access_token_key,
        access_token_secret,
    )
    
    api = tweepy.API(auth)
    
    return api

'''
Method: get_twitter_stats()

Summary: Returns a dictionary of stats about my Twitter account from today
'''
def get_twitter_stats():
    # Instantiate Twitter API
    api = instantiate_api()
    
    # Define Twitter handle
    twitter_handle = 'CodeWithMatt'

    metrics = api.get_user(twitter_handle)
    followers = metrics.followers_count
    tweets = metrics.statuses_count

    twitter_data = {
        'Date': dt.datetime.now().strftime('%m/%d/%Y'),
        'Followers': followers,
        'Tweets': tweets,
    }

    update_csv(
        'Twitter Followers',
        twitter_data,
    )

    return twitter_data

print(get_twitter_stats())