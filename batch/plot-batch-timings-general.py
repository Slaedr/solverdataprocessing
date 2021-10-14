#! /bin/env python3

'''
Plots Ginkgo runtimes from processed JSON input.
Works for run types SpMVs and batch solvers for now.

We assume:
- all files have the same categories (matrix formats, solver types, etc.)
- all categories in a file have the same batch size
'''

import os
import json
import re
import argparse
import numpy as np
from matplotlib import pyplot as plt

from utils import sort_multiple

#textsize = 16
textsize = 12

def get_solver_keys(filename, run_type):
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    solver_keys = []
    for key in db[0][run_type]:
        solver_keys.append(key)
    return solver_keys

def get_data_from_file(filename, run_type, solver_keys, batch_mult):
    # Get batch size and component apply time
    batch_size = 0
    data = [0.0 for i in solver_keys]
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    dbt = db[0][run_type]
    for i in range(len(solver_keys)):
        key = solver_keys[i]
        batch_size = int(dbt[key]['num_batch_entries'])
        #data[i] = dbt[key]['apply']['time'] # Total apply time
        if "solver" in run_type:
            applyre = re.compile(r'apply')
            apply_kernel_time_found = False
            for subkey in dbt[key]['apply']['components']:
                if re.search(applyre, subkey):
                    apply_kernel_time_found = True
                    data[i] = dbt[key]['apply']['components'][subkey]
                    break
            assert(apply_kernel_time_found)
        elif run_type == "spmv":
            data[i] = dbt[key]['time']
    filedict = {}
    filedict['batch_size'] = batch_size
    filedict['batch_multiplier'] = batch_mult
    filedict['timings'] = data
    return filedict

def plot_per_case(datadict, solver_keys, plotlog, opts, imageformatstring):
    '''
    Plot one plot for each case.
    '''
    plt.rcParams.update({'font.size': textsize})
    for casekey in datadict:
        plt.close()
        casename = datadict[casekey]
        num_dupl = len(casename)
        batchsizes = np.zeros(num_dupl)
        maxtime = 0.0
        mintime = 10000.0
        for isolver in range(len(solver_keys)):
            timings = np.zeros((num_dupl, 1))
            ipos = 0
            for filepart in casename:
                timings[ipos,0] = filepart['timings'][isolver]*1000
                batchsizes[ipos] = filepart['batch_size']
                ipos += 1
            sort_multiple(batchsizes, timings)
            if plotlog:
                plt.semilogy(batchsizes, timings[:,0], lw=opts['linewidth'], \
                    ls=opts['linetype'][isolver], color=opts['colorlist'][isolver], \
                    marker=opts['marklist'][isolver], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= solver_keys[isolver])
            else:
                plt.plot(batchsizes, timings[:,0], lw=opts['linewidth'], \
                    ls=opts['linetype'][isolver], color=opts['colorlist'][isolver], \
                    marker=opts['marklist'][isolver], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= solver_keys[isolver])
            thismax = np.max(timings[:,0])
            thismin = np.min(timings[:,0])
            if thismax > maxtime:
                maxtime = thismax
            if thismin < mintime:
                mintime = thismin
        plt.legend(loc="best", fontsize="medium")
        #plt.legend(loc="upper left", fontsize="medium")
        plt.tight_layout()
        plt.xlabel("No. matrices in the batch")
        if plotlog:
            plt.ylabel("Log time (log ms)")
            plt.grid('on',which='both')
            plt.grid('on',which='minor', ls=':', color='0.5')
        else:
            plt.ylabel("Time (ms)")
            yrange = maxtime-mintime
            plt.ylim(mintime-0.1*yrange, maxtime+0.1*yrange)
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

    parser = argparse.ArgumentParser(
        description = "Plot timing comparison of for different types of runs")
    parser.add_argument('--log', help = "For log y axis",
            action="store_true")
    parser.add_argument("--run_type", help = "\'spmv\' or \'batch_solver\'")
    args = parser.parse_args()

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
    
    solver_keys = get_solver_keys(first_filename, args.run_type)
    print("Found runs " + str(solver_keys))
    
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
            file_dict = get_data_from_file(filename, args.run_type, solver_keys,
                    batch_mult)
            datadict[casename].append(file_dict)

    print("Found " + str(len(datadict)) + " different cases.")

    plot_per_case(datadict, solver_keys, args.log, opts, "png")

