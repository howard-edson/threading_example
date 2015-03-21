#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module: threaded.py
# *** WRITTEN FOR PYTHON3 ***
"""
Example of using threading in python3 to download multiple images
concurrently from imgur. Because this is an IO-bound task, threading 
speeds execution significantly.

(Because of the GIL in cpython, threading will not speed up CPU-bound 
tasks like file compression.)
"""

from queue import Queue
from threading import Thread
from time import time
import os
import logging
from download import setup_download_dir, get_links, download_link
from secrets import get_secret

IMGUR_CLIENT_ID = get_secret('IMGUR_CLIENT_ID')
LOG_FILE = 'results.log'

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            directory, link = self.queue.get() # get a task from the queue
            download_link(directory, link)     # execute the task
            self.queue.task_done()             # signal completion

def main():
    ts = time()
    client_id = IMGUR_CLIENT_ID
    if not client_id:
        raise Exception("Need a valid IMGUR_CLIENT_ID to use the API!")
    download_dir = setup_download_dir()
    # get only image links from the API
    links = [l for l in get_links(client_id) if l.endswith('.jpg')]
    # Create a queue to communicate with the worker threads
    queue = Queue()  
    for x in range(8):
        # Create 8 worker threads
        logging.info('Starting thread %s', x)
        worker = DownloadWorker(queue)
        # main thread can exit even though workers are blocked
        worker.daemon = True
        worker.start()
    # Create a task in the queue for each image link
    for link in links:
        logger.info('Queueing {}'.format(link))
        queue.put((download_dir, link))
    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    print('Execution time: {} seconds.'.format(time() - ts))

if __name__ == '__main__':
    main()