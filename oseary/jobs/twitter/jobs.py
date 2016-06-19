import time

from interns.tasks import tasks as intern_tasks

from oseary.jobs.twitter import utils
from oseary.settings import oseary_settings


class TwitterJobs(object):
    
    def __init__(self, queue):
        self.queue = queue
        self.running = True

        self.twitterLimits = utils.TwitterLimits()
        self.sleep_secs = self.twitterLimits.get_sleep_between_jobs()
        self.last_execution_time = time.time() - self.sleep_secs

        self.tracked_twitter_users = utils.get_tracked_twitter_usernames()

        self.twitter_user_index = 0

        if len(self.tracked_twitter_users) == 0:
            self.running = False

        while self.running:
            if not self.queue.empty():
                poison_check = self.queue.get_nowait()
                if poison_check == oseary_settings.process_poison:
                    self.running = False
                    continue
            self.execute_next_job()

    def update_tracked_users(self):
        """
        Get tracked twitter usernames
        """
        self.tracked_twitter_users = utils.get_tracked_twitter_usernames()

    def get_user_timeline_tweets(self, username):
        """
        Pull the timeline tweets from username
        """
        intern_tasks.get_user_timeline_tweets(username)

    def execute_next_job(self):
        """
        Determines and runs the next fetch job, takes care of sleeping between
        jobs
        """
        self.time_to_execute = (
            (time.time() - self.last_execution_time) >= self.sleep_secs
        )
        if self.time_to_execute:
            if self.twitter_user_index >= len(self.tracked_twitter_users):
                self.twitter_user_index = 0
            self.username = self.tracked_twitter_users[self.twitter_user_index]
            self.get_user_timeline_tweets(self.username)
            self.last_execution_time = time.time()
            self.twitter_user_index += 1
        else:
            time.sleep(time.time() - self.last_execution_time)

