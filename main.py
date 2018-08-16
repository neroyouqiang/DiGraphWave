# -*- coding: utf-8 -*-

import argparse
import numpy as np
import pickle
from time import time
from itertools import combinations, permutations

from mydata import load_datas


if __name__ == '__main__':
    # parser
    # FLAGS, unparsed = parser.parse_known_args()
    
    # input data
    As, Vs = load_datas()
    As = As[0:3]
    
    # init sum matrix
    size_sum = 0
    for A in As:
        size_sum += len(A)
    
    # construct sum matrix
    A_sum = np.zeros([size_sum, size_sum], dtype=float)
    ss = 0
    ee = 0
    for ii in xrange(len(As)):
        ss = ee
        ee = ee + len(As[ii])
        A_sum[ss: ee, ss: ee] = As[ii]
    
    # Laplacian matrix
    A_sum = A_sum + A_sum.T
    D_sum = np.diag(A_sum.sum(axis=0))
    L_sum = D_sum - A_sum
    # L_sum = np.sqrt(D_sum).dot(L_sum).dot(np.sqrt(D_sum))
    
    # eigen values and vectors
    eig_val_sum, eig_vec_sum = np.linalg.eig(L_sum)
    
    eig_vals = []
    eig_vecs = []
    ss = 0
    ee = 0
    for ii in xrange(len(As)):
        ss = ee
        ee = ee + len(As[ii])
        eig_vals.append(eig_val_sum[ss: ee])
        eig_vecs.append(eig_vec_sum[ss: ee, ss: ee])