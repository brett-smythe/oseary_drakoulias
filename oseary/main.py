# Currently written to only be sinle threaded and single instanced. If this is
# changed the limitation checks will also need to be re-written
from multiprocessing import Process, Queue

from oseary.jobs.twitter import jobs, utils


def test():
    twitter_unames = utils.get_tracked_twitter_usernames()
    print twitter_unames


def run_service():
    # Start multiprocessing instances here
    service_running = True
    while service_running:
        
    print 'Run service'

