#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 12:44:43 2020

@author: MELLET
"""
from Lattice import *
import os
import math
import matplotlib.pyplot as plt

ITER = 1000

def read_LD(path):
    """ read a learning data file and a criteria list and data matrix. """
    if not os.path.exists(path): raise Exception("Can' find file", path)
    firstLine = 0
    criteria = list()
    importanceValues = list()
    
    with open(path, 'r') as file:
        for line in file.readlines():
            if firstLine == 0:
                firstLine += 1
            elif firstLine == 1: 
                criteria = line.split()[:]
                firstLine += 1
            else:
                importanceValues.append(list(map(lambda x: float(x), line.split())))
                firstLine += 1
              
    return criteria, importanceValues

def calculate_choquet_integral(lattice):
    """ calculate the value of choquet integral. """
    Fu = 0
    permutedIV = lattice.permute_importanceValue()
    A = list(x[0] for x in permutedIV)
    
    for i in range(len(permutedIV)):
        mu = lattice.get_coeff_value(''.join(sorted(A[i:])))
        if i == 0:
            Fu += (permutedIV[i][1]) * mu
        else:
            Fu += (permutedIV[i][1] - permutedIV[i-1][1]) * mu
    return Fu

def calculate_model_error(Fu, y):
    """ return the model error. """
    return Fu - y

def verify_monotonicity(e, v, lattice):
    if e > 0:
        muJ = max(lattice.lower_neighbors_values(v))
        if lattice.get_coeff_value(v) < muJ: lattice.set_coeff_value(v, muJ)
    else:
        muJ = min(lattice.upper_neighbors_values(v))
        if lattice.get_coeff_value(v) > muJ: lattice.set_coeff_value(v, muJ)        

def compute_new_value(alpha, path, lattice, e):
    """ compute the new value for u(i), that u(i) the coefficient's value appreared in path. """
    Fx = [0]
    permutedIV = lattice.permute_importanceValue()
    for x in permutedIV: Fx.append(x[1])
    n = len(Fx)
    
    if e > 0: 
        order = list(range(1, n-1))
    else: 
        order = list(range(n-2, 0, -1))

    for i in order:
        oldU = lattice.get_coeff_value(path[i])
        newU = oldU - alpha * e * (Fx[n-i] - Fx[n-i-1])
        lattice.set_coeff_value(path[i], newU)

        verify_monotonicity(e, path[i], lattice)


def compute_values(importanceValues, lattice, alpha):
    """ do the computation for one iteration. """
    integralValue = list()
    for data in importanceValues:
        lattice.set_importanceValue(data)

        path = lattice.deduce_path()
        Fu = calculate_choquet_integral(lattice)
        integralValue.append(Fu)

        e = calculate_model_error(Fu, data[-1])

        compute_new_value(alpha, path, lattice, e)

    return integralValue

def adjust_value(lattice, beta, n, coeffs):
    for x in coeffs: 
        if x == '.' or len(x) == n:
            continue
        
        # meanU = sum(lattice.upper_neighbors_values(x)) / len(lattice.upper_neighbors_values(x))
        meanU = 1 / (n - len(x)) * sum(lattice.upper_neighbors_values(x))
        
        # meanL = sum(lattice.lower_neighbors_values(x)) / len(lattice.lower_neighbors_values(x))
        meanL = 1 / len(x) * sum(lattice.lower_neighbors_values(x))
        
        delta = meanU + meanL - 2 * lattice.get_coeff_value(x)
        
        if delta > 0: #min distance with upper neighbors
            dmin = min(lattice.upper_neighbors_values(x)) - lattice.get_coeff_value(x)
        else: #min distance with lower neighbors
            dmin = lattice.get_coeff_value(x) - max(lattice.lower_neighbors_values(x))
        
        oldU = lattice.get_coeff_value(x)
        newU = oldU + beta * (delta * dmin / 2 * (meanU + meanL))
        lattice.set_coeff_value(x, newU)
        
def shapley_index(lattice, criteria):
    """ calculate the shapley index (e.g. importance index) for each rule. """
    shapleyIndex = dict()
    rules = sorted(list(filter(lambda x: len(x) == 1 and x != '.', lattice.get_coefficients())))
    n = len(rules)
    
    def Cnk(n, k):
        f = math.factorial
        return f(n) // f(k) // f(n-k)
    
    for i in rules:
        subsetT = lattice.get_coeffs_without(i)
        acc2 = 0
        
        for t in range(n):
            T = set(sorted(list(filter(lambda x: len(x) == t, subsetT))))
            T.discard('.')
            acc3 = 0
            
            if t == 0:
                acc3 = lattice.get_coeff_value(i) - lattice.get_coeff_value('.')
            
            for everyT in T:
                acc3 += lattice.get_coeff_value(''.join(sorted(everyT + i))) - lattice.get_coeff_value(everyT)
            
            acc2 += acc3 * (1 / Cnk(n-1, t))
        shapleyIndex[i] = 1/n * acc2

    print("shapleyIndex: ")
    n = len(criteria)-1
    for item in shapleyIndex.items():
        print(lattice.get_criteria(item[0]), " : ", item[1]*n)
    print("sum shapleyIndex: ", sum(list(item[1]*n for item in shapleyIndex.items())))
    return shapleyIndex
            
def learning_algorithm(importanceValues, lattice, criteria):
    beta = 0.15
    alpha = 0.15
    delta = 0.15 / ITER
    coeffs = list()
    squaredErrors = list()
    
    # repeat iteration
    for i in range(ITER):

        integralValue = compute_values(importanceValues, lattice, alpha) #etape1
        if len(coeffs) == 0:
            coeffs = sorted(lattice.get_coefficients_non_modified(), key = len)
        adjust_value(lattice, beta, len(criteria)-1, coeffs) #etape2
        alpha -= delta
        beta -= delta
        E = 0
        for j in range(len(importanceValues)):
            e = importanceValues[j][-1] - integralValue[j]
            E += e*e # carrée
        squaredErrors.append(E / (len(importanceValues)))

    return squaredErrors

def modeling(criteria, importanceValues):
    #---------------- initialization lattice & vars ---------------
    lattice = Lattice(criteria)
    #lattice.visualize() #uncomment in need of visualizings

    #---------------- run algo ---------------
    squaredErrors = learning_algorithm(importanceValues, lattice, criteria)
    
    #---------------- draw curve ---------------
    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    ax.plot(list(range(1, len(squaredErrors)+1)), squaredErrors)  # Plot some data on the axes.
    print("our total squared mean errors: ", squaredErrors[-1])
    
    return lattice, squaredErrors[-1]

def classification(lattice, testSamples):
    integralValue = list()
    for data in testSamples:
        lattice.set_importanceValue(data)

        Fu = calculate_choquet_integral(lattice)
        integralValue.append(Fu)
        
    return list(map(lambda x: 1 if x>0.5 else 0, integralValue))


def interaction_index(lattice):
    interactionIndex = dict()
    n = len(lattice.get_criterias())
    
    def Cnt(n, t):
        f = math.factorial
        return f(t)*f(n-t-2) / f(n - 1)
    
    for ij in list(filter(lambda x: len(x)==2, lattice.get_coefficients())):
        acc = 0
        for t in list(filter(lambda x: ij[0] not in x and ij[1] not in x, lattice.get_coefficients())):
            if t == ".":
                t = str()
                marginalIndex = lattice.get_coeff_value(''.join(sorted(t + ij[0] + ij[1]))) \
                    + lattice.get_coeff_value(''.join(sorted("."))) \
                    - lattice.get_coeff_value(''.join(sorted(t + ij[0]))) \
                    - lattice.get_coeff_value(''.join(sorted(t + ij[1])))
            else:
                marginalIndex = lattice.get_coeff_value(''.join(sorted(t + ij[0] + ij[1]))) \
                    + lattice.get_coeff_value(''.join(sorted(t))) \
                    - lattice.get_coeff_value(''.join(sorted(t + ij[0]))) \
                    - lattice.get_coeff_value(''.join(sorted(t + ij[1])))
            acc += Cnt(n, len(t)) * marginalIndex

        interactionIndex[ij] = acc

    print("interactionIndex: ")
    for item in interactionIndex.items():
        print(lattice.get_criteria(item[0][0]), lattice.get_criteria(item[0][1]), " : ", item[1])
    return interactionIndex

def matrix_confusion(testSamples, classes):
    #VP, FP, FN, VN
    matrixConfusion = [0]*4 
    
    for i in range(len(testSamples)):
        if int(classes[i]) == 1:
            if int(testSamples[i][-1]) == 1:
                matrixConfusion[0] += 1
            else:
                matrixConfusion[1] += 1
        else:
            if int(testSamples[i][-1]) == 1:
                matrixConfusion[2] += 1
            else:
                matrixConfusion[3] += 1         
    
    print("classification bien fait ", matrixConfusion[0]+matrixConfusion[3], " sur ", len(testSamples))
    print("Faux positive: ", matrixConfusion[1], ", Faux negative: ", matrixConfusion[2])
    return matrixConfusion
