# src/templates/workerprocess.py
import multiprocessing

class WorkerProcess(multiprocessing.Process):
    def __init__(self, queueList):
        super(WorkerProcess, self).__init__()
        self.daemon=True
        self.queuesList = queueList
        self.threads = []

    def run(self):
        for thread in self.threads:
            thread.start()
        while True:
            pass
