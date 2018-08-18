# -*- coding: utf-8 -*-

import argparse
import numpy as np
import pandas as pd
import pickle
from time import time
#import matplotlib.pyplot as plt

from loaddata import load_datas
from networkxtools import get_grid_graph
from graphwavelet import cal_embedding, cal_distances
from graphwavelet import init as graphwavelet_init
from verticelabel import vertice_label, vertice_reshape


parser = argparse.ArgumentParser()
parser.add_argument('--directed', action = 'store_true',
                    help = 'Whether the graph is directed graph or not. ')
parser.add_argument('--relabel', action = 'store_false',
                    help = 'Whether to relabel the vertice or not. ')
parser.add_argument('--cal_distance', action = 'store_false',
                    help = 'Whether to calculate the distance between the embedded vertice or not. ')


def save_embeddings(embeddings, Vs):
    start = 0
    end = 0
    for ii in xrange(len(Vs)):
        start = end
        end = end + len(Vs[ii])
        np.savetxt('./saves/results/embeddings_%d.csv' % ii, embeddings[start: end], delimiter=',')
        

def save_distances(distances, Vs):
    columns = []
    index = []
    for ii in xrange(len(Vs)):
        for jj in xrange(len(Vs[ii])):
            columns.append("G%d-N%d" % (ii, jj))
            index.append("G%d-N%d" % (ii, jj))
    
    df = pd.DataFrame(distances, columns=columns, index=index)
    df.to_csv('./saves/results/embeddings_dist.csv', sep=',')


if __name__ == '__main__':
    # parser
    FLAGS, unparsed = parser.parse_known_args()
    
    # input data
    As, Vs = load_datas()
    
#    As = [As[2] + As[2].T * 1, As[1] + As[1].T * 1]
#    Vs = [Vs[2], Vs[1]]
    
    As = [As[2] + As[2].T * 0]
    Vs = [Vs[2]]
    
#    # test file 6
#    As = [As[5] + As[5].T * 0]
#    Vs = [Vs[5]]
    
#    # test file 5
#    As = [As[4] + As[4].T * 0]
#    Vs = [Vs[4]]
    
#    As = []
#    Vs = []
#    for dim in xrange(3, 4):
#        A, V = get_grid_graph(dim)
#        As.append(A)
##        Vs.append(np.array(['a', 'a', 'b', 'a', 'a', 'a', 'a', 'a', 'a']))
#        Vs.append(V)
        
    # label the vertice
    if FLAGS.relabel:
        start = time()
        Vs = vertice_label(As, Vs)
        print 'Time of vertice labeling:', time() - start
    else:
        Vs = vertice_reshape(Vs)
    
    # whether directed
    if FLAGS.directed or True:
        graphwavelet_init(is_directed=True)
#        for ii in xrange(len(As)):
#            As[ii] = As[ii] - As[ii].T
    else:
        graphwavelet_init(is_directed=False)
            
    # emebedding
    start = time()
    embeddings, Lamdas, Tfs = cal_embedding(As, Vs)
    print 'Time of embedding:',  time() - start
    
    # save
    save_embeddings(embeddings, Vs)
    
    # calculate distance
    if FLAGS.cal_distance:
        start = time()
        dist = cal_distances(embeddings)
        print 'Time of calculating distances:',  time() - start
        
        # save
        save_distances(dist, Vs)
    