# Currently written to only be sinle threaded and single instanced. If this is
# changed the limitation checks will also need to be re-written
import sys
from time import sleep
from multiprocessing import Process, Queue

from oseary.jobs.twitter import jobs, utils as twitter_utils
from oseary.settings import oseary_settings
from oseary import utils


logger = utils.get_logger(__name__)


def test():
    """
    Test invocation function for quick dev testing, will later be removed
    """
    twitter_unames = twitter_utils.get_tracked_twitter_usernames()
    print twitter_unames


def run_service():
    """
    The main entry point for the oseary service, starts and maintains all of
    the various timing jobs
    """
    logger.info('Starting Oseary service')
    service_running = True
    logging_queue = Queue()
    workerLogger = utils.MultiProcessLogger(logging_queue, logger)
    twitter_jobs_queue = Queue()
    twitter_jobs_worker = Process(
        target=jobs.TwitterJobs, args=(twitter_jobs_queue, logging_queue)
    )
    twitter_jobs_worker.start()
    while service_running:
        try:
            # Some call to check if the service should keep running
            workerLogger.write_log_messages()
            sleep(0.5)
        except KeyboardInterrupt as e:
            print 'Shutting down Oseary...'
            break
    logger.info('Shutting down Oseary service')
    twitter_jobs_queue.put(oseary_settings.process_poison)
    twitter_jobs_worker.join()

