import numpy as np
from matplotlib import pyplot as plt

data = np.genfromtxt("roofline.dat")

rst = 3             # Starting row of "actual data"
ndata = 4           # Number of points of actual data

# Labels
labels = ['roofline', 'gri30 - bicgstab', 'gri30 - gmres', 'isooctane - bicgstab', 'isooctane - gmres']

"""
The first three rows of the input file should define the roofline envelope:
   2-------3
  /
 /
1
Then, in further rows, the actual points corresponding to kernels follow.
In any case, each point is given, in one row as
     <arithmetic intensity>           <GFLOP/s>
"""

opts = { \
     "marklist" : ['.', 'x', '+', '^', 'v', '<', '>', 'd'],
     "colorlist" : ['k', 'b', 'r', 'g', 'c', 'm', 'orange', 'pink'],
     "linetype" : ['-', '--', '-.', ':', '--', '-.', '--',':'],
     "linewidth" : 0.75,
     "marksize" : 6,
     "markedgewidth" : 1 \
     }

fig,ax = plt.subplots()

plt.plot(data[0:rst,0], data[0:rst,1], label=labels[0], ls='--',  ms=opts['marksize'])

for row in range(rst,rst+ndata):
    plt.plot(data[row,0], data[row,1], label = labels[row-2], ms = opts['marksize'], \
            marker=opts['marklist'][row-2])
ax.set_xscale("log")
ax.set_yscale("log")
plt.legend(loc="best", fontsize="medium")
plt.grid()
plt.xlabel("Arithmetic intensity")
plt.ylabel("Throughput (GFLOP/s)")
plt.show()
