#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 15:36:55 2020

@author: MELLET
"""
import FuzzyMeusure as fm

def first_test(criteria, importanceValues):
    lattice, squaredErrors = fm.modeling(criteria, importanceValues)
    fm.interaction_index(lattice)
    fm.shapley_index(lattice, criteria) #dictionary
    print("fuzzy measure")
    for key in lattice.get_criterias().keys():
        print(lattice.get_criteria(key), ": ", lattice.get_coeff_value(key))

def test_k_fold(criteria, importanceValues):
    dataSet = list()
    delta = int(len(importanceValues)/3)
    dataSet.append(list(importanceValues[:delta]))
    dataSet.append(list(importanceValues[delta:delta*2]))
    dataSet.append(list(importanceValues[delta*2:]))
    
    listLattice = list()
    listShapleyIndex = list()
    listInteractionIndex = list()
    listMatrixConfusion = list()
    listSquaredErrors = list()
    
    for i in range(3):
        #print("ITERATION: ", i)
        trainingSet = dataSet[(i+1)%3] + dataSet[(i+2)%3]
        lattice, squaredErrors = fm.modeling(criteria, trainingSet)
        listLattice.append(lattice)
        listSquaredErrors.append(squaredErrors)
        
        shapleyIndex = fm.shapley_index(lattice, criteria) #dictionary
        listShapleyIndex.append(shapleyIndex)
                
        testSet = dataSet[i]
        classes = fm.classification(lattice, testSet)
        
        matrixConfusion = fm.matrix_confusion(testSet, classes)
        listMatrixConfusion.append(matrixConfusion)
        
        interactionIndex = fm.interaction_index(lattice) #dictionary
        listInteractionIndex.append(interactionIndex)
    
    print("K fold cross validation: ")

    print("Faux positive average: ", int(sum(list(x[1] for x in listMatrixConfusion))/3), \
          ", Faux negative average: ", int(sum(list(x[2] for x in listMatrixConfusion))/3), \
          ", Vrai positive average: ", int(sum(list(x[0] for x in listMatrixConfusion))/3), \
          ", Vrai negative average: ", int(sum(list(x[3] for x in listMatrixConfusion))/3))
    
    print("shapleyIndex average: ")
    acc = 0
    n = len(criteria)-1
    for key in listShapleyIndex[0].keys():
        v = sum(list(x[key] for x in listShapleyIndex))*n/3
        acc += v
        print(listLattice[0].get_criteria(key), " : ", v)
    print("sum shapley index: ", acc)
    
    print("interactionIndex average: ")
    for key in sorted(listInteractionIndex[0].keys()):
        print(listLattice[0].get_criteria(key[0]), listLattice[0].get_criteria(key[1]),\
              " : ", sum(list(x[key] for x in listInteractionIndex))/3)
    
    print("squared mean errors: ", sum(listSquaredErrors)/3)
    
    print("les poids moyens de 3 treille")
    for key in listLattice[0].get_criterias().keys():
        print(listLattice[0].get_criteria(key), ": ", sum(list(latt.get_coeff_value(key) for latt in listLattice))/3)
    

if __name__ == "__main__":
    #path = "LearningData/EvalEntreprise.txt"
    #path = "LearningData/Fromage.txt"
    #criteria, importanceValues = fm.read_LD(path)
    #first_test(criteria, importanceValues)

    path = "LearningData/LearningBreastCancer.txt"
    criteria, importanceValues = fm.read_LD(path)
    test_k_fold(criteria, importanceValues)

