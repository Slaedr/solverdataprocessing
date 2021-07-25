#! /bin/env python3

import argparse
import scipy as sp
import scipy.io
import scipy.linalg
from matplotlib import pyplot as plt

def get_eigenvalues(A):
	adense = A.toarray()
	w = sp.linalg.eigvals(adense)
	return w

def plot_eigvals(w):
	plt.scatter(w.real, w.imag)
	ymax = w.imag.max()
	ymin = w.imag.min()
	yrange = ymax-ymin
	ymax += 0.1*yrange
	ymin -= 0.1*yrange
	plt.ylim(ymin, ymax)
	plt.grid('on')
	plt.show()

if __name__ == "__main__":
	A = sp.io.mmread("A.mtx")
	w = get_eigenvalues(A)
	plot_eigvals(w)
