# -*- coding: utf-8 -*-

import numpy as np
import pickle
# import MySQLdb


def generate_next_subgraph(As, Vs, subgraphs_1):
    # data to return
    subgraphs_k = []
    
    # init or calculate
    if subgraphs_1 == []:
        # generate 1 size subgraphs
        for ii in xrange(len(As)):
            A = As[ii]
            V = Vs[ii]
            subgraphs_k.append([[x] for x in xrange(len(V))])
    else: 
        # generate k+1 size subgraphs
        for ii in xrange(len(As)):# xrange(len(As)):
            A = As[ii]
            # V = Vs[ii]
            subgraph_1 = subgraphs_1[ii]
            subgraph_k = []
            for nodes in subgraph_1:
                # the connected nodes
                connected_yesno = A[nodes].any(axis=0)
                connected_indexes = np.argwhere(connected_yesno != 0).reshape(-1)
                for index in connected_indexes:
                    # create node set
                    if index not in nodes:
                        nodes_k = list(nodes)
                        # insert and sort ssubgraph_k
                        for pp in xrange(len(nodes_k) + 1):
                            if pp == len(nodes_k):
                                nodes_k.append(index)
                            elif nodes_k[pp] > index:
                                nodes_k.insert(pp, index)
                                break;
                        # add new node set
                        if nodes_k not in subgraph_k:
                            subgraph_k.append(nodes_k)
            
            # add to data list
            subgraphs_k.append(subgraph_k)
        
    # return
    return subgraphs_k


def group_by_labels(As, Vs, subgraphs): 
    # data to return
    subgraph_groups = {}
    
    for ii in xrange(len(subgraphs)):
        subgraph = subgraphs[ii]
        V = Vs[ii]
        for nodes in subgraph:
            # count label number
            label_array = []
            for label in V[nodes]:
                # add array items
                for tt in xrange(label - len(label_array)):
                    label_array.append(0)
                # counting
                label_array[label - 1] += 1
            
            # generate subgraph label name
            name = ''
            for tt in xrange(len(label_array)):
                assert tt <= 100, 'There are too many types of the node label'
                assert label_array[tt] <= 1000, 'There are too many nodes'
                name += '%02d%03d' % (tt + 1, label_array[tt])
            
            # init new key in map
            if not subgraph_groups.has_key(name):
                subgraph_groups[name] = []
                for tt in xrange(len(subgraphs)):
                    subgraph_groups[name].append([])
                    
            # add nodes to map
            subgraph_groups[name][ii].append(nodes)
            
    return subgraph_groups


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


def calculate_mark_set(As, Vs, subgraph_groups, ite_num=4):
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
                subgraph_label[ii].append(Vs[ii][subgraph_group[ii][jj]])
                subgraph_markset[ii].append(set(subgraph_label[ii][jj]))
                
        # iteratively refresh labels
        for ite in xrange(ite_num):
            mymap = {}
            mymap_index = 1
            
            # injective map
            for ii in xrange(len(subgraph_group)):
                for jj in xrange(len(subgraph_group[ii])):
                    # get subgraph adjacent matrix
                    nodes = subgraph_group[ii][jj]
                    A = As[ii][nodes][:, nodes]
                    
                    # refresh subgraph label
                    new_nodes = []
                    for kk in xrange(len(subgraph_label[ii][jj])):
                        # get connected node labels
                        connected_labels_1 = subgraph_label[ii][jj][A[kk] == 1]
                        connected_labels_2 = subgraph_label[ii][jj][A[kk] == -1]
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
                # whether is the repeated data in the same graph
                if markset in subgraph_marksets[key][ii][0: jj]:
                    continue
                
                # count how many time the mark set appeared
                if markset not in list_markset:
                    # init count list
                    list_markset.append(markset)
                    list_count.append(1)
                    list_poistion.append({'key': key, 'ii': ii, 'jj': jj})
                else:
                    list_count[list_markset.index(markset)] += 1
                    
        # select frequent subgraph
        for tt in xrange(len(list_count)):
            if list_count[tt] >= support_num:
                # position information
                pos = list_poistion[tt]
                nodes = subgraph_group[pos['ii']][pos['jj']]
                # graph information
                frequent_fs.append(list_count[tt])
                frequent_Vs.append(Vs[pos['ii']][nodes])
                frequent_As.append(As[pos['ii']][nodes][:, nodes])
    
    # return 
    return frequent_As, frequent_Vs, frequent_fs 


if __name__ == '__main__':
    # input data
    Support_Num = 3
    Subgraph_Size = 3
    
    As = [np.array([[0, 0, 1, 0, 0, 0, 0], 
                    [0, 0, 1, 0, 0, 0, 0],
                    [-1, -1, 0, 1, 0, 0, 0],
                    [0, 0, -1, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1, 0],
                    [0, 0, 0, -1, -1, 0, 1],
                    [0, 0, 0, 0, 0, -1, 0]]),
    
          np.array([[0, 0, 1, 0, 0, 0, 0], 
                    [0, 0, 1, 0, 0, 0, 0],
                    [-1, -1, 0, 1, 0, 0, 0],
                    [0, 0, -1, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1, 0],
                    [0, 0, 0, -1, -1, 0, 1],
                    [0, 0, 0, 0, 0, -1, 0]]),
    
          np.array([[0, 0, 0, 1, 0, 0, 0], 
                    [0, 0, 0, 1, 1, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0],
                    [-1, -1, 0, 0, 0, 1, 0],
                    [0, -1, -1, 0, 0, 0, 1],
                    [0, 0, 0, -1, 0, 0, 0],
                    [0, 0, 0, 0, -1, 0, 0]])]
    
    Vs = [np.array([1, 1, 2, 1, 1, 4, 1]), 
          np.array([1, 1, 4, 1, 1, 3, 1]),
          np.array([1, 1, 1, 2, 4, 1, 1])]
    
    # get different subgraphs with different size
    subgraphs = []
    subgraphs_list = []
    for ii in xrange(5):
        print 'Generate', ii, 'size subgraphs ...'
        subgraphs = generate_next_subgraph(As, Vs, subgraphs)
        subgraphs_list.append(subgraphs)
    
    print 'Generate subgraphs complete.\n'
        
    # devide subgraphs by node labels  
    print 'Group subgraphs by subgraph label name ...'
    subgraph_groups = group_by_labels(As, Vs, subgraphs_list[Subgraph_Size - 1])
    print 'Group subgraphs by subgraph label name complete.\n'
    
    # filter by subgraph label name
    print 'Filter subgraph groups by subgraph label name ...'
    subgraph_groups = filter_groups_by_subgraph_label_name(subgraph_groups, Support_Num)
    print 'Filter subgraph groups by subgraph label name complete.\n'
        
    # calculate the mark set by WL principle
    print 'Calculate the mark set ...'
    subgraph_marksets = calculate_mark_set(As, Vs, subgraph_groups)
    print 'Calculate the mark set Complete.\n'
        
    # select frequent subgraphs
    print 'Select frequent subgraphs ...'
    frequent_As, frequent_Vs, frequent_fs = select_frequent_sugraphs(As, Vs, subgraph_groups, subgraph_marksets, Support_Num)
    print 'Select frequent subgraphs complete.\n'
    
    # save results
    pickle.dump(frequent_As, open('saves/results/frequent_As.pkl', 'w'))
    pickle.dump(frequent_Vs, open('saves/results/frequent_Vs.pkl', 'w'))
    pickle.dump(frequent_fs, open('saves/results/frequent_fs.pkl', 'w'))
    
    # print result
    print '\n=================== Result ===================\n'
    for tt in xrange(len(frequent_fs)):
        print 'Subgraph', tt + 1, '. Frequency is', frequent_fs[tt]
        print 'Vertex labels:'
        print frequent_Vs[tt]
        print 'Adjacent matrix:'
        print frequent_As[tt]
        print ''
                
                    