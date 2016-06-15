import requests

from oseary.settings import oseary_settings
# If this service ever moves from a single thread the limits check must changed
# to be more thread safe

class TwitterLimits(object):

    def __init__(self, timeline_rate_reserve=5):
        self.timeline_rate_reserve = timeline_rate_reserve
        self.timeline_requests_left = 0
        self.update_limits()

    def update_limits(self):
        # TODO rewrite
        # Api call to get relevant information
        requests_left = 95
        self.timeline_requests_left = requests_left - self.timeline_rate_reserve
        return None

    def get_sleep_between_jobs(self):
        # TODO rewrite
        # Twitter requests amount totals are reset every 15 minutes
        self.twitter_requests_window = 15 * 60
        tracked_users = get_tracked_twitter_usernames()
        sleep_time = self.twitter_requests_window / self.timeline_requests_left
        return sleep_time


def get_tracked_twitter_usernames():
    request_url = 'http://{0}:5000/twitter-tl-user/'.format(
        oseary_settings.eleanor_host
    )
    request_data = requests.get(request_url)
    tracked_twitter_unames = request_data.json()['tracked_twitter_usernames']

    return tracked_twitter_unames

