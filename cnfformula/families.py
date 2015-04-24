#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
from .cnf import CNF

# internal methods
from .graphs import enumerate_vertices,is_dag
from .cnf    import parity_constraint
from .cnf    import less_than_constraint


__docstring__ =\
"""Formula families useful in proof complexity

Copyright (C) 2012, 2013, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

__all__ = ["PigeonholePrinciple",
           "GraphPigeonholePrinciple",
           "PebblingFormula",
           "StoneFormula",
           "OrderingPrinciple",
           "GraphOrderingPrinciple",
           "GraphIsomorphism",
           "GraphAutomorphism",
           "RamseyNumber",
           "TseitinFormula",
           "ParityPrinciple",
           "GraphParityPrinciple",
           "SubgraphFormula",
           "RandomKCNF"]

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

def GraphPigeonholePrinciple(graph,functional=False,onto=False):
    """Graph Pigeonhole Principle CNF formula

    The graph pigeonhole principle CNF formula, defined on a bipartite
    graph G=(L,R,E), claims that there is a subset E' of the edges such that 
    every vertex on the left size L has at least one incident edge in E' and 
    every edge on the right side R has at most one incident edge in E'.

    This is possible only if the graph has a matching of size |L|.

    There are different variants of this formula, depending on the
    values of `functional` and `onto` argument.

    - PHP(G):  each left vertex can be incident to multiple edges in E'
    - FPHP(G): each left vertex must be incident to exaclty one edge in E'
    - onto-PHP: all right vertices must be incident to some vertex
    - matching: E' must be a perfect matching between L and R

    Arguments:
    - `graph` : bipartite graph
    - `functional`: add clauses to enforce at most one edge per left vertex
    - `onto`: add clauses to enforce that any right vertex has one incident edge


    Remark: the graph vertices must have the 'bipartite' attribute
    set. Left vertices must have it set to 0 and the right ones to
    1. Any vertex without the attribute is ignored.

    """
    if functional:
        if onto:
            formula_name="Graph matching"
        else:
            formula_name="Graph functional pigeonhole principle"
    else:
        if onto:
            formula_name="Graph onto pigeonhole principle"
        else:
            formula_name="Graph pigeonhole principle"

    Left  =  [v for v in graph.nodes() if graph.node[v]["bipartite"]==0]
    Right =  [v for v in graph.nodes() if graph.node[v]["bipartite"]==1]
            
    # Clause generator
    def _GPHP_clause_generator(G,functional,onto):
        # Pigeon axioms
        for p in Left:
            yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for h in G.adj[p]]
        # Onto axioms
        if onto:
            for h in Right:
                yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for p in G.adj[h]]
        # No conflicts axioms
        for h in Right:
            for (p1,p2) in combinations(G.adj[h],2):
                yield [ (False,'p_{{{0},{1}}}'.format(p1,h)),
                        (False,'p_{{{0},{1}}}'.format(p2,h)) ]
        # Function axioms
        if functional:
            for p in Left:
                for (h1,h2) in combinations(G.adj[p],2):
                    yield [ (False,'p_{{{0},{1}}}'.format(p,h1)),
                            (False,'p_{{{0},{1}}}'.format(p,h2)) ]

    gphp=CNF()
    gphp.header="{0} formula for graph {1}\n".format(formula_name,graph.name)

    clauses=_GPHP_clause_generator(graph,functional,onto)
    for c in clauses:
        gphp.add_clause(c)

    return gphp




def PebblingFormula(digraph):
    """Pebbling formula

    Build a pebbling formula from the directed graph. If the graph has
    an `ordered_vertices` attribute, then it is used to enumerate the
    vertices (and the corresponding variables).

    Arguments:
    - `digraph`: directed acyclic graph.
    """
    if not is_dag(digraph):
        raise ValueError("Pebbling formula is defined only for directed acyclic graphs")

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

def StoneFormula(digraph,nstones):
    """Stones formula

    Build a \"stone formula\" from the directed graph. If the graph has
    an `ordered_vertices` attribute, then it is used to enumerate the
    vertices (and the corresponding variables).

    These formula, introduced in [2] are one of the classic examples
    that separate regular resolutions from general resolution [1].

    Arguments:
    - `digraph`: directed acyclic graph.
    - `nstones`: number of stones.

    References:
    [1] M. Alekhnovich, J. Johannsen, T. Pitassi and A. Urquhart
    	An Exponential Separation between Regular and General Resolution.
        Theory of Computing (2007)
    [2] R. Raz and P. McKenzie
        Separation of the monotone NC hierarchy.
        Combinatorica (1999)

    """
    if not is_dag(digraph):
        raise ValueError("Stone formulas are defined only for directed acyclic graphs.")
    
    if nstones<0:
        raise ValueError("There must be at least one stone.")

    cnf = CNF()

    if hasattr(digraph, 'name'):
        cnf.header = "Stone formula of: " + digraph.name + "\nwith " + str(nstones) + " stones\n" + cnf.header
    else:
        cnf.header = "Stone formula with " + str(nstones) + " stones\n" + cnf.header

    # add variables in the appropriate order
    vertices=enumerate_vertices(digraph)
    stones=range(1,nstones+1)
    
    # Stones->Vertices variables
    for v in vertices:
        for j in stones:
            cnf.add_variable("P_{{{0},{1}}}".format(v,j))

    # Color variables
    for j in stones:
        cnf.add_variable("R_{{{0}}}".format(j))
    
    # Each vertex has some stone
    for v in vertices:
        cnf.add_clause([(True,"P_{{{0},{1}}}".format(v,j)) for j in stones])
        
    # If predecessors have red stones, the sink must have a red stone
    for v in vertices:
        for j in stones:
            pred=digraph.predecessors(v)
            for stones_tuple in product(stones,repeat=len(pred)):
                cnf.add_clause([(False, "P_{{{0},{1}}}".format(p,s)) for (p,s) in zip(pred,stones_tuple)] +
                                  [(False, "R_{{{0}}}".format(s)) for s in stones_tuple] +
                                  [(False, "P_{{{0},{1}}}".format(v,j))] +
                                  [(True,  "R_{{{0}}}".format(j))])
        
        if digraph.out_degree(v)==0: #the sink
            for j in stones:
                cnf.add_clause([
                    (False,"P_{{{0},{1}}}".format(v,j)),
                    (False,"R_{{{0}}}".format(j))
                ])

    return cnf



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
def _graph_isomorphism_var(u, v):
    return "x_{{{0},{1}}}".format(u, v)


def GraphIsomorphism(G1, G2):
    """Graph Isomorphism formula

    The formula is the CNF encoding of the statement that G1 and G2
    are two isomorphic graphs.

    Arguments:
    ----------
    - `G1` : a simple graph
    - `G2` : another simple graph

    Returns:
    --------
    A CNF formula which is satiafiable if and only if graphs G1 and G2
    are isomorphic.

    """
    F = CNF()
    F.header = "Graph Isomorphism problem between graphs " +\
               G1.name + " and " + G2.name + "\n" + F.header

    pairs = [(u, v) for u in G1.nodes() for v in G2.nodes()]
    var = _graph_isomorphism_var

    for (u, v) in pairs:
        F.add_variable(var(u, v))

    # Defined on both side
    for u in G1.nodes():
        F.add_clause([(True, var(u, v)) for v in G2.nodes()], strict=True)

    for v in G2.nodes():
        F.add_clause([(True, var(u, v)) for u in G1.nodes()], strict=True)

    # Injective on both sides
    for u in G1.nodes():
        for v1, v2 in combinations(G2.nodes(), 2):
            F.add_clause([(False, var(u, v1)),
                          (False, var(u, v2))], strict=True)
    for v in G2.nodes():
        for u1, u2 in combinations(G1.nodes(), 2):
            F.add_clause([(False, var(u1, v)),
                          (False, var(u2, v))], strict=True)

    # Edge consistency
    for u1, u2 in combinations(G1.nodes(), 2):
        for v1, v2 in combinations(G2.nodes(), 2):
            if G1.has_edge(u1, u2) != G2.has_edge(v1, v2):
                F.add_clause([(False, var(u1, v1)),
                              (False, var(u2, v2))], strict=True)
                F.add_clause([(False, var(u1, v2)),
                              (False, var(u2, v1))], strict=True)

    return F


def GraphAutomorphism(G):
    """Graph Automorphism formula

    The formula is the CNF encoding of the statement that a graph G
    has a nontrivial automorphism, i.e. an automorphism different from
    the idential one.

    Arguments:
    ----------
    - `G` : a simple graph

    Returns:
    --------
    A CNF formula which is satiafiable if and only if graph G has a
    nontrivial automorphism.
    """
    tmp = CNF()
    header = "Graph automorphism formula for graph "+ G.name +"\n"+ tmp.header
    F = GraphIsomorphism(G, G)
    F.header = header

    var = _graph_isomorphism_var

    F.add_clause([(False, var(u, u)) for u in G.nodes()], strict=True)

    return F


def GraphOrderingPrinciple(graph,total=False,smart=False,plant=False,knuth=0):
    """Generates the clauses for graph ordering principle

    Arguments:
    - `graph` : undirected graph
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies `total`)
    - `plant` : allow last element to be minimum (and could make the formula SAT)
    - `knuth` : Don Knuth variants 2 or 3 of the formula (anything else suppress it)
    """
    gop = CNF()

    # Describe the formula
    if total or smart:
        name = "Total graph ordering principle"
    else:
        name = "Ordering principle"

    if smart:
        name = name + "(compact representation)"

    if hasattr(graph, 'name'):
        gop.header = name+"\n on graph "+graph.name+"\n"+gop.header
    else:
        gop.header = name+".\n"+gop.header

    #
    # Non minimality axioms
    #

    # Fix the vertex order
    V = graph.nodes()

    # Clause is generated in such a way that if totality is enforces,
    # every pair occurs with a specific orientation.
    # Allow minimum on last vertex if 'plant' options.

    for med in xrange(len(V) - (plant and 1)):
        clause = []
        for lo in xrange(med):
            if graph.has_edge(V[med], V[lo]):
                clause += [(True, 'x_{{{0},{1}}}'.format(V[lo], V[med]))]
        for hi in xrange(med+1, len(V)):
            if not graph.has_edge(V[med], V[hi]):
                continue
            elif smart:
                clause += [(False, 'x_{{{0},{1}}}'.format(V[med], V[hi]))]
            else:
                clause += [(True, 'x_{{{0},{1}}}'.format(V[hi], V[med]))]
        gop.add_clause(clause)

    #
    # Transitivity axiom
    #

    if len(V) >= 3:
        if smart:
            # Optimized version if smart representation of totality is used
            for (v1, v2, v3) in combinations(V, 3):
                gop.add_clause([(True,  'x_{{{0},{1}}}'.format(v1, v2)),
                                (True,  'x_{{{0},{1}}}'.format(v2, v3)),
                                (False, 'x_{{{0},{1}}}'.format(v1, v3))])
                gop.add_clause([(False, 'x_{{{0},{1}}}'.format(v1, v2)),
                                (False, 'x_{{{0},{1}}}'.format(v2, v3)),
                                (True,  'x_{{{0},{1}}}'.format(v1, v3))])
        elif total:
            # With totality we still need just two axiom per triangle
            for (v1, v2, v3) in combinations(V, 3):
                gop.add_clause([(False, 'x_{{{0},{1}}}'.format(v1, v2)),
                                (False, 'x_{{{0},{1}}}'.format(v2, v3)),
                                (False, 'x_{{{0},{1}}}'.format(v3, v1))])
                gop.add_clause([(False, 'x_{{{0},{1}}}'.format(v1, v3)),
                                (False, 'x_{{{0},{1}}}'.format(v3, v2)),
                                (False, 'x_{{{0},{1}}}'.format(v2, v1))])
        else:
            for (v1, v2, v3) in permutations(V, 3):

                # knuth variants will reduce the number of
                # transitivity axioms
                if knuth == 2 and ((v2 < v1) or (v2 < v3)):
                    continue
                if knuth == 3 and ((v3 < v1) or (v3 < v2)):
                    continue

                gop.add_clause([(False, 'x_{{{0},{1}}}'.format(v1, v2)),
                                (False, 'x_{{{0},{1}}}'.format(v2, v3)),
                                (True,  'x_{{{0},{1}}}'.format(v1, v3))])

    if not smart:
        # Antisymmetry axioms (useless for 'smart' representation)
        for (v1, v2) in combinations(V, 2):
            gop.add_clause([(False, 'x_{{{0},{1}}}'.format(v1, v2)),
                            (False, 'x_{{{0},{1}}}'.format(v2, v1))])

        # Totality axioms (useless for 'smart' representation)
        if total:
            for (v1, v2) in combinations(V, 2):
                gop.add_clause([(True, 'x_{{{0},{1}}}'.format(v1, v2)),
                                (True, 'x_{{{0},{1}}}'.format(v2, v1))])

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


def GraphMatchingPrinciple(graph):
    """Generates the clauses for the graph matching principle.
    
    The principle claims that there is a way to select edges to such
    that all vertices have exactly one incident edge set to 1.

    Arguments:
    - `graph`  : undirected graph

    """
    cnf=CNF()

    # Describe the formula
    name="Graph Matching Principle"
    
    if hasattr(graph,'name'):
        cnf.header=name+" of graph:\n"+graph.name+"\n"+cnf.header
    else:
        cnf.header=name+".\n"+cnf.header

    def var_name(u,v):
        if u<=v:
            return 'x_{{{0},{1}}}'.format(u,v)
        else:
            return 'x_{{{0},{1}}}'.format(v,u)
            
    # Each vertex has exactly one edge set to one.
    for v in graph.nodes():

        edge_vars = [var_name(u,v) for u in graph.adj[v]]

        # at least one edge is active
        cnf.add_clause([(True,var) for var in edge_vars])

        # at most one edge is active
        for cls in less_than_constraint(edge_vars,2):
            cnf.add_clause(cls)

    return cnf


def MatchingPrinciple(size):
    """Matching principle on a domain with `size` elements

    Arguments:
    - `size`  : size of the domain
    """
    return GraphMatchingPrinciple(networkx.complete_graph(size))


def CountingPrinciple(M,p):
    """Generates the clauses for the counting matching principle.
    
    The principle claims that there is a way to partition M in sets of
    size p each.

    Arguments:
    - `M`  : size of the domain
    - `p`  : size of each class

    """
    cnf=CNF()

    # Describe the formula
    name="Counting Principle: {0} divided in parts of size {1}.".format(M,p)
    cnf.header=name+"\n"+cnf.header

    def var_name(tpl):
        return "Y_{{"+",".join("{0}".format(v) for v in tpl)+"}}"

    # Incidence lists
    incidence=[[] for x in range(M)]
    for tpl in combinations(range(M),p):
        for i in tpl:
            incidence[i].append(tpl)
    
    # Each element of the domain is in exactly one part.
    for el in range(M):

        edge_vars = [var_name(tpl) for tpl in incidence[el]]

        # the element is in at least one part
        cnf.add_clause([(True,var) for var in edge_vars])

        # the element is in at most one part
        for cls in less_than_constraint(edge_vars,2):
            cnf.add_clause(cls)

    return cnf



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
    V=sorted(graph.nodes())

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



def binomial_approx(n,k):
    if (k==0) : return 1,1
    import math
    lowerbound=(float(n)/k)**k
    upperbound=lowerbound*math.exp(k)
    return lowerbound,upperbound

def binomial(n,k):
    nCk=1
    for x in xrange(k):
        nCk*=(n-x)
        nCk/=(k-x)
    return nCk

""" Checks if m < 2^k (n choose k) without computing binomials"""
def m_less_than_2k_nchoosem(k,n,m):
    lowerbound,upperbound = binomial_approx(n,k)
    if (m < 2**k * lowerbound) : return True
    if (m > 2**k * upperbound) : return False
    return m <= 2**k * binomial(n,k)

""" Checks if m < (n choose g) (n-g choose k-g) without computing binomials"""
def m_less_than_nchooseg_ngchoosekg(k,n,m,g):
    lowerbound1,upperbound1 = binomial_approx(n,g)
    lowerbound2,upperbound2 = binomial_approx(n-g,k-g)
    if (m < lowerbound1*lowerbound2) : return True
    if (m > upperbound1*upperbound2) : return False
    return m <= binomial(n,g) * binomial(n-g,k-g)

def RandomKCNF(k, n, m, g=None, seed=None):
    """Build a random k-CNF

    Sample m k-clauses over n variables uniformly at random.

    If g is an integer, fix an assignment and sample from the subset
    of clauses where the assignment satisfies exactly g literals.

    Arguments
    ---------
    - `k`: width of each clause
    - `n': number of variables to choose from. The resulting cnf will
           contain n variables even if some are not picked.
    - `m`: number of clauses to generate
    - `g`: plant an assignment that satisfies exactly g literals in every clause.
    - `seed`: hashable object to seed the random generator with

    Returns
    -------
    a CNF object

    
    Raises
    ------
    ValueError when some paramenter is negative, or when k>n.
    """
    import random
    if seed: random.seed(seed)


    if n<0 or m<0 or k<0 or (g and g<0):
        raise ValueError("Parameters must be non-negative.")
    if k>n:
        raise ValueError("Too wide clauses.")
    if g and g>k:
        raise ValueError("Too many satisfied literals.")
    if g is None:
        if not m_less_than_2k_nchoosem(k,n,m):
            raise ValueError("Too many clauses.")
    else:
        if not m_less_than_nchooseg_ngchoosekg(k,n,m,g):
            raise ValueError("Too many clauses.")

    # TODO: if m < 2^k n choose k / 2, then remove clauses instead of adding them
    F = CNF()
    F.header = "Random {}-CNF over {} variables and {} clauses\n".format(k,n,m) + F.header
    
    for variable in xrange(1,n+1):
        F.add_variable(variable)

    clauses = set()
    if g is None:
        F.header = "Random {}-CNF over {} variables and {} clauses\n".format(k,n,m) + F.header
        while len(clauses)<m :
            clauses.add(frozenset((random.choice([True,False]),x+1)
                                  for x in random.sample(xrange(n),k)))
    else:
        F.header = ("Random {}-CNF over {} variables and {} clauses\n"
        "with a planted assignment that satisfies {} literals in every clause\n").format(k,n,m,g) + F.header
        assignment=[random.choice([True,False]) for x in xrange(n)]
        while len(clauses)<m :
            clauses.add(frozenset((assignment[x] ^ (i<g),x+1)
                                  for i,x in enumerate(random.sample(xrange(n),k))))
    for clause in clauses:
        F.add_clause(list(clause))

    return F
 
