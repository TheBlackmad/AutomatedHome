import time

class timeMetrics:
    '''
        This class represents the access to a shared memory area where all other modules
        such as capture, view, recording can access to perform their jobs.
    '''
    def __init__(self):
        '''
            This routine initializes the object for time Metrics.

            Args:
                None

            Returns:
                None

            Raises:
                None
        '''
        self._start = 0.0
        self.tMax = 0.0
        self.tAverage = 0.0
        self.tCycle = 0.0
        self.nSamples = 0

    def newCycle(self):
        '''
            This routine sets the start of a new cycle.

            Args:
                None

            Returns:
                self

            Raises:
                None
        '''
        self._start = time.time()
        return self

    def endCycle(self):
        '''
            This routine sets the end of the current cycle.

            Args:
                None

            Returns:
                self

            Raises:
                None
        '''
        self.tCycle = time.time() - self._start
        self.tAverage = ( (self.nSamples * self.tAverage) + self.tCycle ) / (self.nSamples + 1)
        self.nSamples += 1
        if self.tMax < self.tCycle:
            self.tMax = self.tCycle

        return self

    def toString(self):
        '''
            This routine returns a string with the execution times
            (current / average / maximum)

            Args:
                None

            Returns:
                string with the execution times since object was created

            Raises:
                None
        '''
        txt = "Execution Times (this / avg / max): {t1:.6f} msec / {t2:.6f} msec / {t3:.6f} msec"
        return txt.format(t1=self.tCycle, t2=self.tAverage, t3=self.tMax)
