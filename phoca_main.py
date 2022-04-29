import sys, os, concurrent.futures
import json
import pickle
from tqdm import tqdm
from pandas import DataFrame
from probes.timingProbes import *
from probes.featureProbes import *

sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'probes'))




class Detector:
    timingProbes = [
        tcpSYNTiming,
        tlsClientHelloTiming,
        tlsClientHelloErrorTiming,
        tlsHandshakeTiming,
        httpsGetRequestTiming,
        httpGetRequestTiming,
        httpGetRequestErrorTiming,
        httpsGetRequestErrorTiming,
        httpGetRequestNoHostHeaderTiming,
        httpsGetRequestNoHostHeaderTiming
    ]

    featureProbes = [
        TLSLibrary,
        TLSVersions,
    ]

    def __init__(self, http_port=80, https_port=443, numIterations=10,
                 modelFile="./classifier.cls", rawData=False,
                 outputFile=None, outputFormat="csv"):

        self.http_port = http_port
        self.https_port = https_port
        self.numIterations = numIterations
        self.modelFile = modelFile
        self.outputFile = outputFile
        self.outputFormat = outputFormat
        self.rawData = rawData
        self.model = pickle.load(open(self.modelFile, 'rb'))

    def crawl(self, domains):
        crawlResults = {}

        with concurrent.futures.ThreadPoolExecutor(10) as executor:
            for result in self.tqdm_parallel_map(executor, self.testSite, domains):
                crawlResults[result['site']] = {'classification': result['classification'],
                                                'data': result['data']}
                if (self.outputFile == None and not self.rawData):
                    if (len(domains) == 1):
                        print(result['classification'])
                    else:
                        print(f"{result['site']}: {result['classification']}")

        self.writeResultsToFile(crawlResults)

    def testSite(self, site):
        result = {'site': site}
        result['data'] = self.probeSite(site)
        result['classification'] = self.classifySite(result['data'])

        return result

    def classifySite(self, recordings):
        classification = None

        recordingsDataFrame = DataFrame([recordings])
        columnsToDrop = [column for column in recordingsDataFrame if column not in self.model.feature_names]
        recordingsDataFrame = recordingsDataFrame.drop(columnsToDrop, axis=1)
        if (recordingsDataFrame.isna().sum().sum() > 0):
            return classification

        recordingsDataFrame = recordingsDataFrame.reindex(sorted(recordingsDataFrame.columns), axis=1)

        try:
            classification = self.model.predict(recordingsDataFrame)[0]
        except Exception as e:
            print(e)

        return classification

    def probeSite(self, site):
        probeResults = {'site': site}

        # Place all feature probes into threadpool queue
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        featureProbeThreads = []
        for probe in Detector.featureProbes:
            featureProbeThreads.append(executor.submit(probe(site, self.http_port, self.https_port).test))

        # On the main thread, loop through the timing threads so the main thread does something
        # while the feature threads are running
        for probe in Detector.timingProbes:
            currentProbeResults = probe(site, self.http_port, self.https_port).test(n=self.numIterations)
            probeResults[probe.__name__] = currentProbeResults

        # Compute the additional timing features
        probeResults['httpsGetSynRatio'] = probeResults['httpsGetRequestTiming'] / probeResults['tcpSYNTiming']
        probeResults['httpGetSynRatio'] = probeResults['httpGetRequestTiming'] / probeResults['tcpSYNTiming']
        probeResults['httpsGetErrorSynRatio'] = probeResults['httpsGetRequestErrorTiming'] / probeResults[
            'tcpSYNTiming']
        probeResults['httpGetErrorSynRatio'] = probeResults['httpGetRequestErrorTiming'] / probeResults['tcpSYNTiming']
        probeResults['httpGetHttpGetErrorRatio'] = probeResults['httpGetRequestTiming'] / probeResults[
            'httpGetRequestErrorTiming']
        probeResults['httpsGetHttpsGetErrorRatio'] = probeResults['httpsGetRequestTiming'] / probeResults[
            'httpsGetRequestErrorTiming']

        # Collect the results of the feature threads
        for thread in featureProbeThreads:
            try:
                probeResults.update(thread.result(timeout=60))
            except Exception as e:
                raise e
                probeResults.update({})

        executor.shutdown(wait=False)
        return probeResults

    def writeResultsToFile(self, siteResults):
        f = open(self.outputFile, 'a')
        for key in siteResults.keys():
            if (not self.rawData):
                del siteResults[key]['data']

        json.dump(siteResults, f)
        f.write('\n')
        f.close()

    def tqdm_parallel_map(self, executor, fn, *iterables, **kwargs):
        futures_list = []
        results = []
        for iterable in iterables:
            futures_list += [executor.submit(fn, i) for i in iterable]
        if (len(futures_list) > 1 and self.outputFile):
            for f in tqdm(concurrent.futures.as_completed(futures_list), total=len(futures_list), **kwargs):
                yield f.result()
        else:
            for f in concurrent.futures.as_completed(futures_list):
                yield f.result()
