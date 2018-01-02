import os.path as path
import numpy as np
from glob import glob as glob
from PostProcessingIO import isNumber
from collections import defaultdict


class Forces:

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

    def __init__(self, inputpath, average = True, FFT = False, verbose = True):
    
        self._inputpath = inputpath
        self._verbose = verbose

        ### parse the input path and check if file or directory
        if (path.exists(inputpath)):
            ### if inputpath is a file, try to open the file and read it
            if (path.isfile(inputpath)):
                self._rawForces = self._readForceFile(inputpath)
            elif (path.isdir(inputpath)):
                self._timeDirs = []
                self._rawForces = []
                ### iterate over the time directories, read in the forces and append them
                for timeDir in glob(path.join(inputpath, "*")):
                    if isNumber(timeDir.split("/")[-1]):
                        self._verbosePrint("processing time dir {}".format(timeDir))
                        self._timeDirs.append(timeDir)                        
                        self._rawForces.append(self._readForceFile(path.join(timeDir, "force.dat")))
                
                ### generate a numpy matrix containing all forces
                self._rawForces = np.concatenate((self._rawForces))
                ### sort the matrix by sorting after the first column (time)
                self._rawForces = self._rawForces[self._rawForces[:,0].argsort()]
            
            ### all forces should be loaded by now
            # build a "nice" dict with the forces                    
            pos = iter(range(1,10))
            self.forces = {}
            self.forces["time"] = self._rawForces[:,0]
            for forceType in ("total", "pressure", "viscous"):
                self.forces[forceType] = {}
                for component in "x", "y", "z":
                    self.forces[forceType][component] = self._rawForces[:,next(pos)]
            
            if average == True:
                self.calculateAveragesStd()
                
            if FFT == True:
                raise Warning("not implemented yet!")
        else:
            raise IOError("could not find file: {}".format(inputpath))      
            
    def _readForceFile(self, filepath):
        raw = []

        with open(filepath, 'r') as filehandle:
            for line in filehandle:
                tmp = [x.strip('(').strip(')') for x in line.split()]
                if len(tmp) == 0:
                    continue
                elif tmp[0] == '#':
                    continue
                elif len(tmp) != 10:
                    continue
                else:
                    try:
                        raw.append([ float(i) for i in tmp ])
                    except ValueError:
                        print("could not convert string to float in line:")
                        print("\t" + line)
                        print("in file:")
                        print("\t" + filepath)

        filehandle.close()
        raw = np.array(raw)
        return raw
    
    def _getTimeIndex(self, time):
        index = 0
        while self._rawForces[index,0] < time and index < len(self._rawForces[:,0]):
            index += 1
        return index
    
    def calculateAveragesStd(self, startTime = 0, endTime = 0):
        if startTime > endTime:
            raise Exception("start time > end time!")
        
        self.averageForces = {}
        self.stdForces = {}
        
        if startTime == 0 and endTime == 0:
            pos = iter(range(1,10))
            for forceType in ("total", "pressure", "viscous"):
                self.averageForces[forceType] = {}
                for component in "x", "y", "z":
                    self.averageForces[forceType][component] = np.average(self._rawForces[:,next(pos)])
                    
            pos = iter(range(1,10))
            for forceType in ("total", "pressure", "viscous"):
                self.stdForces[forceType] = {}
                for component in "x", "y", "z":
                    self.stdForces[forceType][component] = np.std(self._rawForces[:,next(pos)])
                    
        else:
            startIndex = self._getTimeIndex(startTime)
            endIndex = self._getTimeIndex(endTime)
            self._verbosePrint("{} {}".format(startIndex, endIndex))
            pos = iter(range(1,10))
            for forceType in ("total", "pressure", "viscous"):
                self.averageForces[forceType] = {}
                for component in "x", "y", "z":
                    self.averageForces[forceType][component] = np.average(self._rawForces[startIndex:endIndex,next(pos)])
                    
            pos = iter(range(1,10))
            for forceType in ("total", "pressure", "viscous"):
                self.stdForces[forceType] = {}
                for component in "x", "y", "z":
                    # print("force: {}, component: {}".format(forceType, component))
                    self.stdForces[forceType][component] = np.std(self._rawForces[startIndex:endIndex,next(pos)])
            
        return(self.averageForces, self.stdForces)


    def _verbosePrint(self, message):
        if self._verbose == True:
            print(message)
            
class ForceCoefficients(Forces):
    def __init__(self, inputpath, rho = 1, velocity = 1, area = 2, average = True, FFT = False, verbose = True):
    
        self._inputpath = inputpath
        self._verbose = verbose
           
        self._forceObject = Forces(inputpath)

