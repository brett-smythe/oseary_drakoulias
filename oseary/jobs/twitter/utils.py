import datetime

import requests

from pymemcache.client.base import Client as MemCacheClient
from pymemcache.exceptions import ( MemcacheServerError,
    MemcacheUnexpectedCloseError
)

from oseary.settings import oseary_settings
from oseary.creds import config as creds_config
from oseary import utils

from aquatic_twitter import client as twitter_client


epoch_time = datetime.datetime(1970,1,1)

module_logger = utils.get_logger(__name__)
logger = utils.MultiProcessCheckingLogger(module_logger)

class TwitterLimits(object):
    """
    Checks against either the twitter API or memcached twitter API results for
    twitter API requests limits
    """
    def __init__(self, timeline_rate_reserve=5, multi_proc_logger=None):
        """
        The reserve arguments are how many requests to hold back on to leave
        some form of buffer in place with regards to API limits
        """
        
        if multi_proc_logger:
            self.logger = multi_proc_logger
            print 'MP logger!'
        else:
            self.logger = utils.MultiProcessCheckingLogger(module_logger)
        
        self.memcacheClient = MemCacheClient(
            (oseary_settings.memcache_host, oseary_settings.memcache_port)
        )

        self.twitterClient = twitter_client.AquaticTwitter(
            creds_config.twitter_consumer_key,
            creds_config.twitter_consumer_secret,
            creds_config.twitter_access_token_key,
            creds_config.twitter_access_token_secret
        )

        self.timeline_rate_reserve = timeline_rate_reserve

        self.tl_total_reqs = oseary_settings.twitter_timeline_requests
        self.tl_reqs_left = oseary_settings.twitter_timeline_req_left
        self.tl_reqs_reset_time = oseary_settings.twitter_timeline_reset_time

        self.update_limits()

    def update_limits(self):
        """
        Update the limits associated with the twitter api

        First attempts to check memcache and then checks directly with the
        twitter API
        """
        self.logger.debug(__name__, 'Updating twitter limits')
        self.cache_tl_total_reqs = self.memcacheClient.get('timeline_limit')
        if self.cache_tl_total_reqs:
            self.tl_total_reqs = int(self.cache_tl_total_reqs)

        self.cache_tl_reqs_left = self.memcacheClient.get('timeline_remaining')
        if self.cache_tl_reqs_left:
            self.tl_reqs_left = int(self.cache_tl_reqs_left)

        self.cache_tl_reqs_reset_time = self.memcacheClient.get(
            'timeline_reset'
        )
        if self.cache_tl_reqs_reset_time:
            self.tl_reqs_reset_time = int(self.cache_tl_reqs_reset_time)
            self.utc_now = datetime.datetime.utcnow()
            self.utc_secs = (self.utc_now - epoch_time).total_seconds()
            self.secs_until_reset = self.tl_reqs_reset_time - self.utc_secs
            if self.secs_until_reset <= 0:
                # Force getting rates from twitter
                self.tl_reqs_reset_time = None

        self.update_values_valid = (
            self.tl_total_reqs and
            self.tl_reqs_left and
            self.tl_reqs_reset_time
        )
        
        if not self.update_values_valid:
            self.update_vals = self.twitterClient.get_user_timeline_rate_limit()
            self.tl_total_reqs = self.update_vals.limit
            self.tl_reqs_left = self.update_vals.remaining
            self.tl_reqs_reset_time = self.update_vals.reset

    def get_sleep_between_jobs(self):
        """
        Calculate the sleep time between jobs as to not run into the twitter
        API limits
        """
        self.update_limits()
        self.logger.debug(__name__, 'Updating sleep time between jobs')
        self.utc_now = datetime.datetime.utcnow()
        self.utc_secs = (self.utc_now - epoch_time).total_seconds()
        self.logger.debug(__name__, 'UTC in seconds {0}'.format(self.utc_secs))
        self.secs_until_reset = self.tl_reqs_reset_time - self.utc_secs
        self.logger.debug(__name__, 'Seconds until API reset {0}'.format(self.secs_until_reset))
        self.buffered_tl_reqs_left = (
            self.tl_reqs_left - self.timeline_rate_reserve
        )
        self.logger.debug(__name__, 'Buffered timeline requests left {0}'.format(self.buffered_tl_reqs_left))
        self.sleep_time = self.secs_until_reset / self.buffered_tl_reqs_left
        self.logger.debug(__name__, 'Sleep time {0}'.format(self.sleep_time))
        return self.sleep_time


def get_tracked_twitter_usernames():
    """
    Get the usernames that are being tracked on twitter
    """
    logger.debug('Getting tracked twitter user names')
    request_url = 'http://{0}:5000/twitter-tl-user/'.format(
        oseary_settings.eleanor_host
    )
    request_data = requests.get(request_url)
    tracked_twitter_unames = request_data.json()['tracked_twitter_usernames']

    return tracked_twitter_unames

