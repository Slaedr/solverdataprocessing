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

def get_solver_and_matrix_format_keys(filename, run_type):
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    matrix_keys = []
    solver_keys = []
    for key in db[0][run_type]:
        solver_keys.append(key)
        matrix_keys.append(db[0][run_type][key]['matrix_format'])
    return solver_keys, matrix_keys

def get_data_from_file(filename, run_type, solver_name, batch_mult):
    # Get batch size and component apply time
    batch_size = 0
    data = 0.0
    mat_format = ''
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    # Assume just one solver
    dbt = db[0][run_type][solver_name]
    mat_format = dbt['matrix_format']

    batch_size = int(dbt['num_batch_entries'])
    if "solver" in run_type:
        applyre = re.compile(r'apply')
        apply_kernel_time_found = False
        for subkey in dbt['apply']['components']:
            if re.search(applyre, subkey):
                apply_kernel_time_found = True
                data = dbt['apply']['components'][subkey]
                break
        assert(apply_kernel_time_found)
    elif run_type == "spmv":
        data[i] = dbt['time']
    filedict = {}
    filedict['batch_size'] = batch_size
    filedict['batch_multiplier'] = batch_mult
    filedict['timings'] = data
    return mat_format, filedict

def plot_per_case(datadict, plotlog, opts, imageformatstring):
    '''
    Plot one plot for each case.
    '''
    plt.rcParams.update({'font.size': textsize})
    for casekey in datadict:
        plt.close()
        print("Plotting " + casekey)
        casedict = datadict[casekey]
        maxtime = 0.0
        mintime = 10000.0
        iformat = 0
        for mat_format in casedict:
            num_dupl = len(casedict[mat_format])
            print("   Potting " + mat_format + " with " + str(num_dupl) + " duplications")
            batchsizes = np.zeros(num_dupl)
            timings = np.zeros((num_dupl, 1))
            ipos = 0
            for filepart in casedict[mat_format]:
                timings[ipos,0] = filepart['timings']*1000
                batchsizes[ipos] = filepart['batch_size']
                ipos += 1
            sort_multiple(batchsizes, timings)
            if plotlog:
                plt.semilogy(batchsizes, timings[:,0], lw=opts['linewidth'], \
                    ls=opts['linetype'][iformat], color=opts['colorlist'][iformat], \
                    marker=opts['marklist'][iformat], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= mat_format)
            else:
                plt.plot(batchsizes, timings[:,0], lw=opts['linewidth'], \
                    ls=opts['linetype'][iformat], color=opts['colorlist'][iformat], \
                    marker=opts['marklist'][iformat], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= mat_format)
            thismax = np.max(timings[:,0])
            thismin = np.min(timings[:,0])
            if thismax > maxtime:
                maxtime = thismax
            if thismin < mintime:
                mintime = thismin
            iformat += 1
        plt.legend(loc="best", fontsize="medium")
        #plt.legend(loc="upper left", fontsize="medium")
        plt.tight_layout()
        plt.xlabel("No. matrices in the batch")
        plt.ylabel("Time (ms)")
        if plotlog:
            plt.grid('on',which='both')
            plt.grid('on',which='minor', ls=':', color='0.5')
        else:
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
    
    solver_keys,mat_format_keys = get_solver_and_matrix_format_keys(first_filename, args.run_type)
    print("Found runs " + str(mat_format_keys))
    print("Found solvers: " + str(solver_keys))
    if len(solver_keys) > 1:
        throw("More than one solver not supported!")
    
    for file in os.listdir(curdir):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            print("Found " + filename)
            split_ = filename.split('-')
            casename = split_[0]
            batch_mult = int(split_[-1].split('.')[0])
            print("Case " + casename + " with batch multiplier " + str(batch_mult))
    
            if casename not in datadict:
                datadict[casename] = {}
            mat_format, file_dict = get_data_from_file(filename, args.run_type, solver_keys[0],
                    batch_mult)
            if mat_format not in datadict[casename]:
                datadict[casename][mat_format] = []
            datadict[casename][mat_format].append(file_dict)

    print("")
    print("Found " + str(len(datadict)) + " different cases.")
    for casen in datadict:
        print("  Found " + str(len(datadict[casen])) + " different matrix types")
        for mat_format in datadict[casen]:
            print("      Found " + str(len(datadict[casen][mat_format])) + " different duplications")

    plot_per_case(datadict, args.log, opts, "png")

