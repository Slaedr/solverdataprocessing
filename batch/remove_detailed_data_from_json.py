#! /usr/bin/env python3

import os
import json

def process_file(filename, keep_iters_res):
    ''' From the given file, extracts only timing data by default.
    Ignores the norms and iterations by default.
    @param keep_iters_res  If True, keeps true residual norms and iterations.
    '''
    infile = open(filename, 'r')
    db = json.load(infile)
    infile.close()
    outdb = []
    outdb.append({})
    run_type = 'batch_solver'
    if run_type not in db[0]:
        raise Exception("Could not find key " + run_type + "!")
    indb = db[0][run_type]
    outdb[0]['problem'] = db[0]['problem']
    outdb[0][run_type] = {}
    for key in indb:
        print("  Found solver: " + key)
        outdb[0][run_type][key] = {}
        outsec = outdb[0][run_type][key]
        outsec['matrix_format'] = indb[key]['matrix_format']
        outsec['scaling'] = indb[key]['scaling']
        nbatch_key = len(indb[key]['rhs_norm'])
        outsec['num_batch_entries'] = nbatch_key
        outsec['generate'] = indb[key]['generate']
        outsec['apply'] = {}
        outsec['apply']['components'] = indb[key]['apply']['components']
        outsec['apply']['time'] = indb[key]['apply']['time']
        if keep_iters_res:
            outsec['num_iters'] = indb[key]['num_iters']
            outsec['residual_norm'] = indb[key]['residual_norm']
    outfilename = filename + ".processed"
    outfile = open(outfilename, 'w')
    outstring = json.dumps(outdb, indent=4)
    outfile.write(outstring)
    outfile.close()

curdir = os.getcwd()

for file in os.listdir(curdir):
    filename = os.fsdecode(file)
    if filename.endswith(".json"):
        print("Processing " + filename)
        process_file(filename, False)
    else:
        continue

