#!/usr/bin/python3

from Forces1706 import Forces
from matplotlib import pyplot as plt

f = Forces("data/forcesAllv1706Simple/")
plt.plot(f.forces[:,0], f.forces[:,1])
plt.show()

