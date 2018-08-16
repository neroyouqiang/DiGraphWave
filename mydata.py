# -*- coding: utf-8 -*-
import os
import re
import numpy as np


def get_data_files():
    # data to return 
    files = []
    
    path = './data/'
    for myfile in os.listdir(path):
        file_path = os.path.join(path, myfile)
        files.append(file_path)
    
    # return
    return files
        

def load_A_V(file_name):
    data = np.loadtxt(file_name, delimiter=',', dtype=float)
    # node_num = file_name.shape[1]
    
    V = data[0, :]
    A = data[1::, :]
    
    return A, V


def load_datas():
    # data to return
    As = []
    Vs = []
    
    # get file name
    file_names = get_data_files()
    
    # for file_name in file_names:
    #     print re.match(".+\.csv$", file_name)
    
    # load data
    for file_name in file_names:
        if re.match(".+\.csv$", file_name):
            # print file_name
            A, V = load_A_V(file_name)
            if len(V) >= 1:
                As.append(A)
                Vs.append(V)
    
    # for tt in xrange(10):
    #     As.extend(list(As))
    #     Vs.extend(list(Vs))
    
    # return 
    return As, Vs


def get_min_graph_size(As, Vs):
    min_size = float('inf')
    for V in Vs:
        if min_size > len(V):
            min_size = len(V)
            
    return min_size
    

if __name__ == '__main__':
    pass