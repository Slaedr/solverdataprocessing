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

def plot_eigvals(w, casename, imageformatstring):
    plt.close()
    plt.rcParams.update({'font.size': textsize})
    fig,ax = plt.subplots()
    ymax = w.imag.max()
    ymin = w.imag.min()
    # Scale y-axis to ~1 and append the multiplier to the y label
    tenpow = np.log10(ymax)
    tenpow = math.floor(tenpow)
    ymax = ymax / math.pow(10,tenpow)
    ymin = ymin / math.pow(10,tenpow)
    yrange = ymax-ymin
    ymax += 0.1*yrange
    ymin -= 0.1*yrange
    plt.scatter(np.log10(w.real), w.imag/math.pow(10,tenpow))
    #plt.xlabel("Log(10) real part", fontsize=textsize)
    #plt.ylabel("Imaginary part", fontsize = textsize-1)
    plt.xlabel("Log(10) real part")
    y_label = "Imaginary part ($\\times 10^{" + str(int(tenpow)) + "}$)"
    plt.ylabel(y_label)
    plt.ylim(ymin, ymax)
    #plt.xscale('log')
    plt.grid('on')
    plt.savefig(casename + "-eigs." + imageformatstring, dpi=200, bbox_inches='tight')

if __name__ == "__main__":
    curdir = os.getcwd()
    for file in os.listdir(curdir):
        filename = os.fsdecode(file)
        if filename.endswith(".mtx"):
            print("Found " + filename)
            split_ = filename.split('.')
            casename = split_[0]
            A = sp.io.mmread(filename)
            w = get_eigenvalues(A)
            imageformatstring = "png"
            plot_eigvals(w, casename, imageformatstring)
