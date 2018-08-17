# -*- coding: utf-8 -*-
import numpy as np
from time import time
import cmath

def func_g_1(lamda, s=1):
    return np.exp(-lamda / s)


def func_g_2(lamda, s=1):
    if(lamda == s):
        return 1
    else:
        return 0
    
def func_g_3(lamda, s=[]):
    if(lamda in s):
        return 1
    else:
        return 0
    
def func_g_4(lamda, center, width=0.5):
    if lamda > center + width or lamda < center - width:
        return 0
    else:
        return 1
    

def spectrum_indicators(vals, freqs_list):
    # data to return
    embeddings = []
    
    # different powder
    vals_1 = vals
    vals_2 = vals_1 * vals
    vals_3 = vals_2 * vals
    
    # use moments as indicators
    for ii in xrange(len(freqs_list)):
#        print freqs_list[ii]
        m1 = freqs_list[ii].T.dot(vals_1) # (vals_1 * freqs_list[ii]).sum(axis=0)
            
        m2 = freqs_list[ii].T.dot(vals_2) # (vals_2 * freqs_list[ii]).sum(axis=0)
        for tt in xrange(len(m2)):
            if m2[tt] > 0:
                m2[tt] = m2[tt] ** (1.0 / 2)
            else:
                m2[tt] = -((-m2[tt]) ** (1.0 / 2))
            
        m3 = freqs_list[ii].T.dot(vals_3) # (vals_3 * freqs_list[ii]).sum(axis=0)
        for tt in xrange(len(m3)):
            if m3[tt] > 0:
                m3[tt] = m3[tt] ** (1.0 / 3)
            else:
                m3[tt] = -((-m3[tt]) ** (1.0 / 3))
        
#        if m3 > 0:
#            m3 = m3 ** (1.0 / 3)
#        else:
#            m3 = -((-m3) ** (1.0 / 3))
        
        # add result to list
        embeddings.append(np.array([m1, m2, m3], dtype=float).reshape(-1))
        
    # return 
    return embeddings
    
    
#def wavelet_spectrum(A, V):
#    global RcdTime
#    global RcdIndex
#    
#    # calculate Laplacian
#    # A = A + A.T
#    D = np.diag(A.sum(axis=0))
#    L = D - A
#    
#    # eigen values and vectors
#    start = time()
#    eig_vals, eig_vecs = np.linalg.eig(L)
#    RcdTime[RcdIndex][2] = time() - start
#    
#    # wavelet
#    mys_list = eig_vals.copy()
#    mys_list.sort()
#    mys_list = mys_list[mys_list > 1]
#    Tf_list = []
#    RcdTime[RcdIndex][3] = 0
#    RcdTime[RcdIndex][4] = 0
#    RcdTime[RcdIndex][5] = 0
#    for ii in xrange(len(mys_list)):
#        '''
#        # calculate kernel
#        start = time()
#        g_lamda = np.diag([func_g_2(x, s=mys_list[ii]) for x in eig_vals])
#        RcdTime[RcdIndex][3] += time() - start
#        
#        
#        # calculate wavelet operator
#        start = time()
#        T = eig_vecs.dot(g_lamda)
#        RcdTime[RcdIndex][4] += time() - start
#        
#        
#        start = time()
#        T = T.dot(eig_vecs.T)
#        RcdTime[RcdIndex][5] += time() - start
#        '''
#        
#        # calculate wavelet operator
#        start = time()
#        for tt in xrange(len(eig_vals)):
#            if eig_vals[tt] == mys_list[ii]:
#                T = eig_vecs[:, tt: tt + 1].dot(eig_vecs[:, tt: tt + 1].T)
#                break
#        RcdTime[RcdIndex][3] += time() - start
#        
#        # calculate wavelet
#        start = time()
#        Tf = T.dot(V)
#        Tf_list.append(Tf)
#        RcdTime[RcdIndex][4] += time() - start
#    
#    # data to return
#    Tfs = np.array(Tf_list).T
#    Lamdas = mys_list
#            
#    # return 
#    return Lamdas, Tfs


def wavelet_spectrum_fast(A, V, is_directed=False):
    global RcdTime
    global RcdIndex
    
    global Alpha, Lamdas, Cheb_Cs, Cheb_M, Lamda_Min, Is_Directed
    
    # calculate Laplacian
    if Is_Directed:
        H = A - A.T
        L = -H.dot(H)
    else:
        D = np.diag(A.sum(axis=0))
        L = D - A
    
#    eig_vals, eig_vecs = np.linalg.eig(L)
#    print L
#    print eig_vals
#    print eig_vecs
    
#    eig_vals, eig_vecs = np.linalg.eig(L)
#    print L
#    print eig_vals
#    print eig_vecs
    
    # range of the frequency
    Tfs = []
    
    # for every lamda
    for lamda in Lamdas:
        # Chebyshev polynomials
        Ts = [V, L.dot(V)]
        
        # some values to use
        val1 = (2.0 / Alpha) * (L - (Alpha + Lamda_Min) * np.eye(len(V)))
        
        # Chebyshev recurrence
        for ii in xrange(2, Cheb_M + 1):
            T =  val1.dot(Ts[ii - 1]) - Ts[ii - 2]
            Ts.append(T)
            
        # combine polynomials
        Tf = Ts[0] / 2.0 * Cheb_Cs[lamda][0]
        for ii in xrange(1, len(Ts)):
            Tf += Ts[ii] * Cheb_Cs[lamda][ii]
        Tfs.append(Tf)
        
    Tfs = np.array(Tfs)
    Tfs = np.transpose(Tfs, (1, 0, 2))
#    print Tfs
            
    # return 
    return Lamdas, Tfs
    

RcdTime = []
RcdIndex = []

def cal_embedding(As, Vs):
    """
    The main calling function.
    """
    global RcdTime, RcdIndex
    global Lamda_Min
    RcdTime = []
    
    # data to return
    embeddings = []
    
    for ii in xrange(len(As)):
        RcdTime.append(np.zeros(10, dtype=float))
        RcdIndex = ii
        
        print "Calculating graph number", ii, "..."
        
        # calculate walvet spectrum
        start = time()
        Lamdas, Tfs = wavelet_spectrum_fast(As[ii], Vs[ii])
        RcdTime[RcdIndex][0] = time() - start
        
        # calculate indicators as embedding
        start = time()
        embeddings.extend(spectrum_indicators(Lamdas, Tfs))
        RcdTime[RcdIndex][1] = time() - start
        
    embeddings = np.array(embeddings)
        
    # save some result
    np.savetxt("saves/TimeRcds.csv", np.array(RcdTime), delimiter=',', 
               header="walvet spectrum, calculate indicators, WS - eigen decompose, WS - kernel and operator, WS - calculate Tf")
             
    # return
    return embeddings, Lamdas, Tfs


def cal_distances(embeddings):
    """
    Calculate the node distances by embeddings
    """
    # calculate
    dist = np.zeros([len(embeddings), len(embeddings)], dtype=float)
    for ii in xrange(len(embeddings)):
        for jj in xrange(ii + 1, len(embeddings)):
            dist[ii, jj] = np.linalg.norm(embeddings[ii] - embeddings[jj])
            dist[jj, ii] = dist[ii, jj] 
    
    # return
    return dist

# global variables
Lamda_Max = 10.0
Lamda_Min = 0.0
Alpha = 0.0
Lamdas = []
Cheb_Cs = {}
Cheb_M = 5
Is_Directed = False

def init(is_directed=False):
    global Lamda_Max, Lamda_Min, Is_Directed
    global Alpha, Lamdas, Cheb_Cs
    
    # init variables
    if is_directed:
        Lamda_Max = 10.0
        Lamda_Min = 0.0
    else:
        Lamda_Max = 10.0
        Lamda_Min = 0.0
        
    Is_Directed = is_directed
    
    # generate params
    Alpha = (Lamda_Max - Lamda_Min) / 2.0
    Lamdas = np.linspace(Lamda_Min, Lamda_Max, int(Lamda_Max - Lamda_Min + 1))
    
    # generate Chebyshev coefficients
    for lamda in Lamdas:
        xs = np.linspace(-1.0, 1.0, 21)
        ys = [func_g_4((x + 1) * Alpha + Lamda_Min, lamda) for x in xs]
        Cheb_Cs[lamda] = np.polynomial.chebyshev.chebfit(xs, ys, deg=5)
#    print Cheb_Cs
# init
# init(is_directed=False);