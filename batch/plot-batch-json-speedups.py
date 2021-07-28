
"""
Plot iterations from all JSON files in a directory, assuming only 1 file per case.
Requires the abridged JSON file from preprocessing the output of the batched benchmark.
"""

import os
import json
import re
import numpy as np
from matplotlib import pyplot as plt

def get_solver_keys(filename):
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    solver_keys = []
    for key in db[0]:
        solver_keys.append(key)
    return solver_keys


def get_data_from_file(filename, solver_keys, batch_mult):
    # Get batch size, total apply time and component apply time
    batch_size = 0
    data = np.zeros((len(solver_keys),2))
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    for i in range(len(solver_keys)):
        key = solver_keys[i]
        #batch_size = int(db[0][key]['num_batch_entries'])
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

def plot_curve(iterdict, solver_keys, imageformatstring):
    '''
    Plot one plot for all cases.
    '''
    i_direct = -1
    for isolver in range(len(solver_keys)):
        if solver_keys[isolver] == "direct":
            i_direct = isolver
            break
    if i_direct == -1:
        print("No batch direct solver found!")
        exit()
    else:
        print("Direct solver is at position " + str(i_direct))
    dep_keys = [ solver_keys[i] for i in range(len(solver_keys)) if i != i_direct ]
    print("Iterative solvers found: " + str(dep_keys))

    timings = np.zeros((len(iterdict),len(dep_keys),2))
    ref_times = np.zeros((len(iterdict),2));
    icase = 0
    for casekey in sorted(iterdict):
        cased = iterdict[casekey]
        ref_times[icase,:] = cased['timings'][i_direct,:]
        i_dep_solver = 0
        for isolver in range(len(solver_keys)):
            if isolver == i_direct:
                continue
            timings[icase,i_dep_solver,:] = cased['timings'][isolver,:]
            i_dep_solver += 1
        icase += 1

    x_labels = [ casekey for casekey in sorted(iterdict) ]
    x = np.arange(len(x_labels))
    width = 0.24
    fig,ax = plt.subplots()
    for isolver in range(len(dep_keys)):
        solver = dep_keys[isolver]
        plt.bar(x + isolver*width, ref_times[:,1]/timings[:,isolver,1], 0.8*width, align='edge', tick_label=x_labels, label=solver)
    ax.set_yscale('log') 
    plt.legend(loc="best", fontsize="medium")
    plt.xlabel("Problem")
    plt.ylabel("Speedup w.r.t. dense direct solver")
    plt.grid('on')
    plt.savefig("largest_speedup." + imageformatstring, dpi=200, bbox_inches='tight')
    return

if __name__ == "__main__":

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
            assert(batch_mult == 192)
            file_dict = get_data_from_file(filename, solver_keys, batch_mult)
            datadict[casename] = file_dict
    plot_curve(datadict, solver_keys, "png")
