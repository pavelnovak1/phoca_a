import sys
import threading

import phoca_main as p


class Phoca(threading.Thread):

    def __init__(self, domain_storage, output_file):
        self.domain_storage = domain_storage
        self.output_file = output_file
        self.thread = None
        self.stopped = True
        self.crawled = set()

    def start(self):
        self.thread = threading.Thread(target=self.process)
        self.thread.daemon = True
        self.stopped = False
        self.thread.start()
        print("Phoca started")

    def stop(self):
        self.stopped = True
        self.thread.join()

    def process(self):
        detector = p.Detector(outputFile=self.output_file)
        while not self.stopped:
            if self.domain_storage.size() == 0:
                continue
            domain = self.domain_storage.pop()
            if domain in self.crawled:
                print(f"Domain {domain} already checked. Skipping...")
                continue
            print(f"Crawling domain {domain}")
            print(f"Queue length: {self.domain_storage.size()}")
            detector.crawl([domain])
            self.crawled.add(domain)
        sys.exit(1)
