import numpy as np

from PostProcessingIO import readForceFile2
from PostProcessingIO import fftAnalysis
from PostProcessingIO import getIndices



##### OPENFOAM v1706 changend the standard of the forces output file

class Forces2:

    _TIME = 0
    _TOTAL_X = 1
    _TOTAL_Y = 2
    _TOTAL_Z = 3
    _PRESSURE_X = 4
    _PRESSURE_Y = 5
    _PRESSURE_Z = 6
    _VISCOUS_X = 7
    _VISCOUS_Y = 8
    _VISCOUS_Z = 9
    _path = ""
    _startTime = 0
    _endTime = 10

    # TODO overload the constructor
    # TODO catch if user provides faulty start/endtime!!!
    # TODO implement calcCoefficients
    # FIX reimplement calcFFT

    def __init__(self, path, startTime = 0, endTime = 0, Average = True, StdDev = True, FFT = False, Verbose = False):

        if startTime > endTime:
            raise Exception("invalid syntax in __init__: startTime > endTime")

        self._path = path
        self._startTime = startTime
        self._endTime = endTime
        self._verbose = Verbose

        try:
            self._forces = readForceFile2(path, startTime, endTime)
        except IOError:
            print("could not read file: " + path)
            self._forces = None

        if Verbose == True: print("successully parsed file :" + self._path)

        if Average == True:
            self._calcAverages(startTime, endTime)
            if Verbose == True: print("successfully calculated averages")

        if StdDev == True:
            self._calcStdDev(startTime, endTime)
            if Verbose == True: print("successfully calculated StdDev")

        if FFT == True:
            self._calcFFT(startTime, endTime)
            if Verbose == True: print("successfully calculated FFT")

    def reRead(self, path, startTime = 0, endTime = 10):
        del(self._forces)
        if startTime > endTime:
            raise Exception("invalid syntax in __init__: startTime > endTime")
        self._path = path
        self._startTime = startTime
        self._endTime = endTime

        try:
            self._forces = readForceFile2(path, startTime, endTime)
        except:
            print("could not read file: " + path)
            self._forces = None


    def _calcAverages(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        if self._verbose == True: print(startIndex, endIndex)
        self._averageForces = np.array([np.average(force) for force in self._forces[self._TOTAL_X:,startIndex:endIndex]])
        return self._averageForces

    def _calcStdDev(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._stdDevs = [np.std(force) for force in self._forces[self._TOTAL_X:,startIndex:endIndex]]
        return self._stdDevs

    def _calcFFT(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._FFTs = [ fftAnalysis(self._forces[self._TIME,startIndex:endIndex], data) for data in self._forces[self._TOTAL_X:,startIndex:endIndex] ]
        return self._FFTs


    def _calcCoefficients(self, rho = 1.0, u = 1.0, A = 2.0):
        pass

    def _calcMax(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._maxForces = np.array([np.max(force) for force in self._forces[self._TOTAL_X:,startIndex:endIndex]])
        return self._maxForces

    def _calcMin(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._minForces = np.array([np.min(force) for force in self._forces[self._TOTAL_X:,startIndex:endIndex]])
        return self._minForces

    def _calcMaxIndex(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._maxForcesPos = np.array([np.argmax(force) for force in self._forces[self._TOTAL_X:,startIndex:endIndex]])
        return self._maxForcesPos

    def _calcMinINdex(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._minForcesPos = np.array([np.argmin(force) for force in self._forces[self._TOTAL_X:,startIndex:endIndex]])
        return self._minForcesPos

### GETTER FUNCTIONS
    def getViscousForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        return self._forces[self._VISCOUS_X:self._VISCOUS_Z + 1,startIndex:endIndex]

    def getPressureForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        return self._forces[self._PRESSURE_X:self._PRESSURE_Z + 1,startIndex:endIndex]

    # TODO zip viscous and pressure and return sum
    def getTotalForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        return self._forces[self._TOTAL_X:self._TOTAL_Z+1,startIndex:endIndex]

    def getTimes(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        return self._forces[self._TIME,startIndex:endIndex]

    def getViscousForcesAverages(self):
        if hasattr(self, "_averageForces"):
            return self._averageForces[self._VISCOUS_X:self._VISCOUS_Z+1]
        else:
            return self._calcAverages(self._startTime, self._endTime)[self._VISCOUS_X:self._VISCOUS_Z+1]

    def getPressureForcesAverages(self):
        if hasattr(self, "_averageForces"):
            return self._averageForces[self._PRESSURE_X:self._PRESSURE_Z+1]
        else:
            return self._calcAverages(self._startTime, self._endTime)[self._PRESSURE_X:self._PRESSURE_Z+1]

    def getTotalForcesAverages(self):
        if hasattr(self, "_averageForces"):
            return self._averageForces[self._TOTAL_X-1:self._TOTAL_Z]
        else:
            return self._calcAverages(self._startTime, self._endTime)[self._TOTAL_X-1:self._TOTAL_Z]

    def getEndTime(self):
        latestIndex = len(self._forces[self._TIME,:]) - 1
        if self._verbose == True: print ("latest index: ", latestIndex)
        return self._forces[self._TIME,latestIndex]

    def getStartTime(self):
        return self._forces[self._TIME,0]

    def getFFT(self):
        if hasattr(self, "_FFTs"):
            return self._FFTs
        else:
            self._calcFFT(self._startTime, self._endTime)
            return self._FFTs

