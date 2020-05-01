#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 13:17:40 2020

@author: MELLET

installation under ubuntu python3
sudo apt install python3-pip
pip3 install pydot graphviz

under Win10 with anaconda
conda install graphviz
conda install python-graphviz

"""
from DirectedGraph import *
#from graphviz import Digraph #uncomment in need of visualizing

DESCRIPTORS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'] #9 descriptors maximum

class Lattice(object):

    def __init__(self, criteria):
        """ initialize a lattice to the equilibrium state. """
        self.__graph = DirectedGraph()
        self.__weights = dict() #coeff
        self.__descriptors = dict() #{'a' : 'Gout'}
        self.__importanceValue = dict()
        self.__visited = dict()
        for i in range(len(criteria)-1): self.__descriptors[DESCRIPTORS[i]] = criteria[i]
        self.__contribute()
        self.__equilibrate()

    def __contribute(self):
        """ construct a directed graph with combinaison les descriptors,
        and initialize with all coefficients non visited. """
        descriptors = sorted(self.__descriptors.keys())
        end = len(descriptors)
        empty = '.'
        for x in descriptors: self.__graph.add_edge(empty, x) #layer0 & 1
        
        iteration = 1
        while iteration <= end:
            iteration += 1
            concat = set()
            for i in range(len(descriptors)-1):
                for j in range(i+1, len(descriptors)):
                    new_vertex = ''.join(sorted(set(descriptors[i] + descriptors[j])))
                    if len(new_vertex) == iteration : 
                        concat.add(new_vertex)
                        self.__graph.add_edge(descriptors[i], new_vertex)
                        self.__graph.add_edge(descriptors[j], new_vertex)
            descriptors = list(concat)
        
        for x in self.__graph.vertices(): self.__visited[x] = False

    def __equilibrate(self):
        """ status equilibrium  """
        for i in self.__graph.vertices(): self.__weights[i] = len(i)/len(self.__descriptors)
        self.__weights['.'] = 0

    def set_coeff_value(self, v, value):
        """ modify the v coefficient's value and be touched. """
        self.__weights[v] = value
        self.__visited[v] = True

    def get_coeff_value(self, v):
        """ return coefficient's value"""
        return self.__weights[v]

    def set_importanceValue(self, data):
        """ associate every criterion with its importance value. (can be modified when data change) """
        for i in range(len(data)-1): self.__importanceValue[DESCRIPTORS[i]] = data[i]

    def permute_importanceValue(self):
        """ return a pair of list ordered with importance value. """
        return list(x for x in sorted(list(self.__importanceValue.items()), key = lambda x: x[1]))

    def deduce_path(self):
        """ return a path deduced by the importance values"""
        path = ['.']
        for x in reversed(list((x[0] for x in self.permute_importanceValue()))):
            if path[-1] == '.': path.append(x)
            else:
                path.append(''.join(sorted(path[-1]+x)))
        return path

    def has_visited(self, v):
        """ return whether the vertex / coefficient v has been visited. """
        return self.__visited[v]

    def lower_neighbors_values(self, v):
        """ return a list of value of its lower neighbors. """
        return list(map(lambda x: self.get_coeff_value(x), self.__graph.lower_neighbors(v)))

    def upper_neighbors_values(self, v):
        """ return a list of value of its upper neighbors. """
        return list(map(lambda x: self.get_coeff_value(x), self.__graph.upper_neighbors(v)))

    def get_coefficients_non_modified(self):
        """ return all coefficients non modified. """
        return list(filter(lambda x: not self.has_visited(x), self.__graph.vertices()))

    def get_coefficients(self):
        """ return all coefficients. """
        return self.__graph.vertices()

    def get_coeffs_without(self, i):
        """ return all coefficients that dosen't contain element i. """
        return sorted(list(filter(lambda x: i not in x, self.__graph.vertices())))
    
    def get_criteria(self, i):
        """ return the real criteria's name in the context. """
        return self.__descriptors[i]
    
    def get_criterias(self):
        """ return all criteria with pair of (supdo , real name in context). """
        return self.__descriptors
    
    # uncomment in need of visualizing
    """
    def visualize(self):
        dot = Digraph()
        for u in self.__graph.vertices():
            for v in self.__graph.upper_neighbors(u):
                dot.edge(u, v)
        dot.render('test.gv', view = True)
     """
