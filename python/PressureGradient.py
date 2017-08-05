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
        self._pressureGradient = readFile(path)
        
        if self._verbose == True: print ("successfully read file: ", self._path)
        
        if Average == True:
            self._calcAverage()
        

    
    def reRead():
        pass
    
    def _calcAverage(self, start = 0, end = 0):
        startIndex, endIndex = getIndices(self._pressureGradient[0,:], start, end)
        if self._verbose == True: print(startIndex, endIndex)
        self._averagePressureGradient = np.average(self._pressureGradient)
            
    
    def getAverage():
        pass
    
    def _calcStdDev():
        pass
    
    def getStdDev():
        pass
    
    def _calcFFT():
        pass
    
    def getFFT():
        pass
    
    def _calcTauW():
        pass
    
    def getTauW():
        pass
    
    def _calUTau():
        pass
    
    def getUTau():
        pass
    
    