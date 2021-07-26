#! /bin/env python3

import argparse
import scipy as sp
import scipy.io
import scipy.linalg
import numpy as np
from matplotlib import pyplot as plt

def get_eigenvalues(A):
    adense = A.toarray()
    w = sp.linalg.eigvals(adense)
    minreal = np.min(w.real)
    print("Smallest real part of any eigenvalue = " + str(minreal))
    return w

def plot_eigvals(w, imageformatstring):
    plt.scatter(np.log10(w.real), w.imag)
    ymax = w.imag.max()
    ymin = w.imag.min()
    yrange = ymax-ymin
    ymax += 0.1*yrange
    ymin -= 0.1*yrange
    plt.xlabel("Log(10) real part")
    plt.ylabel("Imaginary part")
    plt.ylim(ymin, ymax)
    #plt.xscale('log')
    plt.grid('on')
    plt.savefig("eigs." + imageformatstring, dpi=200, bbox_inches='tight')

if __name__ == "__main__":
    A = sp.io.mmread("A.mtx")
    w = get_eigenvalues(A)
    imageformatstring = "png"
    plot_eigvals(w, imageformatstring)
