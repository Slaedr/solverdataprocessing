#! /bin/env python3

import math
import os
import scipy as sp
import scipy.io
import scipy.linalg
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker as tkr

textsize = 16
ticknumsize = 12

def get_eigenvalues(A):
    adense = A.toarray()
    w = sp.linalg.eigvals(adense)
    minreal = np.min(w.real)
    print("Smallest real part of any eigenvalue = " + str(minreal))
    if minreal < 0.0:
        printf("NEGATIVE real part! Cannot plot x-axis on log scale")
        exit(-1)
    return w

if __name__ == "__main__":
    opts = { \
         "marklist" : ['o', 'x', '+', '^', 'v', '<', '>', 'd'],
         "colorlist" : ['k', 'b', 'r', 'g', 'c', 'm', 'orange', 'pink'],
         "linetype" : ['-', '--', '-.', ':', '--', '-.', '--',':'],
         "linewidth" : 0.75,
         "marksize" : [3,5,5,5,5],
         "markedgewidth" : 1 \
         } 

    curdir = os.getcwd()
    ymin = 1000.0
    ymax = 0.0
    for file in os.listdir(curdir):
        filename = os.fsdecode(file)
        if filename.endswith(".mtx"):
            print("Found " + filename)
            A = sp.io.mmread(filename)
            w = get_eigenvalues(A)
            ymaxl = w.imag.max()
            yminl = w.imag.min()
            # Scale y-axis to ~1 and append the multiplier to the y label
            if ymax < ymaxl:
                ymax = ymaxl
            if ymin > yminl:
                ymin = yminl
    tenpow = np.log10(ymax)
    tenpow = math.floor(tenpow)
    ymax = ymax / math.pow(10,tenpow)
    ymin = ymin / math.pow(10,tenpow)
    yrange = ymax-ymin
    ymax += 0.1*yrange
    ymin -= 0.1*yrange
    plt.rcParams.update({'font.size': textsize})
    plt.close()
    idat = 0
    for file in os.listdir(curdir):
        filename = os.fsdecode(file)
        if filename.endswith(".mtx"):
            split_ = filename.split('.')
            casename = split_[0]
            A = sp.io.mmread(filename)
            w = get_eigenvalues(A)
            imageformatstring = "png"
            #plt.scatter(np.log10(w.real), w.imag/math.pow(10,tenpow), label=casename,
            #        marker=opts['marklist'][idat], ms=opts['marksize'][idat])
            plt.plot(np.log10(w.real), w.imag/math.pow(10,tenpow), label=casename,
                    ls='', marker=opts['marklist'][idat], ms=opts['marksize'][idat])
            idat += 1
    plt.xlabel("Log(10) real part")
    y_label = "Imaginary part ($\\times 10^{" + str(int(tenpow)) + "}$)"
    plt.ylabel(y_label)
    plt.ylim(ymin, ymax)
    #plt.xscale('log')
    plt.grid('on')
    plt.legend()
    plt.savefig(casename + "-eigs-compare." + imageformatstring, dpi=200, bbox_inches='tight')
