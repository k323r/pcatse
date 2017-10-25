# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 14:09:34 2017

@author: alsander
"""

from PostProcessingIO import getIndices
from PostProcessingIO import readFile
from PostProcessingIO import fftAnalysis
from PostProcessingIO import extractPressureGradient
from os.path import isfile
import numpy as np
from math import sqrt as sqrt

class PressureGradient():
    
    _path = ""
    _verbose = False
    
    def __init__(self, path, startTime = 0, endTime = 1, Average = True, StdDev = True, FFT = False, Verbose = False):
        if startTime > endTime:
            raise Exception("invalid syntax in __init__: startTime > endTime")
        
        self._path = path        
        self._startTime = startTime
        self._endTime = endTime
        self._verbose = Verbose
        self._pressureGradient = readFile(path, startTime, endTime)
        self._pressureGradient = self._pressureGradient.T
        
        if self._verbose == True: print ("successfully read file: ", self._path)
        
        if Average == True:
            self._calcAverage(startTime, endTime)
            if self._verbose == True: print ("successfully calculated average: ", self._averagePressureGradient)
        
        if StdDev == True:
            self._calcStdDev(startTime, endTime)
            if self._verbose == True: print ("successfully calculated standard deviation: ", self._stdDev)
            
        
        if FFT == True:
            self._calcFFT(startTime, endTime)
            if self._verbose == True: print ("successfully calculated FFT: ", self._FFT)

    
    def reRead():
        print("not implemented (yet)")

    @property        
    def getPressureGradient(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        return self._pressureGradient[1,startIndex:endIndex]
    
    def _calcAverage(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        self._averagePressureGradient = np.average(self._pressureGradient[1,startIndex:endIndex])
        if self._verbose == True: print("calulated average: ", self._averagePressureGradient)
    
    @property    
    def getTimes(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)          
        return self._pressureGradient[0,startIndex:endIndex]    
    
    @property
    def getStartTime(self):
        return self._pressureGradient[0,0]

    @property        
    def getEndTime(self):
        latestIndex = len(self._pressureGradient[0,:]) - 1
        return self._pressureGradient[0,latestIndex]
    
    @property    
    def getAverage(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        if hasattr(self, "_averagePressureGradient"):
            return self._averagePressureGradient
        else:
            return self._calcAverage(start, end)

    
    def _calcStdDev(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        self._stdDevPressureGradient = np.std(self._pressureGradient[1,startIndex:endIndex])
        return self._stdDevPressureGradient
        
    @property   
    def getStdDev(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        if hasattr(self, "_stdDevPressureGradient"):
            return self._stdDevPressureGradient
        else:
            return self._calcStd(start, end)
    
    def _calcFFT(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        self._FFT = [ fftAnalysis(self._pressureGradient[0,startIndex:endIndex], self._pressureGradient[1,startIndex:endIndex])]
        return self._FFT
        
    @property    
    def getFFT(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        if hasattr(self, "_FFT"):
            return self._FFT
        else:
            return self._calcFFT(start, end)
    
    
    def _calcTauW(self, start = 0, end = 0, hd = 1):
        if hasattr(self, "_averagePressureGradient"):
            self._tauW = self._averagePressureGradient / hd
            return self._tauW
        else:
            self._calcAverage(start, end)
            self._tauW = self._averagePressureGradient / hd
            return self._tauW

    @property
    def getTauW(self, start = 0, end = 0, hd = 1):
        '''
        calulates the wall shear stress for channel flow based upon the following formula:
        tauw = dp/dx / hd
        where dp/dx is the pressure gradient and hd is the hydraulic diameter  
        '''
        if hasattr(self, "_tauW"):
            return self._tauW
        else:
            self._calcTauW(start, end, hd = 1)
            return self._tauW
    
    def _calcUTau(self, start = 0, end = 0, rho = 1, hd = 1):
        if hasattr(self, "_tauW"):
            self._uTauW = sqrt(self._tauW/rho)
            return self._uTauW
        else:
            self._uTauW = sqrt(self._calcTauW(start, end, hd)/rho)
            return self._uTauW

    @property    
    def getUTau(self, start = 0, end = 0, rho = 1, hd = 1):
        '''
        caluculate uTauW based on tauW and the density rho
        '''
        if hasattr(self, "_uTauW"):
            return self._uTauW
        else:
            self._calcUTau(start, end, rho, hd)
            return self._uTauW
            
        
    
    