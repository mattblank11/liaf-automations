# Import Packages
import os
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import datetime as dt
import time
from time import sleep
import json
from dateutil.relativedelta import relativedelta
# AWS
import boto3
from s3fs.core import S3FileSystem
from io import StringIO
s3_fs = S3FileSystem(
  anon=False,
  key=os.environ['aws_access_key_id'],
  secret=os.environ['aws_secret_access_key'],
)
s3_boto = boto3.resource(
  's3', 
  aws_access_key_id=os.environ['aws_access_key_id'],
  aws_secret_access_key=os.environ['aws_secret_access_key'],
)
# REQUESTS
import requests
# SLACK
import slack
slack_token = os.getenv('mattybot_slack_token')
# SHEETS
import pygsheets
# MailChimp
import mailchimp3
from mailchimp3 import MailChimp
# Twitter
import tweepy