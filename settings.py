# Import Packages
import os
import csv
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import datetime as dt
import time
from time import sleep
from itertools import groupby
import json
from dateutil.relativedelta import relativedelta
from itertools import product
import traceback
# SELENIUM
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
# AWS
import boto3
from s3fs.core import S3FileSystem
from io import StringIO
# REQUESTS
import requests
# SLACK
import slack
slack_token = os.environ["MATTYBOT_SLACK_TOKEN"]
# SHEETS
import pygsheets
# MailChimp
import mailchimp3
from mailchimp3 import MailChimp
# Twitter
import tweepy