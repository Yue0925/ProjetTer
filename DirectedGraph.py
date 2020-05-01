#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Implementation of a directed graph using a dictionary: the keys
are the vertices, and the values are the vertices adjacent to a given vertex.
Loops and weights are not allowed.

We use the simplest representation: an edge (u, v) will be present
once in the dictionary: v is in the set of childs of u, and u
is in the set of parents of v.

"""

class DirectedGraph(object):
    def __init__(self):
        """Initialize a graph without edges"""
        self.__dictionary = dict()
    
    def add_edge(self, u, v):
        """Add an edge from the vertices u to v, creating the vertices
        missing if applicable. """
        if u not in self.__dictionary:
             self.__dictionary[u] = set()
        if v not in self.__dictionary:
            self.__dictionary[v] = set()
        self.__dictionary[u].add(v)
        
    def add_edges(self, iterable):
        """Add all edges of the given iterable to the graph.
        whatever types of itrable are acceptable, but it should not contain
        only pairs of elements (regardless of the type of couple). """
        for u, v in iterable:
            self.add_edge(u, v)
            
    def add_vertex(self, u):
        """Add a vertex (whatever types) to the graph."""
        self.__dictionary[u] = set()
    
    def add_vertices(self, iterable):
        """Add all vertices of the given iterable to the graph.
        whatever types of itrable are acceptable."""
        for u in iterable:
            self.add_vertex(u)
    
    def edges(self):
        """Return all the edges of the graph. An edge is represented
        by a tuple (a, b) with a -> b."""
        return { tuple(u, v) for u in self.__dictionary for v in self.__dictionary[u]}
    
    def contain_vertex(self, u):
        """Return True if the vertex u exists, False otherwise."""
        return u in self.__dictionary
        
    def contain_adge(self, u, v):
        """Return True if the edge u -> v exists, False otherwise."""
        if self.contain_vertex(u) and self.contain_vertex(v):
            return v in self.__dictionary[u]
        return False

    def upper_neighbors(self, u): #layer+1 -> children
        """Return all the vertices v s.t. v -> u."""
        return self.__dictionary[u]

    def lower_neighbors(self, u): #layer-1 -> parents
        """Return all the vertices v s.t. u -> v."""
        return (v for v in self.__dictionary if u in self.__dictionary[v] )
    
    def degree_incoming(self, u): 
        """Return the number of parents of the vertex; if it does not exist, causes
         a mistake."""
        return len(self.lower_neighbors(u))
    
    def degre_outgoing(self, u):
        """Return the number of children of the vertex; if it does not exist, causes
         a mistake."""
        return len(self.upper_neighbors(u))
    
    def num_vertices(self):
        """Return the number of vertices in the graph."""
        return len(self.__dictionary)
    
    def remove_edge(self, u, v):
        """Remove edge u -> v if it exists; otherwise it will cause an error."""
        self.__dictionary[u].remove(v)
        
    def remove_edges(self, iterable):
        """Remove all edges of the given iterator from the graph.
        whatever types of itrable are acceptable, but it should not contain
        only pairs of elements (regardless of the type of couple). """
        for u, v in iterable:
            self.remove_edge(u, v)
        
    def remove_vertex(self, u):
        """Erase the vertex of the graph, and remove all the edges that
        are incidental. """
        del self.__dictionary[u]
        for v in self.__dictionary:
            self.__dictionary[v].discard(u)
    
    def remove_vertices(self, iterable):
        """Erase the vertices of the given iterable from the graph, and remove all
        the edges incident at these vertices. """
        for u in iterable:
            self.remove_vertex(u)
    
    def vertices(self):
        """Returns all the vertices of the graph."""
        return set(self.__dictionary.keys())

    
    
            