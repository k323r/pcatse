import numpy as np
import glob, re
from os.path import isdir, isfile
from math import sqrt
from PostProcessingIO import readFile
from PostProcessingIO import getTimeDirs

class SingleGraph():
    '''
    Simple class to post process single graph data from OpenFOAM simulations
    '''

    # for log law calculations
    _kinv = 1.0/0.41
    _Cstart = 5.0
    _nu = 1e-4
    
    def __init__(self, path, startTime = 0, endTime = 1, nu = 0.001, Average = True, StdDev = True, Verbose = False):
        self._timesteps = {}
        if (isfile(path)):
            self._timesteps['constant'] = readFile(path, startTime, endTime).T
            if Verbose: print("successfully read file: ", path, " with ", len(self._timesteps['constant']), "elements")
        elif (isdir(path)):
            for time in getTimeDirs(path):
                self._timeSteps[time] = getTimeDirs(path)
        else:
            raise Exception('no such file or directory: ', path)
            
        
    
    def _scaleProfile(self, factor):
        pass

    def _calcUTau(self):
        pass
    
    @property
    def getUTau(self):
        pass
    
    def _calcYPlus(self):
        pass

    @property    
    def getYPlus(self):
        pass
    
    def _calcPlusProfile(self):
        pass
    
    def getPlusProfle(self):
        pass
    
    
    
