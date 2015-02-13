#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
from .cnf import CNF

# internal methods
from .graphs import enumerate_vertices,is_dag
from .cnf    import parity_constraint


__docstring__ =\
"""Formula families useful in proof complexity

Copyright (C) 2012, 2013, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

__all__ = ["PigeonholePrinciple",
           "PebblingFormula",
           "OrderingPrinciple","GraphOrderingPrinciple",
           "RamseyNumber","TseitinFormula","SubgraphFormula"]

import sys
from textwrap import dedent
from itertools import product,permutations
from itertools import combinations,combinations_with_replacement

# Network X is used to produce graph based formulas
try:
    import networkx
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",
          file=sys.stderr)
    exit(-1)


###
### Formula families
###

def PigeonholePrinciple(pigeons,holes,functional=False,onto=False):
    """Pigeonhole Principle CNF formula

    The pigeonhole  principle claims  that no M  pigeons can sit  in N
    pigeonholes  without collision  if M>N.   The  counterpositive CNF
    formulation  requires  such mapping  to  be  satisfied. There  are
    different  variants of this  formula, depending  on the  values of
    `functional` and `onto` argument.

    - PHP: pigeon can sit in multiple holes
    - FPHP: each pigeon sits in exactly one hole
    - onto-PHP: pigeon can  sit in multiple holes, every  hole must be
                covered.
    - Matching: one-to-one bijection between pigeons and holes.

    Arguments:
    - `pigeon`: number of pigeons
    - `hole`:   number of holes
    - `functional`: add clauses to enforce at most one hole per pigeon
    - `onto`: add clauses to enforce that any hole must have a pigeon

    >>> print(PigeonholePrinciple(4,3).dimacs(export_header=False))
    p cnf 12 22
    1 2 3 0
    4 5 6 0
    7 8 9 0
    10 11 12 0
    -1 -4 0
    -1 -7 0
    -1 -10 0
    -4 -7 0
    -4 -10 0
    -7 -10 0
    -2 -5 0
    -2 -8 0
    -2 -11 0
    -5 -8 0
    -5 -11 0
    -8 -11 0
    -3 -6 0
    -3 -9 0
    -3 -12 0
    -6 -9 0
    -6 -12 0
    -9 -12 0
    """
    if functional:
        if onto:
            formula_name="Matching"
        else:
            formula_name="Functional pigeonhole principle"
    else:
        if onto:
            formula_name="Onto pigeonhole principle"
        else:
            formula_name="Pigeonhole principle"

    # Clause generator
    def _PHP_clause_generator(pigeons,holes,functional,onto):
        # Pigeon axioms
        for p in xrange(1,pigeons+1):
            yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for h in xrange(1,holes+1)]
        # Onto axioms
        if onto:
            for h in xrange(1,holes+1):
                yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for p in xrange(1,pigeons+1)]
        # No conflicts axioms
        for h in xrange(1,holes+1):
            for (p1,p2) in combinations(range(1,pigeons+1),2):
                yield [ (False,'p_{{{0},{1}}}'.format(p1,h)),
                        (False,'p_{{{0},{1}}}'.format(p2,h)) ]
        # Function axioms
        if functional:
            for p in xrange(1,pigeons+1):
                for (h1,h2) in combinations(range(1,holes+1),2):
                    yield [ (False,'p_{{{0},{1}}}'.format(p,h1)),
                            (False,'p_{{{0},{1}}}'.format(p,h2)) ]

    php=CNF()
    php.header="{0} formula for {1} pigeons and {2} holes\n".format(formula_name,pigeons,holes) + php.header

    clauses=_PHP_clause_generator(pigeons,holes,functional,onto)
    for c in clauses:
        php.add_clause(c)

    return php





def PebblingFormula(digraph):
    """Pebbling formula

    Build a pebbling formula from the directed graph. If the graph has
    an `ordered_vertices` attribute, then it is used to enumerate the
    vertices (and the corresponding variables).

    Arguments:
    - `digraph`: directed acyclic graph.
    """
    if not is_dag(digraph):
        raise RuntimeError("Pebbling formula is defined only for directed acyclic graphs")

    peb=CNF()

    if hasattr(digraph,'name'):
        peb.header="Pebbling formula of: "+digraph.name+"\n\n"+peb.header
    else:
        peb.header="Pebbling formula\n\n"+peb.header

    # add variables in the appropriate order
    vertices=enumerate_vertices(digraph)

    for v in vertices:
        peb.add_variable(v)

    # add the clauses
    for v in vertices:

        # If predecessors are pebbled the vertex must be pebbled
        peb.add_clause([(False,p) for p in digraph.predecessors(v)]+[(True,v)])

        if digraph.out_degree(v)==0: #the sink
            peb.add_clause([(False,v)])

    return peb


def OrderingPrinciple(size,total=False,smart=False,plant=False,knuth=0):
    """Generates the clauses for ordering principle

    Arguments:
    - `size`  : size of the domain
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
    - `plant` : allow a single element to be minimum (could make the formula SAT)
    - `knuth` : Donald Knuth variant of the formula ver. 2 or 3 (anything else suppress it)
    """

    return GraphOrderingPrinciple(networkx.complete_graph(size),total,smart,plant,knuth)


def GraphOrderingPrinciple(graph,total=False,smart=False,plant=False,knuth=0):
    """Generates the clauses for graph ordering principle

    Arguments:
    - `graph` : undirected graph
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
    - `plant` : allow a single element to be minimum (could make the formula SAT)
    - `knuth` : Donald Knuth variant of the formula ver. 2 or 3 (anything else suppress it)
    """
    gop=CNF()

    # Describe the formula
    if total or smart:
        name="Total graph ordering principle"
    else:
        name="Graph ordering principle"

    if smart:
        name = name + "(compact representation)"

    if hasattr(graph,'name'):
        gop.header=name+" on graph:\n"+graph.name+"\n"+gop.header
    else:
        gop.header=name+".\n"+gop.header

    #
    # Non minimality axioms
    #

    # Fix the vertex order
    V=graph.nodes()

    # Clause is generated in such a way that if totality is enforces,
    # every pair occurs with a specific orientation.
    # Allow minimum on last vertex if 'plant' options.

    for med in xrange(len(V)- (plant and 1) ):
        clause = []
        for lo in xrange(med):
            if graph.has_edge(V[med],V[lo]):
                clause += [(True,'x_{{{0},{1}}}'.format(V[lo],V[med]))]
        for hi in xrange(med+1,len(V)):
            if not graph.has_edge(V[med],V[hi]):
                continue
            elif smart:
                clause += [(False,'x_{{{0},{1}}}'.format(V[med],V[hi]))]
            else:
                clause += [(True,'x_{{{0},{1}}}'.format(V[hi],V[med]))]
        gop.add_clause(clause)

    #
    # Transitivity axiom
    #
    
    if len(V)>=3:
        if smart:
            # Optimized version if smart representation of totality is used
            for (v1,v2,v3) in combinations(V,3):
                gop.add_clause([ (True,'x_{{{0},{1}}}'.format(v1,v2)),
                                (True,'x_{{{0},{1}}}'.format(v2,v3)),
                                (False,'x_{{{0},{1}}}'.format(v1,v3))])
                gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True,'x_{{{0},{1}}}'.format(v1,v3))])
        else:
            for (v1,v2,v3) in permutations(V,3):

                # knuth variants will reduce the number of
                # transitivity axioms
                if knuth==2 and ((v2<v1) or (v2<v3)): continue
                if knuth==3 and ((v3<v1) or (v3<v2)): continue

                gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True, 'x_{{{0},{1}}}'.format(v1,v3))])

    if not smart:
        # Antisymmetry axioms (useless for 'smart' representation)
        for (v1,v2) in combinations(V,2):
            gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                            (False,'x_{{{0},{1}}}'.format(v2,v1))])

        # Totality axioms (useless for 'smart' representation)
        if total:
            for (v1,v2) in combinations(V,2):
                gop.add_clause([ (True,'x_{{{0},{1}}}'.format(v1,v2)),
                                 (True,'x_{{{0},{1}}}'.format(v2,v1))])

    return gop


def ColoringFormula(graph,colors,functional=True):
    """Generates the clauses for k-colorability formula

    Arguments:
    - `graph`  : undirected graph
    - `colors` : sequence of available colors
    """
    kcol=CNF()

    # Describe the formula
    name="K-Colorabily"
    
    if hasattr(graph,'name'):
        kcol.header=name+" of graph:\n"+graph.name+"\n"+kcol.header
    else:
        kcol.header=name+".\n"+kcol.header

    # Fix the vertex order
    V=graph.nodes()

    # Each vertex has a color
    for vertex in V:
        clause = []
        for color in colors:
            clause += [(True,'x_{{{0},{1}}}'.format(vertex,color))]
        kcol.add_clause(clause)
        
        # unique color per vertex
        if functional:
            for (c1,c2) in combinations(colors,2):
                kcol.add_clause([
                    (False,'x_{{{0},{1}}}'.format(vertex,c1)),
                    (False,'x_{{{0},{1}}}'.format(vertex,c2))])

    # This is a legal coloring
    for (v1,v2) in combinations(V,2):
        if graph.has_edge(v1,v2):
            for c in colors:
                kcol.add_clause([
                    (False,'x_{{{0},{1}}}'.format(v1,c)),
                    (False,'x_{{{0},{1}}}'.format(v2,c))])
            
    return kcol



def RamseyNumber(s,k,N):
    """Formula claiming that Ramsey number r(s,k) > N

    Arguments:
    - `s`: independent set size
    - `k`: clique size
    - `N`: vertices
    """

    ram=CNF()

    ram.header=dedent("""\
        CNF encoding of the claim that there is a graph of %d vertices
        with no independent set of size %d and no clique of size %d
        """ % (N,s,k)) + ram.header

    #
    # No independent set of size s
    #
    for vertex_set in combinations(xrange(1,N+1),s):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause += [(True,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    #
    # No clique of size k
    #
    for vertex_set in combinations(xrange(1,N+1),k):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause+=[(False,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    return ram


def TseitinFormula(graph,charges=None):
    """Build a Tseitin formula based on the input graph.

Odd charge is put on the first vertex by default, unless other
vertices are is specified in input.

    Arguments:
    - `graph`: input graph
    - `charges': odd or even charge for each vertex
    """
    V=graph.nodes()

    if charges==None:
        charges=[1]+[0]*(len(V)-1)             # odd charge on first vertex
    else:
        charges = [bool(c) for c in charges]   # map to boolean

    if len(charges)<len(V):
        charges=charges+[0]*(len(V)-len(charges))  # pad with even charges

    # init formula
    tse=CNF()
    for e in graph.edges():
        tse.add_variable("E_{{{0},{1}}}".format(*sorted(e)))

    # add constraints
    for v,c in zip(V,charges):
        
        # produce all clauses and save half of them
        names = [ "E_{{{0},{1}}}".format(*sorted(e)) for e in graph.edges_iter(v) ]
        for cls in parity_constraint(names,c):
            tse.add_clause(list(cls))

    return tse

def SubgraphFormula(graph,templates):
    """Formula which claims that one of the subgraph is contained in a
    graph.

    Arguments:
    - `graph'    : input graph
    - `templates': a sequence of graphs
    """

    F=CNF()

    # One of the templates is chosen to be the subgraph
    if len(templates)==0:
        return F
    elif len(templates)==1:
        selectors=[]
    elif len(templates)==2:
        selectors=['c']
    else:
        selectors=['c_{{{}}}'.format(i) for i in range(len(templates))]

    if len(selectors)>1:

        # Exactly one of the graphs must be selected as subgraph
        F.add_clause([(True,v) for v in selectors])

        for (a,b) in combinations(selectors):
            F.add_clause( [ (False,a), (False,b) ] )

    # comment the formula accordingly
    if len(selectors)>1:
        F.header=dedent("""\
                 CNF encoding of the claim that a graph contains one among
                 a family of {0} possible subgraphs.
                 """.format(len(templates))) + F.header
    else:
        F.header=dedent("""\
                 CNF encoding of the claim that a graph contains an induced
                 copy of a subgraph.
                 """.format(len(templates)))  + F.header

    # A subgraph is chosen
    N=graph.order()
    k=max([s.order() for s in templates])

    for i,j in product(range(k),range(N)):
        F.add_variable("S_{{{0}}}{{{1}}}".format(i,j))

    # each vertex has an image...
    for i in range(k):
        F.add_clause([(True,"S_{{{0}}}{{{1}}}".format(i,j)) for j in range(N)])

    # ...and exactly one
    for i,(a,b) in product(range(k),combinations(range(N),2)):
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(i,a)),
                      (False,"S_{{{0}}}{{{1}}}".format(i,b))  ])

 
    # Mapping is strictly monotone increasing (so it is also injective)
    localmaps = product(combinations(range(k),2),
                        combinations_with_replacement(range(N),2))

    for (a,b),(i,j) in localmaps:
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(min(a,b),max(i,j))),
                      (False,"S_{{{0}}}{{{1}}}".format(max(a,b),min(i,j)))  ])


    # The selectors choose a template subgraph.  A mapping must map
    # edges to edges and non-edges to non-edges for the active
    # template.

    if len(templates)==1:

        activation_prefixes = [[]]

    elif len(templates)==2:

        activation_prefixes = [[(True,selectors[0])],[(False,selectors[0])]]

    else:
        activation_prefixes = [[(True,v)] for v in selectors]


    # maps must preserve the structure of the template graph
    gV = graph.nodes()

    for i in range(len(templates)):


        k  = templates[i].order()
        tV = templates[i].nodes()

        localmaps = product(combinations(range(k),2),
                            combinations(range(N),2))


        for (i1,i2),(j1,j2) in localmaps:

            # check if this mapping is compatible
            tedge=templates[i].has_edge(tV[i1],tV[i2])
            gedge=graph.has_edge(gV[j1],gV[j2])
            if tedge == gedge: continue

            # if it is not, add the corresponding
            F.add_clause(activation_prefixes[i] + \
                         [(False,"S_{{{0}}}{{{1}}}".format(min(i1,i2),min(j1,j2))),
                          (False,"S_{{{0}}}{{{1}}}".format(max(i1,i2),max(j1,j2))) ])

    return F

