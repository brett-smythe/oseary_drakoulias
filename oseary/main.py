# Currently written to only be sinle threaded and single instanced. If this is
# changed the limitation checks will also need to be re-written
from time import sleep
from multiprocessing import Process, Queue

from oseary.jobs.twitter import jobs, utils
from oseary.settings import oseary_settings


def test():
    twitter_unames = utils.get_tracked_twitter_usernames()
    print twitter_unames


def run_service():
    # Start multiprocessing instances here
    service_running = True
    twitter_jobs_queue = Queue()
    twitter_jobs_worker = Process(
        target=jobs.TwitterJobs, args=(twitter_jobs_queue,)
    )
    twitter_jobs_worker.start()
    while service_running:
        # Some call to check if the service should keep running
        sleep(0.5)
    twitter_jobs_queue.put(oseary_settings.process_poison)
    twitter_jobs_worker.join()

