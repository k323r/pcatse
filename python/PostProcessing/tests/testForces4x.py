#!/usr/bin/python3

import sys

### add the wiggle lab postprocessing to the python path
sys.path.append("/home/alsander/Projekte/wigglelabGIT/python/PostProcessing")
import Forces4x as Forces

import matplotlib.pyplot as plt

resolution = 1e-7

dataClean = Forces.Forces("../data/OpenFOAM4x/forces_synthetic_clean.dat")
dataNoisy = Forces.Forces("../data/OpenFOAM4x/forces_synthetic_noise.dat")
dataClean.calculateAveragesStd()
dataNoisy.calculateAveragesStd()
dataNoisy.filterForces()
#dataNoisy.calculateFilteredAveragesStd()

plt.figure(1)
plt.plot(dataNoisy.forces["total"]["x"], label="raw")
plt.plot(dataNoisy.filteredForces["total"]["x"], label="filtered, kernel length = 10")
plt.grid()
plt.show()


averageIter = iter(range(9))

for force in ("pressure", "viscous"):
    for component in ("x", "y", "z"):
        avg = next(averageIter)
        assert dataClean.averageForces[force][component] < avg + resolution and dataClean.averageForces[force][component] > avg - resolution, "average deviates: {}, {} -> average is {}, expecting: {} +- {}".format(force, component, dataClean.averageForces[force][component], avg, resolution)
        assert dataClean.getMaxTime != 10, "max time != 10!"
        assert dataClean.getMinTime != 0, "min time != 0!"
        


print("done testing.")
