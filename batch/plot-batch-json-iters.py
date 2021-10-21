
"""
Plot iterations from all JSON files in a directory, assuming only 1 file per case.
Requires the original detailed JSON output from batched benchmark.
"""

import os
import json
import numpy as np
from matplotlib import pyplot as plt

textsize = 14

def get_solver_keys(filename):
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    solver_keys = []
    for key in db[0]['batch_solver']:
        solver_keys.append(key)
    return solver_keys


def get_data_from_file(filename, solver_keys, batch_mult):
    # Get batch size[0], total apply time[1] and component apply time[2]
    batch_size = 0
    iters = []
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    for i in range(len(solver_keys)):
        key = solver_keys[i]
        #batch_size = int(db[0][key]['num_batch_entries'])
        numiters_d = db[0]['batch_solver'][key]['num_iters']
        batch_size = len(numiters_d)
        solver_iters = [0 for i in range(batch_size)]
        for i in range(batch_size):
            solver_iters[i] = numiters_d[str(i)][0]
        iters.append(solver_iters)
    filedict = {}
    filedict['batch_size'] = batch_size
    filedict['batch_multiplier'] = batch_mult
    filedict['num_iters'] = iters
    return filedict

def plot_curve(iterdict, solver_keys, opts, imageformatstring):
    '''
    Plot one plot for each case.
    '''
    plt.rcParams.update({'font.size': textsize})
    for casekey in iterdict:
        plt.close()
        casename = iterdict[casekey]
        batch_size = casename['batch_size']
        print("Batch size is " + str(batch_size))
        for isolver in range(len(solver_keys)):
            timings = np.zeros((batch_size))
            for ipos in range(batch_size):
                timings[ipos] = casename['num_iters'][isolver][ipos]
            plt.plot(timings[:], lw=opts['linewidth'], ls=opts['linetype'][isolver], \
                    color=opts['colorlist'][isolver], \
                    marker=opts['marklist'][isolver], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= solver_keys[isolver])
        plt.legend(loc="best")
        #plt.legend(loc="upper left", fontsize="medium")
        plt.xlabel("Matrix index in the batch")
        plt.ylabel("Iterations")
        plt.grid('on')
        plt.savefig(casekey+"-iters." + imageformatstring, dpi=200, bbox_inches='tight')
    return

if __name__ == "__main__":

    opts = { \
         "marklist" : ['.', 'x', '+', '^', 'v', '<', '>', 'd'],
         "colorlist" : ['k', 'b', 'r', 'g', 'c', 'm', 'orange', 'pink'],
         "linetype" : ['-', '--', '-.', ':', '--', '-.', '--',':'],
         "linewidth" : 0.75,
         "marksize" : 5,
         "markedgewidth" : 1 \
         } 

    curdir = os.getcwd()

    first_filename = ""
    datadict = {}
    
    for file in os.listdir(curdir):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            first_filename = filename
            break
    if first_filename == "":
        print("No JSON files found in the current directory.")
        exit()
    solver_keys = get_solver_keys(first_filename)
    print("Found solvers" + str(solver_keys))

    for file in os.listdir(curdir):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            print("Found " + filename)
            split_ = filename.split('_')
            casename = '_'.join(split_[0:-1])
            batch_mult = int(split_[-1].split('.')[0][1:])
            print("Case " + casename + " with batch multiplier " + str(batch_mult))
            assert(batch_mult == 1)
            file_dict = get_data_from_file(filename, solver_keys, batch_mult)
            datadict[casename] = file_dict
    plot_curve(datadict, solver_keys, opts, "png")
