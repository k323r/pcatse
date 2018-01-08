#!/usr/bin/python3

from matplotlib import pyplot as plt
import numpy as np


def writeFile(outFile, timeSteps, data):
    with open(outFile, 'w') as f:
        f.writelines("# Forces\n# CofR       : (0.000000e+00 0.000000e+00 0.000000e+00)\n# Time       forces(pressure viscous porous) moment(pressure viscous porous)\n")
        for t, x in zip(timeSteps, data):
            f.writelines("".join([a for a in [str(t),
                                "\t(",	# Forces
                                "(", str(x), " ", str(x + 1), " ", str(x + 2), ")"	# pressure
                                " ",
                                "(", str(x + 3), " ", str(x + 4), " ", str(x + 5), ")"	# viscous
                                " ",
                                "(", str(x + 6), " ", str(x + 7), " ", str(x + 8), ")"	# porous
                                ")",
                                " (", 	# Moments
                                "(", str(x), " ", str(x + 1), " ", str(x + 2), ")"	# pressure
                                " ",
                                "(", str(x + 3), " ", str(x + 4), " ", str(x + 5), ")"	# viscous
                                " ",
                                "(", str(x + 6), " ", str(x + 7), " ", str(x + 8), ")"	# porous
                                ")\n"]]
                                ))
        f.close()

if __name__ == "__main__":

    f = 1.0
    mag = 5.0
    randMag = 0.1*mag
    deltaT = 0.01
    startTime = 0
    stopTime = 10
    outFileClean = "OpenFOAM4x/forces_synthetic_clean.dat"
    outFileNoise = "OpenFOAM4x/forces_synthetic_noise.dat"
    
    timeSteps = np.linspace(startTime, stopTime, num=((stopTime-startTime)/deltaT + 1), endpoint=True, dtype='f')
    dataClean = mag * np.sin(2 * np.pi * f * timeSteps)
    dataNoise = mag * np.sin(2 * np.pi * f * timeSteps) + np.random.normal(scale = randMag, size = len(timeSteps))
    
    plt.figure(1)
    plt.plot(timeSteps, dataClean, label="clean data")
    plt.plot(timeSteps, dataNoise, label="noisy data, noise mag = {}".format(randMag))
    plt.grid()
    plt.legend(loc="best")
    plt.hold()
    plt.show()
    
    writeFile(outFileClean, timeSteps, dataClean)
    writeFile(outFileNoise, timeSteps, dataNoise)
    

    


