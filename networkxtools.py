# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx


def get_adjacent_matrix(G, defval=1):
    A = np.zeros([len(G.nodes), len(G.nodes)], dtype=float)
    
    nodes = list(G.nodes)
    for ii in xrange(len(nodes)):
        node_i = nodes[ii]
        for jj in xrange(len(nodes)):
            node_j = nodes[jj]
            if node_j in G[node_i]:
                if G[node_i][node_j].has_key('weight'):
                    A[ii, jj] = G[node_i][node_j]['weight']
                else:
                    A[ii, jj] = defval
            
    return A


def get_vertice_list(G, defval=1):
    V = np.zeros([len(G.nodes)], dtype=float)
    
    nodes = list(G.nodes)
    for ii in xrange(len(nodes)):
        node = nodes[ii]
        if G.nodes[node].has_key('weight'):
            V[ii] = G.nodes[node]['weight']
        else:
            V[ii] = defval
            
    return V


def get_grid_graph(dim):
    
    G = nx.grid_2d_graph(dim, dim)
    A = get_adjacent_matrix(G)
    V = get_vertice_list(G)
    
    # 2 5 6 8
    # V[5] = 2
    V[2] = 2
    
    return A, V