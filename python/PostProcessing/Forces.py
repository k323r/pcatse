# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 17:52:18 2017

@author: alsander
"""
import numpy as np

from PostProcessingIO import readForceFile
from PostProcessingIO import fftAnalysis
from PostProcessingIO import getIndices

class Forces:

    _TIME = 0
    _PRESSURE_X = 1
    _PRESSURE_Y = 2
    _PRESSURE_Z = 3
    _VISCOUS_X = 4
    _VISCOUS_Y = 5
    _VISCOUS_Z = 6
    _path = ""
    _startTime = 0
    _endTime = 10

    # TODO overload the constructor
    # TODO implement calcCoefficients
    # FIX reimplement calcFFT

    def __init__(self, path, startTime = 0, endTime = 10, Average = True, StdDev = True, FFT = False, Verbose = False):
        
        if startTime > endTime:
            raise Exception("invalid syntax in __init__: startTime > endTime")
        
        self._path = path        
        self._startTime = startTime
        self._endTime = endTime
        self._verbose = Verbose

        try:        
            self._forces = readForceFile(path, startTime, endTime)
        except:
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
            self._forces = readForceFile(path, startTime, endTime)
        except:
            print("could not read file: " + path)
            self._forces = None


    def _calcAverages(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        if self._verbose == True: print(startIndex, endIndex)
        self._averageForces = np.array([np.average(force) for force in self._forces[self._PRESSURE_X:,startIndex:endIndex]])
        return self._averageForces

    def _calcStdDev(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._stdDevs = [np.std(force) for force in self._forces[self._PRESSURE_X:,startIndex:endIndex]]
        return self._stdDevs

    def _calcFFT(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._FFTs = [ fftAnalysis(self._forces[self._TIME,startIndex:endIndex], data) for data in self._forces[self._PRESSURE_X:,startIndex:endIndex] ]
        return self._FFTs

    def _calcTotalForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._totalForces = np.array([
            self._forces[self._TIME,startIndex:endIndex],
            self._forces[self._PRESSURE_X,startIndex:endIndex] + self._forces[self._VISCOUS_X,startIndex:endIndex],
            self._forces[self._PRESSURE_Y,startIndex:endIndex] + self._forces[self._VISCOUS_Y,startIndex:endIndex],
            self._forces[self._PRESSURE_Z,startIndex:endIndex] + self._forces[self._VISCOUS_Z,startIndex:endIndex]])
        return self._totalForces

    def _calcTotalAverages(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        if (hasattr(self, "_averageForces")):
            self._totalAverageForces = np.array([
                self._averageForces[self._PRESSURE_X] + self._averageForces[self._VISCOUS_X],
                self._averageForces[self._PRESSURE_Y] + self._averageForces[self._VISCOUS_Y],
                self._averageForces[self._PRESSURE_Z] + self._averageForces[self._VISCOUS_Z]
            ])
        else:
            self._calcAverages(self._startTime, self._endTime)
            self._totalAverageForces = np.array([
                self._averageForces[self._PRESSURE_X] + self._averageForces[self._VISCOUS_X],
                self._averageForces[self._PRESSURE_Y] + self._averageForces[self._VISCOUS_Y],
                self._averageForces[self._PRESSURE_Z] + self._averageForces[self._VISCOUS_Z]
            ])
        return self._totalAverageForces

    def _calcCoefficients(self, rho = 1.0, u = 1.0, A = 2.0):
        pass

    def _calcMax(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._maxForces = np.array([np.max(force) for force in self._forces[self._PRESSURE_X:,startIndex:endIndex]])
        return self._maxForces

    def _calcMin(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._minForces = np.array([np.min(force) for force in self._forces[self._PRESSURE_X:,startIndex:endIndex]])
        return self._minForces

    def _calcMaxIndex(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._maxForcesPos = np.array([np.argmax(force) for force in self._forces[self._PRESSURE_X:,startIndex:endIndex]])
        return self._maxForcesPos

    def _calcMinINdex(self, start = 0, end = 0):
        startIndex, stopIndex = getIndices(self._forces[self._TIME,:], start, end)
        self._minForcesPos = np.array([np.argmin(force) for force in self._forces[self._PRESSURE_X:,startIndex:endIndex]])
        return self._minForcesPos

### GETTER FUNCTIONS
    @property
    def getViscousForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        return self._forces[self._VISCOUS_X:self._VISCOUS_Z + 1,startIndex:endIndex]

    @property
    def getPressureForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        return self._forces[self._PRESSURE_X:self._PRESSURE_Z + 1,startIndex:endIndex]

    # TODO zip viscous and pressure and return sum
    @property
    def getTotalForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        if hasattr(self, "_totalForces"):
            return self._totalForces[self._PRESSURE_X:, startIndex:endIndex]
        else:
            return self._calcTotalForces(start, end)[self._PRESSURE_X:, startIndex:endIndex]

    @property
    def getTimes(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[self._TIME,:], start, end)
        return self._forces[self._TIME,startIndex:endIndex]

    @property
    def getViscousForcesAverages(self):
        if hasattr(self, "_averageForces"):
            return self._averageForces[3:6]
        else:
            return self._calcAverages(self._startTime, self._endTime)[3:6]

    @property
    def getPressureForcesAverages(self):
        if hasattr(self, "_averageForces"):
            return self._averageForces[0:3]
        else:
            return self._calcAverages(self._startTime, self._endTime)[0:3]

    @property
    def getTotalForcesAverages(self):
        if hasattr(self, "_totalAverageForces"):
            return self._totalAverageForces[0:3]
        else:
            return self._calcTotalAverages(self._startTime, self._endTime)

    @property
    def getEndTime(self):
        latestIndex = len(self._forces[self._TIME,:]) - 1
        if self._verbose == True: print ("latest index: ", latestIndex)
        return self._forces[self._TIME,latestIndex]

    @property
    def getStartTime(self):
        return self._forces[self._TIME,0]

    @property
    def getFFT(self):
        if hasattr(self, "_FFTs"):
            return self._FFTs
        else:
            self._calcFFT(self._startTime, self._endTime)
            return self._FFTs


    
