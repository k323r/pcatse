# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 17:52:18 2017

@author: alsander
"""
import numpy as np

from PostProcessinIO import readForceFile
from PostProcessinIO import fftAnalysis
from PostProcessinIO import getIndices

class Forces:
    
    _path = ""
    _startTime = 0
    _endTime = 10    

    # TODO overload the constructor
    # TODO implement getTotalForces
    # TODO implement calcMax
    # TODO implement calcMin
    # TODO implement calcMaxIndex
    # TODO implement calcMinINdex
    # TODO implement calcCoefficients
    # FIX reimplement calcFFT

    def __init__(self, path, startTime = 0, endTime = 1, Average = True, StdDev = True, FFT = False, Verbose = False):
        
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
    
    def reRead(self, path, startTime = 0, endTime = 1):
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
    
    def getTimes(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)          
        return self._forces[0,startIndex:endIndex]
    
    def _calcAverages(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)
        if self._verbose == True: print(startIndex, endIndex)
        self._averageForces = [np.average(force) for force in self._forces[1:,startIndex:endIndex]]
        return self._averageForces
        
    def _calcStdDev(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)
        self._stdDevs = [np.std(force) for force in self._forces[1:,startIndex:endIndex]]
        return self._stdDevs
        
    def _calcFFT(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)
        self._FFTs = [ fftAnalysis(self._forces[0,startIndex:endIndex], data) for data in self._forces[1:,startIndex:endIndex] ]
        return self._FFTs
    
    def _calcTotalForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)
        self._totalForces = np.array([
            self._forces[0,startIndex:endIndex],
            self._forces[1,startIndex:endIndex] + self._forces[4,startIndex:endIndex], 
            self._forces[2,startIndex:endIndex] + self._forces[5,startIndex:endIndex],
            self._forces[3,startIndex:endIndex] + self._forces[6,startIndex:endIndex]])
        return self._totalForces

    def _calcCoefficients(self, rho = 1.0, u = 1.0, A = 2.0):
        pass
       
    def getViscousForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)
        return self._forces[4:6,startIndex:endIndex]
    
    def getPressureForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)
        return self._forces[1:3,startIndex:endIndex]

    # TODO zip viscous and pressure and return sum
    def getTotalForces(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._forces[0,:], start, end)        
        if hasattr(self, "_totalForces"):
            startIndex, endIndex = getIndices(self._totalForces[0,:], start, end)            
            return self._totalForces[1:3, startIndex:endIndex]
        else:
            return self._calcTotalForces(start, end)
   
    def getViscousForcesAverages(self):
        if len(self._averageForces) > 0:
            return self._averageForces[0:2]
        else:
            self.calcAverages(self._startTime, self._endTime)
            return self._averageForces[0:2]

    def getPressureForcesAverages(self):
        if len(self._averageForces) > 0:
            return self._averageForces[3:5]
        else:
            self.calcAverages(self._startTime, self._endTime)
            return self._averageForces[3:5]


    def _calcMax(self, start = 0, end = 0):
        pass
    
    def _calcMin(self, start = 0, end = 0):
        pass

    def _calcMaxIndex(self, start = 0, end = 0):
        pass    
    def _calcMinINdex(self, start = 0, end = 0):
        pass

    def getEndTime(self):
        latestIndex = len(self._forces[0,:]) - 1
        print(self._verbose)
        if self._verbose == True: print ("latest index: ", latestIndex)
        return self._forces[0,latestIndex]


    def getStartTime(self):
        return self._forces[0,0]


    
