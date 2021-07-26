
"""
Plot iterations from all JSON files in a directory, assuming only 1 file per case.
Requires the original detailed JSON output from batched benchmark.
"""

import os
import json
import argparse
import numpy as np
from matplotlib import pyplot as plt

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
    resnorms = []
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    for i in range(len(solver_keys)):
        key = solver_keys[i]
        #batch_size = int(db[0][key]['num_batch_entries'])
        resnorm_d = db[0]['batch_solver'][key]['residual_norm']
        batch_size = len(resnorm_d)
        solver_norms = [0 for i in range(batch_size)]
        for i in range(batch_size):
            solver_norms[i] = resnorm_d[str(i)][0]
        resnorms.append(solver_norms)
    bnorms = [0 for i in range(batch_size)]
    b_d = db[0]['batch_solver'][key]['rhs_norm']
    for i in range(batch_size):
        bnorms[i] = b_d[str(i)][0]
    filedict = {}
    filedict['batch_size'] = batch_size
    filedict['batch_multiplier'] = batch_mult
    filedict['residual_norm'] = resnorms
    filedict['rhs_norm'] = bnorms
    return filedict

def plot_curve(normdict, solver_keys, opts, imageformatstring, normtype, relcheck_limit):
    '''
    Plot one plot for each case.
    '''
    for casekey in normdict:
        plt.close()
        casename = normdict[casekey]
        batch_size = casename['batch_size']
        print("Batch size is " + str(batch_size))
        maxnorm = 20
        minnorm = -20
        for isolver in range(len(solver_keys)):
            norms = np.zeros((batch_size))
            b_norms = np.zeros((batch_size))
            for ipos in range(batch_size):
                norms[ipos] = casename['residual_norm'][isolver][ipos]
                b_norms[ipos] = casename['rhs_norm'][ipos]
            maxnorml = 0.0
            minnorml = 0.0
            if normtype == "absolute":
                plt.plot(np.log10(norms[:]), lw=opts['linewidth'], ls=opts['linetype'][isolver], \
                        color=opts['colorlist'][isolver], \
                        marker=opts['marklist'][isolver], ms=opts['marksize'], \
                        mew=opts['markedgewidth'], \
                        label= solver_keys[isolver])
                plt.ylabel("Log(10) residual 2-norm")
                maxnorml = np.max(norms[:])
                minnorml = np.min(norms[:])
                print("Maximum norm = " + str(maxnorml))
            else:
                plt.plot(np.log10(norms[:]/b_norms[:]), lw=opts['linewidth'], ls=opts['linetype'][isolver], \
                        color=opts['colorlist'][isolver], \
                        marker=opts['marklist'][isolver], ms=opts['marksize'], \
                        mew=opts['markedgewidth'], \
                        label= solver_keys[isolver])
                plt.ylabel("Log(10) (residual 2-norm / RHS 2-norm)")
                maxnorml = np.max(norms[:]/b_norms[:])
                minnorml = np.min(norms[:]/b_norms[:])
                print("Maximum norm = " + str(maxnorml))
                if relcheck_limit != 0.0:
                    if maxnorml > relcheck_limit:
                        print(solver_keys[isolver] + " DID NOT CONVERGE TO TOLERANCE " + str(relcheck_limit) + "!!")
            if maxnorml > maxnorm:
                maxnorm = maxnorml
            if minnorml < minnorm:
                minnorm = minnorml
        plt.legend(loc="best", fontsize="medium")
        #plt.legend(loc="upper left", fontsize="medium")

        if minnorm < 1e-30:
            if normtype == "relative":
                minnorm = 1e-30
            else:
                minnorm = 1e-40
        if normtype == "absolute":
            if maxnorm > 1e-12:
                plt.ylim(0.9*np.log10(minnorm), -12)
        else:
            if maxnorm > 1:
                plt.ylim(0.9*np.log10(minnorm), 0)
        plt.xlabel("Matrix index in the batch")
        plt.grid('on')
        outfname = casekey + "-" + normtype + "-resnorms." + imageformatstring
        plt.savefig(outfname, dpi=200, bbox_inches='tight')
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = "Plot residual norms of a batch problem.")
    parser.add_argument('--type', default = "relative", help = "Plot \'absolute\' or \'relative\' norm")
    parser.add_argument('--relative_check', default = 0.0, type=float, help = "Threshold value that all relative norms should be below")
    args = parser.parse_args()
    print("Norm type to plot: " + args.type + ", relative check threshold = " + str(args.relative_check))

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
    plot_curve(datadict, solver_keys, opts, "png", args.type, args.relative_check)
