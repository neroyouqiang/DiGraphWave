# -*- coding: utf-8 -*-
import numpy as np


def vertice_label(As, Vs):
    global Label_Dim
    
    Vmap = {}
    Vmap_index = 0
    
    # get vertice map
    for ii in xrange(len(Vs)):
        for jj in xrange(len(Vs[ii])):
            if not Vmap.has_key(Vs[ii][jj]):
                Vmap[Vs[ii][jj]] = Vmap_index
                Vmap_index += 1
                
    # combined adjacent index
    N = len(Vmap.keys())
    Ac = np.zeros([N, N], dtype=float)
    for ii in xrange(len(As)):
        for key1 in Vmap.keys():
            for key2 in Vmap.keys():
                if key1 != key2:
                    A = As[ii][Vs[ii] == key1][:, Vs[ii] == key2]
                    Ac[Vmap[key1], Vmap[key2]] = A.sum()
                    
    # node embedding
    eig_vals, eig_vecs = np.linalg.eig(Ac)
    eig_index = eig_vals.argsort()[::-1]
    
    dim = min(Label_Dim, len(eig_index) - 1)
    labels = eig_vecs[eig_index[0: dim], :].T
    
    # map the labels
    Vs_return = []
    for ii in xrange(len(Vs)):
        Vs_return.append(np.zeros([len(Vs[ii]), dim], dtype=float))
        for jj in xrange(len(Vs[ii])):
            Vs_return[ii][jj, :] = labels[Vmap[Vs[ii][jj]]]
            
    # return
    return Vs_return


def vertice_reshape(Vs):
    Vs = list(Vs)
    for ii in xrange(len(Vs)):
        Vs[ii] = Vs[ii].reshape(-1, 1)
        
    return Vs
    

Label_Dim = 0
def init():
    global Label_Dim
    
    Label_Dim = 2
    
init()