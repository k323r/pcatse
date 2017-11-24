#!/usr/bin/python3

from matplotlib import pyplot as plt
import numpy as np

def printForcesHeader(filehandle):
    filehandle.writelines("# Forces\n# CofR       : (0.000000e+00 0.000000e+00 0.000000e+00)\n# Time       forces(pressure viscous porous) moment(pressure viscous porous)\n")

f = 1.0
mag = 5.0
randMag = 0.1
deltaT = 0.01
startTime = 0
stopTime = 10
outFile = "forces1.dat"

# 0.01         	((-1.898779e-22 -4.017774e-03 4.357906e-03) (1.715850e-02 4.548571e-06 1.701528e-04) (0.000000e+00 0.000000e+00 0.000000e+00)) ((5.894662e-03 1.786078e-02 -6.068779e-03) (-5.633429e-06 2.286602e-02 -1.872746e-04) (0.000000e+00 0.000000e+00 0.000000e+00))


timeSteps = np.linspace(startTime, stopTime, num=((stopTime-startTime)/deltaT + 1), endpoint=True, dtype='f')
data = mag * np.sin(2 * np.pi * f * timeSteps)
with open(outFile, 'w') as f:
    printForcesHeader(f)
    for t, x in zip(timeSteps, data):
        f.writelines("".join([a for a in [str(t),
                                "\t(",	# Forces
                                "(", str(x*0.1), " ", str(x*0.2), " ", str(x*0.3), ")"	# pressure
                                " ",
                                "(", str(x*0.4), " ", str(x*0.5), " ", str(x*0.6), ")"	# viscous
                                " ",
                                "(", str(x*0.7), " ", str(x*0.8), " ", str(x*0.9), ")"	# porous
                                ")",
                                " (", 	# Moments
                                "(", str(x*-0.1), " ", str(x*-0.2), " ", str(x*-0.3), ")"	# pressure
                                " ",
                                "(", str(x*-0.4), " ", str(x*-0.5), " ", str(x*-0.6), ")"	# viscous
                                " ",
                                "(", str(x*-0.7), " ", str(x*-0.8), " ", str(x*-0.9), ")"	# porous
                                ")\n"]]
                                ))
    f.close()


