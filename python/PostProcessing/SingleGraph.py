import numpy as np
import glob, re
from os.path import isdir, isfile
from math import sqrt
from PostProcessingIO import readFile
from PostProcessingIO import getTimeDirs
from PostProcessingIO import isNumber, fftAnalysis, filterData, toCoefficient

class SingleGraph():
    '''
    Simple class to post process single graph data from OpenFOAM simulations
    '''


    # for log law calculations
    _kinv = 1.0/0.41
    _Cstart = 5.0
    _nu = 1e-4
    
    def __init__(self, path, fields = ("UMean",), time = ("latestTime",), nu = 0.001, Average = True, StdDev = True, Verbose = False):
    
        self._fields = {}
        for field in fields:
            self._fields[field] = {}
            if (isfile(path) and re.findall(".*"+field+"\.xy", path)):
                try:
                    self._fields[field]['constant'] = readFile(path)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
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
    
    
    
