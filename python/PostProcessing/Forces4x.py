import os.path as path
import numpy as np
from glob import glob as glob
from PostProcessingIO import isNumber, fftAnalysis, filterData, toCoefficient
from collections import defaultdict

# TODO add fft analysis (probably need reimplementation)

class Forces:

    _TIME = 0
    _PRESSURE_X = 1
    _PRESSURE_Y = 2
    _PRESSURE_Z = 3
    _VISCOUS_X = 4
    _VISCOUS_Y = 5
    _VISCOUS_Z = 6
    _POROUS_X = 7
    _POROUS_Y = 8
    _POROUS_Z = 9

    def __init__(self, inputpath, average = False, FFT = False, verbose = True):
    
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
                        self._rawForces.append(self._readForceFile(path.join(timeDir, "forces.dat")))
                
                ### generate a numpy matrix containing all forces
                self._rawForces = np.concatenate((self._rawForces))
                ### sort the matrix by sorting after the first column (time)
                self._rawForces = self._rawForces[self._rawForces[:,0].argsort()]
            
            ### all forces should be loaded by now
            # build a "nice" dict with the forces                    
            pos = iter(range(1,10))
            self.forces = {}
            self.forces["time"] = self._rawForces[:,self._TIME]
            # get the forces (pressure, viscous, porous)
            for forceType in ("pressure", "viscous", "porous"):
                self.forces[forceType] = {}
                for component in "x", "y", "z":
                    self.forces[forceType][component] = self._rawForces[:,next(pos)]
            # calculate total forces:
            self.forces["total"] = {}
            self.forces["total"]["x"] = self.forces["pressure"]["x"] + self.forces["viscous"]["x"] + self.forces["porous"]["x"]
            self.forces["total"]["y"] = self.forces["pressure"]["y"] + self.forces["viscous"]["y"] + self.forces["porous"]["y"]
            self.forces["total"]["z"] = self.forces["pressure"]["z"] + self.forces["viscous"]["z"] + self.forces["porous"]["z"]
            
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
                elif len(tmp) != 19:
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
    
    def _getIndices(self, startTime = 0, endTime = 0):
        startIndex = 0
        endIndex = len(self.forces["time"])
        if startTime == 0 and endTime == 0:
            pass        
        elif startTime > 0 and endTime > 0 and startTime > endTime:
            self._verbosePrint("start time > end time, setting end time to max time: {}".format(self._rawForces[-1,self._TIME]))                  
            startIndex = self._getTimeIndex(startTime)
        elif startTime == 0 and endTime > 0:
            self._verbosePrint("start time is set to zero!")
            endIndex = self._getTimeIndex(endTime)
        else:
            startIndex = self._getTimeIndex(startTime)
            endIndex = self._getTimeIndex(endTime)
            self._verbosePrint("start time set to {} and end time set to {}".format(startIndex, endIndex))
        return (startIndex, endIndex)
    
    def calculateAveragesStd(self, startTime = 0, endTime = 0):
        
        self.averageForces = {}
        self.stdForces = {}
        
        startIndex, endIndex = self._getIndices(startTime, endTime)

        for forceType in ("total", "pressure", "viscous", "porous"):
            self.averageForces[forceType] = {}
            self.stdForces[forceType] = {}
            for component in ("x", "y", "z"):
                self.averageForces[forceType][component] = np.average(self.forces[forceType][component][startIndex:endIndex])
                self.stdForces[forceType][component] = np.std(self.forces[forceType][component][startIndex:endIndex])
            
        return (self.averageForces, self.stdForces)

    def _verbosePrint(self, message):
        if self._verbose == True:
            print(message)
    
    def getMaxTime(self):
        self._verbosePrint("max time is {}".format(self.forces["time"][-1]))
        return self.forces["time"][-1]
        
        
    def filterForces(self, startTime = 0, endTime = 0, filterFunction = "flat", filterWindow = 11):
        startIndex, endIndex = self._getIndices(startTime, endTime)
        
        self.filteredForces = {}
        self.filteredForces["time"] =  self._rawForces[:,self._TIME]
        
        for forceType in ("total", "pressure", "viscous", "porous"):
            self.filteredForces[forceType] = {}
            for component in ("x", "y", "z"):
                self.filteredForces[forceType][component] = filterData(self.forces[forceType][component][startIndex:endIndex], filterWindow, filterFunction)
        
        return self.filteredForces
    
    def calculateFilteredAveragesStd(self, startTime = 0, endTime = 0):
        
        if hasattr(self, "filteredForces") == False:
            raise Exception("missing attribute filteredForces. Please run filterForces prior to calculateFilteredAveragesStd!")
        
        self.averageFilteredForces = {}
        self.stdFilteredForces = {}
        
        startIndex, endIndex = self._getIndices(startTime, endTime)

        for forceType in ("total", "pressure", "viscous", "porous"):
            self.averageFilteredForces[forceType] = {}
            self.stdFilteredForces[forceType] = {}
            for component in ("x", "y", "z"):
                self.averageFilteredForces[forceType][component] = np.average(self.filteredForces[forceType][component][startIndex:endIndex])
                self.stdFilteredForces[forceType][component] = np.std(self.filteredForces[forceType][component][startIndex:endIndex])
            
        return (self.averageFilteredForces, self.stdFilteredForces)
    
    def getMinTime(self):
        self._verbosePrint("min time is {}".format(self.forces["time"][0]))
        return self.forces["time"][0]
    
    ## define a method for getting forces by time
    def getForceByTime(self,  startTime = 0, endTime = 0, forceType = "total", forceComponent = "x"):
        startIndex, endIndex = getIndices(startTime, endTime)
        return self.forces[forceType][forceComponent][startIndex:endIndex]
    
    
            
class ForceCoefficients(Forces):
    def __init__(self, inputpath, rho = 1, velocity = 1, area = 2, average = False, FFT = False, verbose = True):
    
        self._inputpath = inputpath
        self._verbose = verbose
           
        self._forces = Forces(inputpath, average = average, FFT = FFT, verbose = verbose)
        
        self.forceCoefficients = {forceType : { component : self._forces.forces[forceType][component] / toCoefficient(rho, velocity, area) for component in self._forces.forces[forceType].keys()} for forceType in self._forces.forces.keys() }
        
        
    
    
        
        
                
        
        

