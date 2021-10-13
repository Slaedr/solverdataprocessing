#! /bin/env python3

'''
Outputs a table of Ginkgo batch solver runtimes from JSON input.

We assume:
- all files have the same solvers.
- all solvers in a file have the same batch size
'''

import os
import json
import re
import argparse
import numpy as np
import pandas as pd
#from matplotlib import pyplot as plt

from utils import sort_multiple

def get_data_from_file(filename, batch_mult):
    """ Assumes only one one solver dataset per file.
    """
    batch_size = 0
    times = []
    solver_names = []
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    for key in db[0]['batch_solver']:
        solver_names.append(key)
        batch_size = int(db[0]['batch_solver'][key]['num_batch_entries'])
        #totalapplytime = db[0]['batch_solver'][key]['apply']['time']
        applyre = re.compile(r'apply')
        apply_kernel_time_found = False
        for subkey in db[0]['batch_solver'][key]['apply']['components']:
            if re.search(applyre, subkey):
                apply_kernel_time_found = True
                times.append(db[0]['batch_solver'][key]['apply']['components'][subkey])
                break
        assert(apply_kernel_time_found)
    return batch_size, times, solver_names

def output_per_case(batch_sizes, data, case_name, solver_name, norm_type, matrix_format,
        backend):
    assert(len(batch_sizes) == len(data))
    bsizes = np.array(batch_sizes, dtype=int)
    timesm = np.zeros((len(data),1))
    timesm[:,0] = data[:]
    sort_multiple(bsizes, timesm)
    times = timesm[:,0]
    df = pd.DataFrame({ "processor":backend, "case name": case_name, "solver type": solver_name, 
        "matrix format": matrix_format, "tolerance type": norm_type,
        "batch size": bsizes, "solve time (s)": times})
    df.to_csv(case_name + ".txt", sep=' ', index=False)
    return

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description = "Extract timing data of a batch problem")
    parser.add_argument('--norm_type', default = "relative", help = "\'absolute\' or \'relative\' norm")
    parser.add_argument('--matrix_format', help = "matrix format name")
    parser.add_argument('--processor', default='CPU', help = "Processor on which runs were performed")
    args = parser.parse_args()

    print("Processor = ", args.processor)

    curdir = os.getcwd()

    data = []
    labels = []
    batch_sizes = []
    solver_name = ""
    case_name = ""
    
    for filen in os.listdir(curdir):
        if filen.endswith("json"):
            fsplit = filen.split('.')[0].split('-')
            batch_mult = int(fsplit[-1])
            case_name = fsplit[0]
            print("Case " + case_name + " with batch multiplier " + str(batch_mult))

            batch_size = 0
            times = []
            if "block" in filen:
                #batch_size, times = get_data_from_block_file(dirpath + os.sep + filen, batch_mult)
                #assert(len(times) == 1)
                throw("Block output file not yet supported!")
            else:
                batch_size, times, solver_names = get_data_from_file(curdir + os.sep + filen, batch_mult)
                assert(len(times) == 1)
            batch_sizes.append(batch_size)
            data.append(times[0])
            solver_name = solver_names[0]

    output_per_case(batch_sizes, data, case_name, solver_name, args.norm_type, args.matrix_format,
            args.processor)
