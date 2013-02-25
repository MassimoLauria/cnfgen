#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

__docstring__ =\
"""Utilities to manage graph formats and graph files in order to build
formulas that are graph based.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

__all__ = ["supported_formats","readGraph","readDigraph","writeGraph"]

#################################################################
#          Graph Decoders (first is default)
#################################################################

_graphformats = {
    'dag':   ['kth','gml','dot'],
    'bipartite':   ['kth','gml','dot'],
    'digraph': ['kth','gml','dot'],
    'simple': ['kth','gml','dot']
    }

def supported_formats():
    return _graphformats



#################################################################
#          Import third party code
#################################################################

import sys

try:
    import networkx
    import networkx.algorithms
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",
          file=sys.stderr)
    exit(-1)

# remove dot format if graphviz is not installed
# we put it by default for documentation purpose
try:
    import pygraphviz
except ImportError:
    print("WARNING: Missing 'dot' library: no support for graph based formulas.",
          file=sys.stderr)
    for k in _graphformats.values():
        try:
            k.remove('dot')
        except ValueError:
            pass


#################################################################
#          Graph reader(s)
#################################################################

def readDigraph(file,format,force_dag=False,multi=False):
    """Read a directed graph from file

    Arguments:
    - `file`: file object
    - `format`: file format
    - `force_dag`: enforces whether graph must be acyclic
    - `multi`:     multiple edge allowed

    Return: a networkx.DiGraph / networkx.MultiDiGraph object.
    """
    if format not in _graphformats['digraph']:
        raise ValueError("Invalid format for directed graph")

    if multi:
        grtype=networkx.MultiDiGraph
    else:
        grtype=networkx.DiGraph

    if format=='dot':

        D=grtype(pygraphviz.AGraph(file.read()).edges())

    elif format=='gml':

        D=grtype(networkx.read_gml(file))

    elif format=='kth':

        D=grtype()
        D.name=''
        D.ordered_vertices=[]

        for l in file.readlines():

            # add the comment to the header
            if l[0]=='c':
                D.name+=l[2:]
                continue

            if ':' not in l:
                continue # vertex number spec (we ignore it)

            target,sources=l.split(':')
            target=target.strip()
            sources=sources.split()

            # Load all vertices in this line
            for vertex in [target]+sources:
                if vertex not in D:
                    D.add_node(vertex)
                    D.ordered_vertices.append(vertex)

            for s in sources:
                D.add_edge(s,target)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(format))

    if force_dag and not networkx.algorithms.is_directed_acyclic_graph(D):
        raise ValueError("Graph must be acyclic".format(format))

    return D


def readGraph(file,format,multi=False):
    """Read a graph from file

    Arguments:
    - `file`: file object
    - `format`: file format
    - `multi`: multiple edge allowed

    Return: a networkx.Graph / networkx.MultiGraph object.
    """
    if format not in _graphformats['simple']:
        raise ValueError("Invalid format for undirected graph")

    if multi:
        grtype=networkx.MultiGraph
    else:
        grtype=networkx.Graph

    if format=='dot':

        G=grtype(pygraphviz.AGraph(file.read()).edges())

    elif format=='gml':

        G=grtype(networkx.read_gml(file))

    elif format=='kth':

        G=grtype()
        G.name=''
        G.ordered_vertices=[]

        for l in file.readlines():

            # add the comment to the header
            if l[0]=='c':
                G.name+=l[2:]
                continue

            if ':' not in l:
                continue # vertex number spec

            target,sources=l.split(':')
            target=target.strip()
            sources=sources.split()

            # Load all vertices in this line
            for vertex in [target]+sources:
                if vertex not in G:
                    G.add_node(vertex)
                    G.ordered_vertices.append(vertex)

            for s in sources:
                G.add_edge(s,target)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(format))

    return G

#################################################################
#          Graph writer(s)
#################################################################

def writeGraph(G,output_file,format,graph_type='simple'):
    """Write a graph to a file

    Arguments:
    - `G`: graph object
    - `output_file`: file name or file handle to write on
    - `output_format`: graph format (e.g. dot, gml)
    - `graph_type`: one among {graph,digraph,dag,bipartite}

    Return: none.
    """
    if graph_type not in _graphformats:
        raise ValueError("Invalid graph type")

    if format not in _graphformats[graph_type]:
        raise ValueError("Invalid format for {} graph".format(graph_type))

    if format=='dot':

        networkx.write_dot(G,output_file)

    elif format=='gml':

        networkx.write_gml(G,output_file)

    elif format=='kth':

        print("c {}".format(G.name),file=output_file)
        print("{}".format(G.order()),file=output_file)

        # we need numerical indices for the vertices
        enumeration = zip( enumerate_vertices(G),
                               xrange(1,G.order()+1))

        # adj list in the same order
        indices = dict( enumeration )

        from cStringIO import StringIO
        output = StringIO()

        for v,i in enumeration:

            if G.is_directed():
                neighbors = [indices[w] for w in G.predecessors(v)]

            else:
                neighbors = [indices[w] for w in G.adj[v].keys()]

            neighbors.sort()

            output.write( str(i)+" : ")
            output.write( " ".join([str(i) for i in neighbors]))
            output.write( "\n")

        print(output.getvalue(),file=output_file)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(format))

    return G



#
# Use, when possible, a fixed vertex order
#
def enumerate_vertices(graph):
    """Compute an ordered list of vertices of `graph`

    If the graph as the field `ordered_vertices` use it. Otherwise
    give an arbitrary vertex sequence.

    Arguments:
    - `graph`: input graph
    """
    if hasattr(graph,"ordered_vertices"):
        assert graph.order()==len(graph.ordered_vertices)
        assert set(graph.nodes())==set(graph.ordered_vertices)
        return graph.ordered_vertices
    else:
        return graph.nodes()

