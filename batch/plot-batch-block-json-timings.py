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
import argparse
import numpy as np
from matplotlib import pyplot as plt

from utils import sort_multiple

textsize = 12

def get_data_from_file(filename, batch_mult):
    # Get batch size[0], total apply time[1] and component apply time[2]
    batch_size = 0
    times = []
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    for key in db[0]['batch_solver']:
        batch_size = int(db[0]['batch_solver'][key]['num_batch_entries'])
        totalapplytime = db[0]['batch_solver'][key]['apply']['time']
        applyre = re.compile(r'apply')
        apply_kernel_time_found = False
        time = 0.0
        for subkey in db[0]['batch_solver'][key]['apply']['components']:
            if re.search(applyre, subkey):
                apply_kernel_time_found = True
                times.append(db[0]['batch_solver'][key]['apply']['components'][subkey])
                break
        assert(apply_kernel_time_found)
    return batch_size, times

def get_data_from_block_file(filename, batch_mult):
    # Get batch size[0], total apply time[1] and component apply time[2]
    batch_size = 0
    times = []
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    for key in db[0]['solver']:
        batch_size = int(db[0]['solver'][key]['num_batch_entries'])
        times.append(db[0]['solver'][key]['apply']['time'])
    return batch_size, times

def plot_per_case(batch_sizes, data, labels, opts, imageformatstring, is_log):
    plt.rcParams.update({'font.size': textsize})
    plt.close()
    assert(len(batch_sizes) == len(data))
    for i in range(len(batch_sizes)):
        times = np.zeros((len(data[i]),1))
        times[:,0] = data[i][:]
        bsizes = np.array(batch_sizes[i], dtype=int)
        sort_multiple(bsizes, times)
        if is_log:
            plt.semilogy(bsizes, times, lw=opts['linewidth'], \
                    ls=opts['linetype'][i], color=opts['colorlist'][i], \
                    marker=opts['marklist'][i], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= labels[i])
        else:
            plt.plot(bsizes, times, lw=opts['linewidth'], \
                    ls=opts['linetype'][i], color=opts['colorlist'][i], \
                    marker=opts['marklist'][i], ms=opts['marksize'], \
                    mew=opts['markedgewidth'], \
                    label= labels[i])
    plt.legend(loc="best", fontsize="medium")
    plt.tight_layout()
    plt.xlabel("No. matrices in the batch")
    plt.ylabel("Time (s)")
    plt.grid('on')
    plt.savefig("timings." + imageformatstring, dpi=200, bbox_inches='tight')
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
        description = "Plot timing comparison of a batch problem, potentially against a block solution")
    parser.add_argument('--log', help = "Plot \'absolute\' or \'relative\' norm",
            action="store_true")
    args = parser.parse_args()

    curdir = os.getcwd()

    data = []
    labels = []
    batch_sizes = []
    
    for dire in os.listdir(curdir):
        dirname = os.fsdecode(dire)
        dirpath = curdir + os.sep + dirname
        if not os.path.isdir(dirpath):
            continue
        print("Found " + dirname)
        split_ = dirname.split('-')
        descript = split_[-1]
        labels.append(descript)
        data.append([])
        batch_sizes.append([])
        for filen in os.listdir(dirpath):
            if filen.endswith("json"):
                fsplit = filen.split('.')[0].split('-')
                batch_mult = int(fsplit[-1])
                print("Case " + descript + " with batch multiplier " + str(batch_mult))

                batch_size = 0
                times = []
                if "block" in dirname:
                    batch_size, times = get_data_from_block_file(dirpath + os.sep + filen, batch_mult)
                    assert(len(times) == 1)
                else:
                    batch_size, times = get_data_from_file(dirpath + os.sep + filen, batch_mult)
                    assert(len(times) == 1)
                batch_sizes[-1].append(batch_size)
                data[-1].append(times[0])

    plot_per_case(batch_sizes, data, labels, opts, "png", args.log)
