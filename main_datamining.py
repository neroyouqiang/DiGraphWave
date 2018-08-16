# -*- coding: utf-8 -*-

import argparse
import numpy as np
import pickle
# import MySQLdb
from time import time
from itertools import combinations, permutations

from mydata import load_datas, get_min_graph_size


parser = argparse.ArgumentParser()
parser.add_argument('--min_support', type = float, default = '1.0', 
                    help = 'Minimum suport of the frequent subgraph.')
parser.add_argument('--max_size', type = int, default = '-1', 
                    help = 'Maximum size of the common subgraph. -1 means not limited.')

# Test_1 = []
# Test_2 = []

def generate_bigger_subgraph(As, Vs, subgraphs_1):
    # global Test_1
    # global Test_2
    # data to return
    subgraphs_k = []
    
    # init or calculate
    if subgraphs_1 == []:
        # generate 1 size subgraphs
        for ii in xrange(len(As)):
            A = As[ii]
            V = Vs[ii]
            subgraphs_k.append([])
            for n in xrange(len(V)):
                subgraphs_k[ii].append({'nodes':[n], 'edges':np.zeros((1, 1), dtype=int)})
                # if(A[n, n] != 0):
                #     subgraphs_k[ii].append({'nodes':[n], 'edges':np.ones((1, 1), dtype=int)})    
            # subgraphs_k.append([[x] for x in xrange(len(V))])
    else: 
        # generate k+1 size subgraphs
        for ii in xrange(len(As)):# xrange(len(As)):
            A = As[ii]
            # V = Vs[ii]
            subgraph_1 = subgraphs_1[ii]
            subgraph_k = []
            for mynodes in subgraph_1:
                nodes = mynodes["nodes"] # nodes list
                edges = mynodes["edges"] # edges matrix
                
                # get connected nodes
                connected_yesno_r = A[nodes, :].any(axis=0)
                connected_yesno_c = A[:, nodes].any(axis=1)
                connected_yesno = connected_yesno_r | connected_yesno_c
                connected_nodes = np.argwhere(connected_yesno).reshape(-1).tolist()
                
                # traverse connected nodes
                for connected_node in connected_nodes:
                    if connected_node not in nodes:
                        # create nodes list
                        nodes_k = list(nodes)
                        
                        # insert and sort nodes list
                        for pp in xrange(len(nodes_k) + 1):
                            if pp == len(nodes_k):
                                nodes_k.append(connected_node)
                            elif nodes_k[pp] > connected_node:
                                nodes_k.insert(pp, connected_node)
                                break;
                                
                        # get connected edges
                        connected_edges = []
                        for nn in nodes:
                            if A[nn, connected_node]:
                                connected_edges.append([nn, connected_node])
                            if A[connected_node, nn]:
                                connected_edges.append([connected_node, nn])
                        
                        # traverse connected edges
                        for edge_num in xrange(len(connected_edges)):
                            for ees in combinations(connected_edges, edge_num + 1):
                                # create edges matrix
                                edges_k = np.zeros(A.shape, dtype=int)
                                edges_k_t = edges_k[nodes, :]
                                edges_k_t[:, nodes] = edges.copy()
                                edges_k[nodes, :] = edges_k_t
                                
                                for ee in ees:
                                    edges_k[ee[0], ee[1]] = 1
                                edges_k = edges_k[nodes_k, :][:, nodes_k]
                            
                                # insert edges matrix
                                mynodes_k = {}
                                mynodes_k["nodes"] = nodes_k
                                mynodes_k["edges"] = edges_k
                                
                                # add new node set
                                for tt in xrange(len(subgraph_k) + 1):
                                    if tt == len(subgraph_k):
                                        subgraph_k.append(mynodes_k)
                                    elif mynodes_k["nodes"] == subgraph_k[tt]["nodes"]:
                                        if (mynodes_k["edges"] == subgraph_k[tt]["edges"]).all():
                                            break;
                                            
                                # if nodes_k not in subgraph_k:
                                #     subgraph_k.append(nodes_k)
            
            # add to data list
            subgraphs_k.append(subgraph_k)
        
    # return
    return subgraphs_k


def subgraphs_group(As, Vs, subgraphs): 
    # data to return
    subgraph_groups = {}
    
    # used for list corresponding to each data
    # data_list = []
    # for ii in xrange(len(subgraphs)):
    #     data_list.append([])
                    
    for ii in xrange(len(subgraphs)):
        subgraph = subgraphs[ii]
        A = As[ii]
        V = Vs[ii]
        for mynodes in subgraph:
            nodes = mynodes["nodes"] # nodes list
            edges = mynodes["edges"] # edges matrix
                
            # count vertex label number
            label_array = []
            for label in V[nodes]:
                # add array items
                for tt in xrange(label - len(label_array)):
                    label_array.append(0)
                # counting
                label_array[label - 1] += 1
            
            # count edge label number
            # edge_array = []
            # for eii in xrange(edges.shape[0]):
            #     for ejj in xrange(edges.shape[1]):
            #         edge = edges[eii, ejj]
            #         label = A[nodes[eii], nodes[ejj]]
            #         if edge > 0 and label > 0:
            #             # add array items
            #             for tt in xrange(label - len(edge_array)):
            #                 edge_array.append(0)
            #             # counting
            #             edge_array[label - 1] += 1
                
            # count edge number
            edge_num = edges.sum()
            
            # generate subgraph label 
            assert edge_num <= 1000, 'There are too many edges'
            name = '%03d' % edge_num
            
            # name = ''
            # for tt in xrange(len(edge_array)):
            #     assert tt <= 100, 'There are too many types of the edge label'
            #     assert edge_array[tt] <= 1000, 'There are too many edges'
            #     name += '-%02d-%03d' % (tt + 1, edge_array[tt])
            # name += '+'
                
            for tt in xrange(len(label_array)):
                assert tt <= 100, 'There are too many types of the node label'
                assert label_array[tt] <= 1000, 'There are too many nodes'
                name += '-%02d-%03d' % (tt + 1, label_array[tt])
                
            print name
            
            # print name
            # init new key in map
            if not subgraph_groups.has_key(name):
                subgraph_groups[name] = []
                for tt in xrange(len(subgraphs)):
                    subgraph_groups[name].append([])
                # subgraph_groups[name] = list(data_list)
                
            # add nodes to map
            subgraph_groups[name][ii].append(mynodes)
        
    
    # print subgraph_groups        
    return subgraph_groups


def subgraphs_disband(As, Vs, subgraph_groups):
    # data to return
    subgraphs = []
    
    # init data
    for V in Vs:
        subgraphs.append([])
    
    for key in subgraph_groups.keys():
        for ii in xrange(len(subgraph_groups[key])):
            subgraphs[ii].extend(subgraph_groups[key][ii])
        
    # return
    return subgraphs


def filter_groups_by_subgraph_label_name(subgraph_groups, support_num):
    # data to return
    subgraph_groups = dict(subgraph_groups)
    
    for key in subgraph_groups.keys():
        count = 0
        for graph in subgraph_groups[key]:
            # whether this graph has subgraph in this group
            if len(graph) > 0:
                count += 1
        # delete this group if the frequency is less support number
        if count < support_num:
            del subgraph_groups[key]
    
    # return 
    return subgraph_groups


def calculate_mark_set(As, Vs, subgraph_groups, ite_num=3):
    # data to return 
    subgraph_labels = {}
    subgraph_marksets = {}
    
    for key in subgraph_groups.keys():
        subgraph_group = subgraph_groups[key]
        subgraph_label = []
        subgraph_markset = []
        
        # init labels and mark set 
        for ii in xrange(len(subgraph_group)):
            subgraph_label.append([])
            subgraph_markset.append([])
            for jj in xrange(len(subgraph_group[ii])):
                subgraph_label[ii].append(Vs[ii][subgraph_group[ii][jj]["nodes"]])
                subgraph_markset[ii].append(set(subgraph_label[ii][jj]))
                
        # iteratively refresh labels
        for ite in xrange(ite_num):
            mymap = {}
            mymap_index = 1
            
            # injective map
            for ii in xrange(len(subgraph_group)):
                for jj in xrange(len(subgraph_group[ii])):
                    # get subgraph adjacent matrix
                    mynodes = subgraph_group[ii][jj]
                    nodes = mynodes["nodes"] # nodes list
                    edges = mynodes["edges"] # edges matrix
                    A = As[ii][nodes][:, nodes] & edges
                    
                    # refresh subgraph label
                    new_nodes = []
                    for kk in xrange(len(subgraph_label[ii][jj])):
                        # get connected node labels
                        connected_labels_1 = subgraph_label[ii][jj][A[kk, :] == 1]
                        connected_labels_2 = subgraph_label[ii][jj][A[:, kk] == 1]
                        # injective map
                        name = ''
                        for lb in connected_labels_1:
                            name += '%d_' % lb
                        name += '+'
                        for lb in connected_labels_2:
                            name += '%d_' % lb
                        
                        # add to new node list
                        new_nodes.append(name)
                        
                        # add to map
                        if not mymap.has_key(name):
                            mymap[name] = mymap_index
                            mymap_index += 1  
                        
                    subgraph_label[ii][jj] = new_nodes
                    
            # map compress
            for ii in xrange(len(subgraph_group)):
                for jj in xrange(len(subgraph_group[ii])):
                    for kk in xrange(len(subgraph_label[ii][jj])):
                        subgraph_label[ii][jj][kk] = mymap[subgraph_label[ii][jj][kk]]
                        
                    # to numpy
                    subgraph_label[ii][jj] = np.array(subgraph_label[ii][jj])
            
        # refresh mark set
        for ii in xrange(len(subgraph_group)):
            for jj in xrange(len(subgraph_group[ii])):
                subgraph_markset[ii][jj] = set(subgraph_label[ii][jj])
                   
        # add to dict
        subgraph_labels[key] = subgraph_label
        subgraph_marksets[key] = subgraph_markset
    
    # return
    return subgraph_marksets


def select_frequent_sugraphs(As, Vs, subgraph_groups, subgraph_marksets, support_num):
    # data to return
    frequent_As = []
    frequent_Vs = []
    frequent_fs = []
    
    for key in subgraph_groups.keys():
        subgraph_group = subgraph_groups[key]
        # count list
        list_markset = []
        list_count = []
        list_poistion = []
        for ii in xrange(len(subgraph_group)):
            for jj in xrange(len(subgraph_group[ii])):
                markset = subgraph_marksets[key][ii][jj]
                # count how many time the mark set appeared
                if markset not in list_markset:
                    # init count list
                    list_markset.append(markset)
                    list_count.append(1)
                    list_poistion.append([{'key': key, 'ii': ii, 'jj': jj}])
                else:
                    list_poistion[list_markset.index(markset)].append({'key': key, 'ii': ii, 'jj': jj})
                    # whether is the repeated data in the same graph
                    if markset not in subgraph_marksets[key][ii][0: jj]:
                        list_count[list_markset.index(markset)] += 1
        
        # [Acceleration] the new subgraph list only contains frequent subgraphs
        subgraph_group_new = []
        for ii in xrange(len(subgraph_group)):
            subgraph_group_new.append([])
        
        # select frequent subgraph
        for tt in xrange(len(list_count)):
            if list_count[tt] >= support_num:
                # position information
                pos = list_poistion[tt][0]
                mynodes = subgraph_group[pos['ii']][pos['jj']]
                nodes = mynodes["nodes"] # nodes list
                edges = mynodes["edges"] # edges matrix
                
                # graph information
                frequent_fs.append(list_count[tt])
                frequent_Vs.append(Vs[pos['ii']][nodes])
                frequent_As.append(As[pos['ii']][nodes][:, nodes] & edges)
                
                # [Acceleration] add to new subgraph list
                for pos in list_poistion[tt]:
                    nodes = subgraph_group[pos['ii']][pos['jj']]
                    subgraph_group_new[pos['ii']].append(nodes)
        
        # [Acceleration] refresh subgraph group
        subgraph_groups[key] = subgraph_group_new
    
    # return 
    return frequent_As, frequent_Vs, frequent_fs, subgraph_groups


def result_save_show(frequent_As, frequent_Vs, frequent_fs):
    # save results
    pickle.dump(frequent_As, open('saves/results/frequent_As.pkl', 'w'))
    pickle.dump(frequent_Vs, open('saves/results/frequent_Vs.pkl', 'w'))
    pickle.dump(frequent_fs, open('saves/results/frequent_fs.pkl', 'w'))
    
    # print result
    print '\n=================== Result ===================\n'
    # print 'Find %d frequent subgraphs.\n' % len(frequent_fs)
    for tt in xrange(len(frequent_fs)):
        print 'Subgraph', tt + 1, '. Frequency is', frequent_fs[tt]
        print 'Vertex labels:'
        print frequent_Vs[tt]
        print 'Adjacent matrix:'
        print frequent_As[tt]
        print ''


def cut_infrequent_subgraphs(As, tt, subgraphs):
    # [Acceleration] cut unfrequent vertex
    if tt == 1:
        for ii in xrange(len(As)):
            vertices = [x[0] for x in subgraphs[ii]]
            A_t = np.zeros(As[ii].shape)
            A_t[vertices, :] = As[ii][vertices, :]
            A_t[:, vertices] = As[ii][:, vertices]
            As[ii] = A_t
                
    # [Acceleration] cut unfrequent edges
    elif tt == 2:
        for ii in xrange(len(As)):
            A_t = np.zeros(As[ii].shape)
            for nodes in subgraphs[ii]:
                A_t[nodes[0], nodes[1]] = As[ii][nodes[0], nodes[1]]
                A_t[nodes[1], nodes[0]] = As[ii][nodes[1], nodes[0]]
            As[ii] = A_t
    
    # return 
    return As


if __name__ == '__main__':
    # parser
    FLAGS, unparsed = parser.parse_known_args()
    
    # input data
    As, Vs = load_datas()
    
    # inferred data
    support_num = len(As) * FLAGS.min_support
    max_size = FLAGS.max_size
    if max_size <= 0:
        max_size = get_min_graph_size(As, Vs)
    
    # print start info
    print '\nSearch for the frequent subgraph. Minimum support is %d. Maximum subgraph size is %d. \n' % (support_num, max_size)
    
    start = time()
    
    subgraphs = []
    frequent_As = []
    frequent_Vs = []
    frequent_fs = []
    for tt in xrange(max_size):
        # [Acceleration] cut infrequent vertices and edges
        # As = cut_infrequent_subgraphs(As, tt, subgraphs)
        
        # get different subgraphs with different size
        print 'Generate', tt + 1, 'size subgraphs ...'
        subgraphs = generate_bigger_subgraph(As, Vs, subgraphs)
        print 'Generate', tt + 1, 'size subgraphs complete.\n'
        
        # get different subgraphs with different size
        # print 'Generate subgraphs ...'
        # subgraphs_list = generate_subgraphs(As, Vs, max_size)
        # print 'Generate subgraphs complete.\n'
            
        # group subgraphs by node labels  
        print 'Group subgraphs by subgraph label name ...'
        subgraph_groups = subgraphs_group(As, Vs, subgraphs)
        # print subgraph_groups
        print 'Group subgraphs by subgraph label name complete.\n'
        
        # [Acceleration] filter by subgraph label name
        print 'Filter subgraph groups by subgraph label name ...'
        subgraph_groups = filter_groups_by_subgraph_label_name(subgraph_groups, support_num)
        print 'Filter subgraph groups by subgraph label name complete.\n'
            
        # calculate the mark set by WL principle
        print 'Calculate the mark set ...'
        subgraph_marksets = calculate_mark_set(As, Vs, subgraph_groups)
        print 'Calculate the mark set Complete.\n'
            
        # select frequent subgraphs
        print 'Select frequent subgraphs ...'
        result_As, result_Vs, result_fs, subgraph_groups = select_frequent_sugraphs(As, Vs, subgraph_groups, subgraph_marksets, support_num)
        frequent_As.extend(result_As)
        frequent_Vs.extend(result_Vs)
        frequent_fs.extend(result_fs)
        print 'Select frequent subgraphs complete.\n'
            
        # [Acceleration] disband subgraphs for next iteration
        print 'Disband subgraphs by subgraph label name ...'
        subgraphs = subgraphs_disband(As, Vs, subgraph_groups)
        print 'Disband subgraphs by subgraph label name complete.\n'
        
        # [Acceleration] If no frequent subgraphs are found, stop.
        if len(result_As) <= 0:
            break;
    
    end = time()
    
    # save and show results
    result_save_show(frequent_As, frequent_Vs, frequent_fs)
    
    print "\nRunning time:", end - start
                    