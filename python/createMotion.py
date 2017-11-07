import os
import numpy as np
from math import pi, atan

simulationType = 'yaw'

startTime = 0
endTime = 40
dt = 0.001


f = 0.1
a0 = 0.1
omega = f * 2 * pi
phaseshift = pi / 2

print('Amplitude = {}'.format(a0))
print('Model Frequency =  {}'.format(f))
print('Omega = {}'.format(omega))

# Calculate sinusoidal movement
timesteps = np.linspace(startTime, endTime, int((endTime - startTime) / dt))
translation = a0 * np.sin(omega * timesteps + phaseshift)
velocity = a0 * omega * np.cos(omega * timesteps + phaseshift)
acceleration = - a0 * omega * omega * np.sin(omega * timesteps + phaseshift)

# Calculate body angle according to body position
# applicable only for trim and yaw
angle = np.arctan(velocity) * 180 / np.pi
angularVelocity = np.arctan(acceleration) * 180 / np.pi

# Calculate angular acceleration, need derivation of translational acceleration for that
yTwoPrime = - a0 * omega * omega * omega * np.cos(omega * timesteps + phaseshift)
angularAcceleration = np.arctan(yTwoPrime) * 180 / np.pi

# Checking
print('Max displacement: {}'.format(max(translation)))
print('Max velocity: {}'.format(max(velocity)))
print('Max angle: {}'.format(max(angle)))

# Period length T = 1 / f
# Timeshift = phaseshift / ( 2 * pi) * T
tAtZero = int((1 / f) * (1 - phaseshift / (2 * pi)) / dt)
angleAtZero = angle[tAtZero]
print('Angle at zero displacement = {}'.format(angleAtZero))
print('Angle at start = {}'.format(angle[0]))


sixDoFfile = os.path.join(os.getcwd(), 'constant/tables/6DoFMotion.txt')

if not os.path.exists(sixDoFfile):
    os.makedirs(sixDoFfile)

print("Writing output file to: " + sixDoFfile)

with open(sixDoFfile, 'w') as file_handler:

    file_handler.write("{}\n(\n".format(timesteps.size))

    if simulationType == 'sway':
        for t, y in zip(timesteps, translation):
            file_handler.write("({}\t ((0 {} 0) (0 0 0)))\n".format(t, y))

    elif simulationType == 'heave':
        for t, y in zip(timesteps, translation):
            file_handler.write("({}\t ((0 0 {}) (0 0 0)))\n".format(t, y))

    elif simulationType == 'yaw':
        for t, y, r in zip(timesteps, translation, angle):
            file_handler.write("({}\t ((0 {} 0) (0 0 {})))\n".format(t, y, r))

    elif simulationType == 'trim':
        for t, y, r in zip(timesteps, translation, angle):
            file_handler.write("({}\t ((0 0 {}) (0 {} 0)))\n".format(t, y, r))


    file_handler.write(")")


pyTablefile = os.path.join(os.getcwd(), 'constant/tables/pyTable')
headerFile = os.path.join(os.getcwd(), 'constant/tables/tableHeader')

assert os.path.exists(headerFile)
header = open(headerFile, 'r')

print("Writing output file to: " + pyTablefile)

with open(pyTablefile, 'w') as file_handler:
    for line in header:
        file_handler.write(line)

    file_handler.write("(\n")

    if simulationType == 'sway':
        for t, y in zip(timesteps, translation):
            file_handler.write("({}\t(0 {} 0))\n".format(t, y))

    elif simulationType == 'heave':
        for t, y in zip(timesteps, translation):
            file_handler.write("({}\t(0 0 {}))\n".format(t, y))

    elif simulationType == 'yaw':
        for t, y in zip(timesteps, translation):
            file_handler.write("({}\t(0 {} 0))\n".format(t, y))

    elif simulationType == 'trim':
        for t, y in zip(timesteps, translation):
            file_handler.write("({}\t(0 0 {}))\n".format(t, y))

    file_handler.write(")")


# accelerationFile = os.path.join(os.getcwd(), 'constant/tables/acceleration.dat')
#
# print("Writing output file to: " + accelerationFile)
#
# with open(accelerationFile, 'w') as file_handler:
#     file_handler.write("{}\n(\n".format(timesteps.size))
#     for t, y, rv, racc in zip(timesteps, acceleration, angularVelocity, angularAcceleration):
#         file_handler.write("({}\t ((0 {} 0) (0 0 0)(0 0 {})))\n".format(t, y, rv, racc))
#     file_handler.write(")")
#

