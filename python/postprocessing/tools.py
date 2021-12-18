import numpy as np
import pandas as pd
from os.path import join as joinPaths
from os.path import isdir
from os.path import isfile
from os import listdir as ls
from IPython.display import display, Markdown, Latex
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.pyplot import cm

# Definition of constants
# matplotlib
PLOTWIDTH = 16
PLOTHEIGHT = 9
DEBUG = False

'''
def setMatplotlibParams():
    # configure matplotlib
    plt.rcParams['savefig.dpi'] = 150
    plt.rcParams['figure.autolayout'] = False
    plt.rcParams['figure.figsize'] = (PLOTWIDTH, PLOTHEIGHT)
    plt.rcParams['xtick.labelsize'] = plt.rcParams['ytick.labelsize'] = 18   # presentation version
    plt.rcParams['axes.labelsize'] = 22   # presentation version
    plt.rcParams['axes.titlesize'] = 22   # presentation version
    plt.rcParams['font.size'] = 22
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'EB Garamond'
    plt.rcParams['mathtext.fontset'] = 'dejavuserif'
    plt.rcParams['lines.linewidth'] = 2.5
    plt.rcParams['lines.markersize'] = 12
    plt.rcParams['legend.fontsize'] = 22
    plt.rcParams['legend.numpoints'] = 1
    plt.rcParams['lines.markeredgewidth'] = 1
'''

def colorIterGenerator(nColors = 4):
    return iter(cm.rainbow(np.linspace(0,1,nColors)))

def printMD(string):
    display(Markdown(string))

def printTeX(string):
    display(Latex(string))

def isNumber(string):
    try:
        float(string)
        return True
    except:
        return False

def readDir(path):
    return [d for d in ls(path) if isdir(joinPaths(path, d))]

def getTimeSteps(path):
    tmp = sorted([float(d) for d in readDir(path) if isNumber(d)])
    return [str(x).split(".")[0] for x in tmp]

def readForceFile(path, skipHeader=3, startTime=100, endTime=500, normalTime=1, normalForce=1):
    data = list()
    with open(path, "r") as forceInFile:
        for counter, line in enumerate(forceInFile):
            # skip header
            if counter < skipHeader:
                continue
            if line[0] == '#':
                continue
            # replace parentheses and split into array of floats 
            tmp = [float(x) for x in line.replace("(", "").replace(")", "").split()]

            # check if the time (first column) is smaller than the startTime
            if tmp[0] < startTime:
                continue

            # check if the endTime was reached
            if tmp[0] >= endTime:
                break

            # if none of the above criteria were met, append data for keeping
            data.append(tmp)
    data = pd.DataFrame(data = np.array(data), 
                        columns=["time",
                                 "total_x",
                                 "total_y",
                                 "total_z",
                                 "pressure_x",
                                 "pressure_y",
                                 "pressure_z",
                                 "viscous_x",
                                 "viscous_y",
                                 "viscous_z",
                                ])
    # normalise data
    data["time"] = data["time"] / normalTime
    for c in data.columns[1:]:
        data[c] = data[c] / normalForce

    return data

def readRibletForces(dataDir, forceDirName, forceFileName, normaliseForces, STARTTIME = 100, ENDTIME = 500, LATESTTIME = -1):
    ribletForces = dict()
    # read in riblet data
    for case in readDir(dataDir):
        try:
            name, _, _, _, s, = case.split("_")[:5]
        except:
            if DEBUG: printMD("__could no parse directory: {}, skipping__".format(case))
            continue
        if len(s) == 4:
            try:
                s = float(s)/10
            except:
                pass
        elif len(s) == 5:
            try:
                s = float(s)/100
            except:
                pass
        else:
            print("encountered non matching string length for s")

        if name == "Riblet":
            timeDir = getTimeSteps(joinPaths(dataDir, joinPaths(case, forceDirName)))[LATESTTIME]
            forceFilePath = joinPaths(
                joinPaths(dataDir, joinPaths(
                    case, joinPaths(
                        forceDirName, joinPaths(timeDir, forceFileName)))))
            ribletForces[str(s)] = readForceFile(forceFilePath,
                                                 startTime = STARTTIME,
                                                 endTime = ENDTIME,
                                                 normalForce = normaliseForces[str(s)]
                                                )
    return ribletForces

def readTimeDirs(dataDir, dirName, fileName, normalise = [], columns = [] , STARTTIME = 100, ENDTIME = 500, LATESTTIME = -1):
    dataPerDir = dict()
    # read in riblet data
    for case in readDir(dataDir):
        try:
            name, _, _, _, s, = case.split("_")[:5]
        except:
            if DEBUG: printMD("__could no parse directory: {}, skipping__".format(case))
            continue
        if len(s) == 4:
            try:
                s = float(s)/10
            except:
                pass
        elif len(s) == 5:
            try:
                s = float(s)/100
            except:
                pass
        else:
            print("encountered non matching string length for s")

        if name == "Riblet":
            timeDir = getTimeSteps(joinPaths(dataDir, joinPaths(case, dirName)))[LATESTTIME]
            if DEBUG: print(timeDir)
            filePath = joinPaths(
                joinPaths(dataDir, joinPaths(
                    case, joinPaths(
                        dirName, joinPaths(timeDir, fileName)))))
            dataPerDir[str(s)] = filePath
            '''
            dataPerDir[str(s)] = readTimeFile(filePath,
                                              startTime = STARTTIME,
                                              endTime = ENDTIME,
                                              normalise = normalise,
                                              columns = columns,
                                             )
            '''
    return dataPerDir

def readTimeFile(path, skipHeader=0, normalise=[], columns=[], startTime=100, endTime=500, latestTime=-1):
    data = list()
    with open(path, "r") as inFile:
        for counter, line in enumerate(inFile):
            # skip header
            if counter < skipHeader:
                continue

            # replace parentheses and split into array of floats 
            tmp = [float(x) for x in line.replace("(", "").replace(")", "").split()]

            # check if the time (first column) is smaller than the startTime
            if tmp[0] < startTime:
                continue

            # check if the endTime was reached
            if tmp[0] >= endTime:
                break

            # if none of the above criteria were met, append data for keeping
            data.append(tmp)
    if normalise:
        if len(normalise) != len(columns):
            raise Exception("normalise and columns need to be of equal length")
        if len(normalise) > len(data[0]):
            raise Exception("normalise must not have same length as available columns")
        # convert to numpy matrix 
        data = np.array(data)
        # normalise
        for i,n in enumerate(normalise):
            data[:,i] = data[:,i]/n
        # converto to panda dataframe
        data = pd.DataFrame(data = data[:,:len(columns)], columns=columns)
    else:
        data = pd.DataFrame(data = np.array(data))

    return data

### function to read in Bechert data
def readBechert(bechertRawFilePath):
    '''
    Reads in a given file and seperates the values into different datasets
        by splitting at empty lines

    Keyword arguments:
        bechertRawFilePath: path to file

    Return value:
        dict containing panda DataFrames with the corresponding datasets
    '''
    bechert = dict()
    parseHeader = True
    with open(bechertRawFilePath, "r") as bechertRaw:
        for line in bechertRaw:
            line = line.rstrip()               # remove trailing newlines
            if len(line) == 0:                 # new data sets are seperated by a empty newline
                parseHeader = True             # set parse header flag, since the next line holds the data set name
                continue                       # continue to next line
            if parseHeader:                    # check if the header parse flag is set
                _, name = line.split(" ")      # if so, the name of the dataset is the second element of the line
                bechert[name] = list()         # create a new list for the new data set
                parseHeader = False            # header has been parsed so set the flag to false
                continue                       # continue with the next line
            try:
                bechert[name].append([float(x) for x in line.split(" ")])
            except:
                print("could not parse line: {}, skipping".format(line))
                continue
    for k in bechert.keys():
        bechert[k] = pd.DataFrame(data = np.array(bechert[k]),
                              columns=["s+", "reduction"])
    return bechert

### function to read in profile data extracted from simulations
def readLineFile(path, skipHeader=0, normalise=[], columns=[]):
    '''
    Reads in a file which contains arbitrary Tensors extracted following a
        specified line

    Keyword arguments:
        path: path to the file
        skipHeader: number of lines to skip in case of a header
        normalise: list of values to normalise each column by
        columns: list of column names

    Return value:
        returns a panda DataFrame containing the data
    '''

    data = list()
    with open(path, "r") as inFile:
        for counter, line in enumerate(inFile):
            # skip header
            if counter < skipHeader:
                continue

            # replace parentheses and split into array of floats 
            tmp = [float(x) for x in line.split()]

            # if none of the above criteria were met, append data for keeping
            data.append(tmp)
    if normalise:
        if len(normalise) != len(columns):
            raise Exception("normalise and columns must be of equal length")
        data = pd.DataFrame(data = np.array(data)[:,:len(normalise)], columns=columns)
        # normalise data
        for i, c in enumerate(data.columns):
            data[c] = data[c] / normalise[i]
    else:
        data = pd.DataFrame(data = np.array(data))

    return data


# central differencing function
def centralDifference(x, y):
    if len(x) < 5:
        raise Exception("need at least length of 5 to implement central differencing")

    if len(x) != len(y):
        raise Exception("x and y must be of equal length")

    derivative = list()
    lastI = len(x) - 1
    # calculate the first element via forward differnce
    derivative.append((y[1] - y[0]) / (x[1] - x[0]))
    for i in range(1, lastI):
        derivative.append((y[i+1] - y[i-1])/(x[i+1] - x[i-1]))
    # calculate the last element via backwards differencing
    derivative.append

    # iteratte over the remaining elements

def plotRST(ribletRSTProfiles, cleanRSTProfiles, MoserRSTProfiles, component="uu"):
    
    def uvSwitch(component):
        if component=="uv":
            return -1
        else:
            return 1        
    
    componenLabelMap = {"uu" : "$<u'^2>^+$",
                        "vv" : "$<v'^2>^+$",
                        "ww" : "$<w'^2>^+$",
                        "uv" : "$<-u'v'>^+$",
                        "uw" : "$<u'w'>^+$",
                        "vw" : "$<v'w'>^+$",
                       }
    
    colorI = colorIterGenerator(nColors=len(ribletRSTProfiles.keys()))    # color iterator

    plt.semilogx(cleanRSTProfiles["y+"], cleanRSTProfiles[component]*uvSwitch(component), color="k", label="Smooth channel")

    # iterate over the riblet cases
    for s in sorted(ribletRSTProfiles.keys()):
        plt.semilogx(ribletRSTProfiles[s]["y+"], ribletRSTProfiles[s][component]*uvSwitch(component), color = next(colorI), label="S$^+ = {}$".format(s))

    plt.semilogx(MoserRSTProfiles["y+"], MoserRSTProfiles[component]*uvSwitch(component), color = "k", label = "Moser, Kim & Mansour (1998)", ls="-.")

    plt.grid(); plt.xlabel("$y^+$"); plt.ylabel(componenLabelMap[component]); plt.legend(); plt.xlim([0.5,400])
