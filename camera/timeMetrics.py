import time

class timeMetrics:

    def __init__(self):
        self._start = 0.0
        self.tMax = 0.0
        self.tAverage = 0.0
        self.tCycle = 0.0
        self.nSamples = 0

    def newCycle(self):
        self._start = time.time()
        return self

    def endCycle(self):
        self.tCycle = time.time() - self._start
        self.tAverage = ( (self.nSamples * self.tAverage) + self.tCycle ) / (self.nSamples + 1)
        self.nSamples += 1
        if self.tMax < self.tCycle:
            self.tMax = self.tCycle

        return self

    def toString(self):
        txt = "Execution Times (this / avg / max): {t1:.6f} msec / {t2:.6f} msec / {t3:.6f} msec"
        return txt.format(t1=self.tCycle, t2=self.tAverage, t3=self.tMax)
