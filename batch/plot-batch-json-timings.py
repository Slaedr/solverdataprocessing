#! /bin/env python3

'''
Plots Ginkgo batch solver runtimes from processed JSON input.

We assume:
- all files have the same solvers.
- all solvers in a file have the same batch size
'''

import os
import json
import re
import numpy as np
from matplotlib import pyplot as plt

from utils import sort_multiple

textsize = 16

def get_data_from_file(filename, solver_keys, batch_mult):
    # Get batch size[0], total apply time[1] and component apply time[2]
    batch_size = 0
    data = np.zeros((len(solver_keys),2))
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    for i in range(len(solver_keys)):
        key = solver_keys[i]
        batch_size = int(db[0][key]['num_batch_entries'])
        data[i,0] = db[0][key]['apply']['time']
        applyre = re.compile(r'apply')
        apply_kernel_time_found = False
        for subkey in db[0][key]['apply']['components']:
            if re.search(applyre, subkey):
                apply_kernel_time_found = True
                data[i,1] = db[0][key]['apply']['components'][subkey]
                break
        assert(apply_kernel_time_found)
    filedict = {}
    filedict['batch_size'] = batch_size
    filedict['batch_multiplier'] = batch_mult
    filedict['timings'] = data
    return filedict

def get_solver_keys(filename):
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    solver_keys = []
    for key in db[0]:
        solver_keys.append(key)
    return solver_keys

def plot_per_case(datadict, solver_keys, opts, imageformatstring):
    '''
    Plot one plot for each case.
    '''
    plt.rcParams.update({'font.size': textsize})
    for casekey in datadict:
        plt.close()
        casename = datadict[casekey]
        num_dupl = len(casename)
        #plotarrs = []
        batchsizes = np.zeros(num_dupl)
        maxtime = 0.0
        mintime = 10000.0
        for isolver in range(len(solver_keys)):
            #plotarrs.append(np.zeros(num_dupl,2))
            timings = np.zeros((num_dupl, 2))
            ipos = 0
            #solverkey = solver_keys[i]
            for filepart in casename:
                timings[ipos,0] = filepart['timings'][isolver,0]
                timings[ipos,1] = filepart['timings'][isolver,1]
                batchsizes[ipos] = filepart['batch_size']
                ipos += 1
            sort_multiple(batchsizes, timings)
            plt.plot(batchsizes, timings[:,1], lw=opts['linewidth'], \
                    ls=opts['linetype'][isolver], color=opts['colorlist'][isolver], \
                    marker=opts['marklist'][isolver], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= solver_keys[isolver])
            thismax = np.max(timings[:,1])
            thismin = np.min(timings[:,1])
            if thismax > maxtime:
                maxtime = thismax
            if thismin < mintime:
                mintime = thismin
        plt.legend(loc="best", fontsize="medium")
        plt.tight_layout()
        yrange = maxtime-mintime
        plt.ylim(mintime-0.1*yrange, maxtime+0.1*yrange)
        #plt.legend(loc="upper left", fontsize="medium")
        plt.xlabel("No. matrices in the batch")
        plt.ylabel("Time (s)")
        plt.grid('on')
        plt.savefig(casekey+"-timings." + imageformatstring, dpi=200, bbox_inches='tight')
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
    
    datadict = {}
    first_filename = ""
    
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
    
            if casename not in datadict:
                datadict[casename] = []
            file_dict = get_data_from_file(filename, solver_keys, batch_mult)
            datadict[casename].append(file_dict)

    plot_per_case(datadict, solver_keys, opts, "png")
