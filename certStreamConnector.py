import sys
import threading

import certstream

from filter import Filter


class CertStream(threading.Thread):

    def __init__(self, shared_storage):
        threading.Thread.__init__(self)
        self.shared_storage = shared_storage
        self.thread = None
        self.stopped = True

    def push_to_filter(self, message, context):
        if self.stopped:
            sys.exit()
        Filter.process(message, self.shared_storage)

    def start(self):
        self.thread = threading.Thread(target=self.consume)
        self.thread.daemon = True
        self.thread.start()
        print("CertStream started")

    def stop(self):
        self.stopped = True
        self.thread.join()

    def consume(self):
        self.stopped = False
        certstream.listen_for_events(self.push_to_filter, url='wss://certstream.calidog.io/')

