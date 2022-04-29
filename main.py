import time

from certStreamConnector import CertStream
from phocaConnector import Phoca
from sharedStorage import Storage


def main():
    output_file = "C:\\Users\\novakpav\\Documents\\PhocaCrawler\\phoca_test.txt"
    domainStorage = Storage()

    cert_stream = CertStream(domainStorage)
    phoca = Phoca(domainStorage, output_file)

    cert_stream.start()
    phoca.start()
    while True:
        time.sleep(1)
if __name__ == "__main__":
    main()
