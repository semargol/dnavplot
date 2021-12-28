#!/usr/bin/python3
import sys
import os
import argparse
import numpy as np


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile',
                        required=True, type=argparse.FileType('rb'))
    parser.add_argument('-o', '--out', default='tmp/',
                        required=False)
    parser.add_argument('-t', '--time',
                        required=False, type=str)
    return parser

if __name__ == '__main__':
    print('Import data:')
    parser = createParser()
    ns = parser.parse_args(sys.argv[1:])
    #d = np.genfromtxt(ns.infile, names=True, delimiter="\t")
    d = np.genfromtxt(ns.infile, names=True)
    d_len = len(d)

    os.makedirs(os.path.dirname(ns.out), exist_ok=True)


    for name in d.dtype.names:
        print('\t' + name)
        outarr = np.zeros(d_len * 2, dtype='d')
        if ns.time == None:
            outarr[0::2] = d[d.dtype.names[0]]
        else:
            outarr[0::2] = d['time']
        outarr[1::2] = d[name]
        f = open(ns.out + name + '.dat', 'wb')
        outarr.tofile(f)
        f.close()
