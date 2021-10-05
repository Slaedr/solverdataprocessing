import numpy as np

def sort_multiple(base, dependent):
    # Simple insertion sort
    # depenent is a numpy 2D array
    N = len(base)
    m = dependent.shape[1]
    for i in range(N-1):
        maxn = 0
        for j in range(N-i):
            if base[j] > base[maxn]:
                maxn = j
        temp = base[maxn]
        base[maxn] = base[N-i-1]
        base[N-i-1] = temp
        temp = np.zeros((1,m))
        temp[0,:] = dependent[maxn,:]
        dependent[maxn,:] = dependent[N-i-1,:]
        dependent[N-i-1,:] = temp[0,:]
