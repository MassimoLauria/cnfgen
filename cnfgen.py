#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
from cnf import CNF
from cnf import LiftFormula,available_lifting

__docstring__ =\
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git


Create you own CNFs:

>>> c=CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], \
          [(False,"x2"),(True,"x4")] ])
>>> print( c.dimacs(False) )
p cnf 4 2
1 2 -3 0
-2 4 0

You can add clauses later in the process:

>>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
>>> print( c.dimacs(add_header=False))
p cnf 5 3
1 2 -3 0
-2 4 0
-3 4 -5 0

"""

import sys
from textwrap import dedent
from itertools import product,permutations
from itertools import combinations,combinations_with_replacement

import argparse
import random

try:
    import networkx
    import networkx.algorithms
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

    >>> print(PigeonholePrinciple(4,3).dimacs(False,True))
    p cnf 12 22
    c Pigeon axiom: pigeon 1 sits in a hole
    1 2 3 0
    c Pigeon axiom: pigeon 2 sits in a hole
    4 5 6 0
    c Pigeon axiom: pigeon 3 sits in a hole
    7 8 9 0
    c Pigeon axiom: pigeon 4 sits in a hole
    10 11 12 0
    c No collision in hole 1
    -1 -4 0
    -1 -7 0
    -1 -10 0
    -4 -7 0
    -4 -10 0
    -7 -10 0
    c No collision in hole 2
    -2 -5 0
    -2 -8 0
    -2 -11 0
    -5 -8 0
    -5 -11 0
    -8 -11 0
    c No collision in hole 3
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
            yield "Pigeon axiom: pigeon {0} sits in a hole".format(p)
            yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for h in xrange(1,holes+1)]
        # Onto axioms
        if onto:
            for h in xrange(1,holes+1):
                yield "Onto hole axiom: hole {0} hosts a pigeon".format(h)
                yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for p in xrange(1,pigeons+1)]
        # No conflicts axioms
        for h in xrange(1,holes+1):
            yield "No collision in hole {0}".format(h)
            for (p1,p2) in combinations(range(1,pigeons+1),2):
                yield [ (False,'p_{{{0},{1}}}'.format(p1,h)),
                        (False,'p_{{{0},{1}}}'.format(p2,h)) ]
        # Function axioms
        if functional:
            for p in xrange(1,pigeons+1):
                yield "No multiple images for pigeon {0}".format(p)
                for (h1,h2) in combinations(range(1,holes+1),2):
                    yield [ (False,'p_{{{0},{1}}}'.format(p,h1)),
                            (False,'p_{{{0},{1}}}'.format(p,h2)) ]

    php=CNF()
    php.header="{0} formula for {1} pigeons and {2} holes\n".format(formula_name,pigeons,holes) + php.header

    clauses=_PHP_clause_generator(pigeons,holes,functional,onto)
    for c in clauses:
        php.add_clause_or_comment(c)

    return php


def PebblingFormula(digraph):
    """Pebbling formula

    Build a pebbling formula from the directed graph. If the graph has
    an `ordered_vertices` attribute, then it is used to enumerate the
    vertices (and the corresponding variables).

    Arguments:
    - `digraph`: directed acyclic graph.
    """
    if not networkx.algorithms.is_directed_acyclic_graph(digraph):
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

        # If predecessors are pebbled it must be pebbles
        if digraph.in_degree(v)!=0:
            peb.add_comment("Pebbling propagates on vertex {}".format(v))
        else:
            peb.add_comment("Source vertex {}".format(v))

        peb.add_clause([(False,p) for p in digraph.predecessors(v)]+[(True,v)])

        if digraph.out_degree(v)==0: #the sink
            peb.add_comment("Sink vertex {}".format(v))
            peb.add_clause([(False,v)])

    return peb


def OrderingPrinciple(size,total=False,smart=False):
    """Generates the clauses for ordering principle

    Arguments:
    - `size`  : size of the domain
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
    """

    return GraphOrderingPrinciple(networkx.complete_graph(size),total,smart)


def GraphOrderingPrinciple(graph,total=False,smart=False):
    """Generates the clauses for graph ordering principle

    Arguments:
    - `graph` : undirected graph
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
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

    # Non minimality axioms
    gop.add_comment("Each vertex has a predecessor")

    # Fix the vertex order
    V=graph.nodes()

    # Clause is generated in such a way that if totality is enforces,
    # every pair occurs with a specific orientation.
    for med in xrange(len(V)):
        clause = []
        for lo in xrange(med):
            if graph.has_edge(V[med],V[lo]):
                clause += [(True,'x_{{{0},{1}}}'.format(lo,med))]
        for hi in xrange(med+1,len(V)):
            if not graph.has_edge(V[med],V[hi]):
                continue
            elif smart:
                clause += [(False,'x_{{{0},{1}}}'.format(med,hi))]
            else:
                clause += [(True,'x_{{{0},{1}}}'.format(hi,med))]
        gop.add_clause(clause)

    # Transitivity axiom
    gop.add_comment("Relation must be transitive")

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
                gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True, 'x_{{{0},{1}}}'.format(v1,v3))])

    if not smart:
        # Antisymmetry axioms (useless for 'smart' representation)
        gop.add_comment("Relation must be anti-symmetric")
        for (v1,v2) in combinations(V,2):
            gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                            (False,'x_{{{0},{1}}}'.format(v2,v1))])

        # Totality axioms (useless for 'smart' representation)
        if total:
            gop.add_comment("Relation must be total")
            for (v1,v2) in combinations(V,2):
                gop.add_clause([ (True,'x_{{{0},{1}}}'.format(v1,v2)),
                                 (True,'x_{{{0},{1}}}'.format(v2,v1))])

    return gop


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
        with no indipendent set of size %d and no clique of size %d
        """ % (s,k,N)) + ram.header

    # No independent set of size s
    ram.add_comment("No independent set of size %d" % s)

    for vertex_set in combinations(xrange(1,N+1),s):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause += [(True,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    # No clique of size k
    ram.add_comment("No clique of size %d"%k)

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
    ordered_edges=graph.edges()
    tse=CNF()
    for (v,w) in graph.edges():
        tse.add_variable("E_{{{0},{1}}}".format(v,w))

    # add constraints
    ordered_edges=graph.edges()
    for v,c in zip(V,charges):
        tse.add_comment("Vertex {} must have {} charge".format(v," odd" if c else "even"))

        edges=filter(lambda e: v in e, ordered_edges)

        # produce all clauses and save half of them
        names = [ "E_{{{0},{1}}}".format(v,w) for (v,w) in edges ]
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

        F.add_comment("Exactly of the graphs must be a subgraph")
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

    # each vertex has an image
    F.add_comment("A subgraph is chosen")
    for i in range(k):
        F.add_clause([(True,"S_{{{0}}}{{{1}}}".format(i,j)) for j in range(N)])

    # and exactly one
    F.add_comment("The mapping is a function")
    for i,(a,b) in product(range(k),combinations(range(N),2)):
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(i,a)),
                      (False,"S_{{{0}}}{{{1}}}".format(i,b))  ])

    # # and there are no collision
    # F.add_comment("The function is injective")
    # for (a,b),j in product(combinations(range(k),2),range(N)):
    #     F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(a,j)),
    #                   (False,"S_{{{0}}}{{{1}}}".format(b,j))  ])

    F.add_comment("Mapping is strictly monotone increasing (so it is also injective)")
    localmaps = product(combinations(range(k),2),
                        combinations_with_replacement(range(N),2))

    for (a,b),(i,j) in localmaps:
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(min(a,b),max(i,j))),
                      (False,"S_{{{0}}}{{{1}}}".format(max(a,b),min(i,j)))  ])


    # The selectors choose a template subgraph.  A mapping must map
    # edges to edges and non-edges to non-edges for the active
    # template.

    if len(templates)==1:

        activation_prefixes=[[]]

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

        F.add_comment("structure constraints for subgraph {}".format(i))

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


#################################################################
#          Graph Decoders (first is default)
#################################################################
implemented_graphformats = {
    'dag':   ['kth','gml','dot'],
    'bipartite':   ['kth','gml','dot'],
    'digraph': ['kth','gml','dot'],
    'simple': ['kth','gml','dot']
    }

# remove dot format if graphviz is not installed
# we put it by default for documentation purpose
try:
    import pygraphviz
except ImportError:
    print("WARNING: Missing 'dot' library: no support for graph based formulas.",
          file=sys.stderr)
    for k in implemented_graphformats.values():
        try:
            k.remove('dot')
        except ValueError:
            pass


def readDigraph(file,format,force_dag=False,multi=False):
    """Read a directed graph from file

    Arguments:
    - `file`: file object
    - `format`: file format
    - `force_dag`: enforces whether graph must be acyclic
    - `multi`:     multiple edge allowed

    Return: a networkx.DiGraph / networkx.MultiDiGraph object.
    """
    if format not in implemented_graphformats['digraph']:
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
    if format not in implemented_graphformats['simple']:
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


def writeGraph(G,output_file,format,graph_type='simple'):
    """Write a graph to a file

    Arguments:
    - `G`: graph object
    - `output_file`: file name or file handle to write on
    - `output_format`: graph format (e.g. dot, gml)
    - `graph_type`: one among {graph,digraph,dag,bipartite}

    Return: none.
    """
    if graph_type not in implemented_graphformats:
        raise ValueError("Invalid graph type")

    if format not in implemented_graphformats[graph_type]:
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



#################################################################
#          Command line tool follows
#################################################################


class HelpLiftingAction(argparse.Action):
    def __init__(self, **kwargs):
        super(HelpLiftingAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        print("""
        Liftings/Substitutions available
        """)
        for k,entry in available_lifting().iteritems():
            print("{}\t:  {}".format(k,entry[k][0]))
        print("\n")
        sys.exit(0)

###
### Command line helpers
###

class _CMDLineHelper(object):
    """Base Command Line helper

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def setup_command_line(parser):
        """Add command line options for this family of formulas
        """
        pass

    @staticmethod
    def additional_options_check(args):
        pass


class _GeneralCommandLine(_CMDLineHelper):
    """Command Line helper for the general commands

    For every formula family there should be a subclass.
    """

    @staticmethod
    def setup_command_line(parser):
        """Setup general command line options

        Arguments:
        - `parser`: parser to fill with options
        """
        parser.add_argument('--output','-o',
                            type=argparse.FileType('wb',0),
                            metavar="<output>",
                            default='-',
                            help="""Output file. The formula is saved
                            on file instead of being sent to standard
                            output. Setting '<output>' to '-' is another
                            way to send the formula to standard output.
                            (default: -)
                            """)
        parser.add_argument('--output-format','-of',
                            choices=['latex','dimacs'],
                            default='dimacs',
                            help="""
                            Output format of the formulas. 'latex' is
                            convenient to insert formulas into papers, and
                            'dimacs' is the format used by sat solvers.
                            (default: dimacs)
                            """)

        parser.add_argument('--seed','-S',
                            metavar="<seed>",
                            default=None,
                            type=str,
                            action='store',
                            help="""Seed for any random process in the
                            program. Any python hashable object will
                            be fine.  (default: current time)
                            """)
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--verbose', '-v',action='count',default=1,
                       help="""Add comments inside the formula. It may
                            not be supported by very old sat solvers.
                            """)
        g.add_argument('--quiet', '-q',action='store_const',const=0,dest='verbose',
                       help="""Output just the formula with not header
                            or comment.""")
        parser.add_argument('--lift','-l',
                            metavar="<lifting method>",
                            choices=available_lifting().keys(),
                            default='none',
                            help="""
                            Apply a lifting procedure to make the CNF harder.
                            See `--help-lifting` for more informations
                            """)
        parser.add_argument('--liftrank','-lr',
                            metavar="<lifting rank>",
                            type=int,
                            default=None,
                            help="""
                            Hardness parameter for the lifting procedure.
                            See `--help-lifting` for more informations
                            """)
        parser.add_argument('--help-lifting',nargs=0,action=HelpLiftingAction,help="""
                             Formula can be made harder applying some
                             so called "lifting procedures".
                             This gives information about the implemented lifting.
                             """)


### Graph readers/generators

class _GraphHelper(object):
    """Command Line helper for reading graphs
    """

    @staticmethod
    def obtain_graph(args):
        raise NotImplementedError("Graph Input helper must be subclassed")


class _DAGHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group("Reading a directed acyclic graph (DAG) from input")
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The DAG is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Output the DAG to a file. The
                            graph is saved, which is useful if the
                            graph is generated internally.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=implemented_graphformats['dag'],
                        default=implemented_graphformats['dag'][0],
                        help="""
                        Format of the DAG in input/output, several
                        formats are supported if networkx is
                        installed.  (default:  {})
                        """.format(implemented_graphformats['dag'][0]))

        gr=parser.add_argument_group("Generate input DAG from a library")
        gr=gr.add_mutually_exclusive_group()
        gr.add_argument('--tree',type=int,action='store',metavar="<height>",
                            help="tree graph")

        gr.add_argument('--pyramid',type=int,action='store',metavar="<height>",
                            help="pyramid graph")

    @staticmethod
    def obtain_graph(args):
        """Produce a DAG from either input or library
        """
        if hasattr(args,'tree') and args.tree>0:

            D=networkx.DiGraph()
            D.ordered_vertices=[]
            # vertices
            vert=['v_{}'.format(i) for i in range(1,2*(2**args.tree))]
            for w in vert:
                D.add_node(w)
                D.ordered_vertices.append(w)
            # edges
            for i in range(len(vert)//2):
                D.add_edge(vert[2*i+1],vert[i])
                D.add_edge(vert[2*i+2],vert[i])

        elif hasattr(args,'pyramid') and args.pyramid>0:

            D=networkx.DiGraph()
            D.name='Pyramid of height {}'.format(args.pyramid)
            D.ordered_vertices=[]

            # vertices
            X=[
                [('x_{{{},{}}}'.format(h,i),h,i) for i in range(args.pyramid-h+1)]
                for h in range(args.pyramid+1)
              ]

            for layer in X:
                for (name,h,i) in layer:
                    D.add_node(name,rank=(h,i))
                    D.ordered_vertices.append(name)

            # edges
            for h in range(1,len(X)):
                for i in range(len(X[h])):
                    D.add_edge(X[h-1][i][0]  ,X[h][i][0])
                    D.add_edge(X[h-1][i+1][0],X[h][i][0])

        elif args.graphformat:

            D=readDigraph(args.input,args.graphformat,force_dag=True)

        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(D,
                       args.savegraph,
                       args.graphformat,
                       graph_type='dag')

        return D


class _SimpleGraphHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group("Read/Write the underlying undirected graph")
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The graph is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Output the graph to a file. The
                            graph is saved, which is useful if the
                            graph is randomly generated internally.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=implemented_graphformats['simple'],
                        default=implemented_graphformats['simple'][0],
                        help="""
                        Format of the graph in input/output, several
                        formats are supported in networkx is
                        installed.  (default:  {})
                        """.format(implemented_graphformats['simple'][0]))


        gr=parser.add_argument_group("Generate input graph from a library")
        gr=gr.add_mutually_exclusive_group()

        class IntFloat(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                n, p = int(values[0]),float(values[1])
                if not isinstance(n,int):
                    raise ValueError('n must be an integer')
                if not (isinstance(p,float) and p<=1.0 and p>=0):
                    raise ValueError('p must be an float between 0 and 1')
                setattr(args, self.dest, (n,p))

        gr.add_argument('--gnp',nargs=2,action=IntFloat,metavar=('n','p'),
                            help="random graph according to G(n,p) model (i.e. independent edges)")


        gr.add_argument('--gnm',type=int,nargs=2,action='store',metavar=('n','m'),
                            help="random graph according to G(n,m) model (i.e. m random edges)")

        gr.add_argument('--gnd',type=int,nargs=2,action='store',metavar=('n','d'),
                            help="random d-regular graph according to G(n,d) model (i.e. d random edges per vertex)")

        gr.add_argument('--grid',type=int,nargs='+',action='store',metavar=('d1','d2'),
                        help="n-dimensional grid of dimension d1 x d2 x ... ")

        gr.add_argument('--complete',type=int,action='store',metavar="<N>",
                            help="complete graph on N vertices")

        gr=parser.add_argument_group("Graph modifications")
        gr.add_argument('--plantclique',type=int,action='store',metavar="<k>",
                            help="choose k vertices at random and add all edges among them")


    @staticmethod
    def obtain_graph(args):
        """Build a Graph according to command line arguments

        Arguments:
        - `args`: command line options
        """
        if hasattr(args,'gnd') and args.gnd:

            n,d = args.gnd
            if (n*d)%2 == 1:
                raise ValueError("n * d must be even")
            G=networkx.random_regular_graph(d,n)
            return G

        elif hasattr(args,'gnp') and args.gnp:

            n,p = args.gnp
            G=networkx.gnp_random_graph(n,p)

        elif hasattr(args,'gnm') and args.gnm:

            n,m = args.gnm
            G=networkx.gnm_random_graph(n,m)

        elif hasattr(args,'grid') and args.grid:

            G=networkx.grid_graph(args.grid)

        elif hasattr(args,'complete') and args.complete>0:

            G=networkx.complete_graph(args.complete)

        elif args.graphformat:

            G=readGraph(args.input,args.graphformat)
        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Graph modifications
        if hasattr(args,'plantclique') and args.plantclique>1:

            clique=random.sample(G.nodes(),args.plantclique)

            for v,w in combinations(clique,2):
                G.add_edge(v,w)

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(G,
                       args.savegraph,
                       args.graphformat,
                       graph_type='simple')

        return G

### Formula families

class _FormulaFamilyHelper(object):
    """Command Line helper for formula families

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def build_cnf(args):
        pass


class _PHP(_FormulaFamilyHelper,_CMDLineHelper):
    name='php'
    description='pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('pigeons',metavar='<pigeons>',type=int,help="Number of pigeons")
        parser.add_argument('holes',metavar='<holes>',type=int,help="Number of holes")
        parser.add_argument('--functional',action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',action='store_true',
                            help="every hole has a sitting pigeon")
        parser.set_defaults(func=_PHP.build_cnf)

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PigeonholePrinciple(args.pigeons,
                                   args.holes,
                                   functional=args.functional,
                                   onto=args.onto)


class _RAM(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for RamseyNumber formulas
    """
    name='ram'
    description='ramsey number principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('s',metavar='<s>',type=int,help="Forbidden independent set size")
        parser.add_argument('k',metavar='<k>',type=int,help="Forbidden independent clique")
        parser.add_argument('N',metavar='<N>',type=int,help="Graph size")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RamseyNumber(args.s, args.k, args.N)


class _OP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Ordering principle formulas
    """
    name='op'
    description='ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")
        parser.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        parser.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return OrderingPrinciple(args.N,args.total,args.smart)


class _GOP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Graph Ordering principle formulas
    """
    name='gop'
    description='graph ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Graph ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        parser.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return GraphOrderingPrinciple(G,args.total,args.smart)


class _KClique(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for k-clique formula
    """
    name='kclique'
    description='k clique formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k)])


class _RAMLB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for ramsey graph formula
    """
    name='ramlb'
    description='unsat if G witnesses that r(k,s)>|V(G)| (i.e. G has not k-clique nor s-stable)'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for ramsey witness formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        parser.add_argument('s',metavar='<s>',type=int,action='store',help="size of the stable to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k),
                                  networkx.complete_graph(args.s)])



class _TSE(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Tseitin  formulas
    """
    name='tseitin'
    description='tseitin formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Tseitin formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--charge',metavar='<charge>',default='first',
                            choices=['first','random','randomodd','randomeven'],
                            help="""charge on the vertices.
                                    `first'  puts odd charge on first vertex;
                                    `random' puts a random charge on vertices;
                                    `randomodd' puts random odd  charge on vertices;
                                    `randomeven' puts random even charge on vertices.
                                     """)
        _SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)

        if G.order()<1:
            charge=None

        elif args.charge=='first':

            charge=[1]+[0]*(G.order()-1)

        else: # random vector
            charge=[random.randint(0,1) for i in xrange(G.order()-1)]

            parity=sum(charge) % 2

            if args.charge=='random':
                charge.append(random.randint(0,1))
            elif args.charge=='randomodd':
                charge.append(1-parity)
            elif args.charge=='randomeven':
                charge.append(parity)
            else:
                raise ValueError('Illegal charge specification on command line')

        return TseitinFormula(G,charge)


class _OR(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='or'
    description='a single disjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for single or of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build an disjunction

        Arguments:
        - `args`: command line options
        """
        clause = [ (True,"x_{}".format(i)) for i in range(args.P) ] + \
                 [ (False,"y_{}".format(i)) for i in range(args.N) ]
        return CNF([clause],
                   header="""Single clause with {} positive and {} negative literals""".format(args.P,args.N))


class _PEB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='peb'
    description='pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        _DAGHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D=_DAGHelper.obtain_graph(args)
        return PebblingFormula(D)


class _AND(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='and'
    description='a single conjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        clauses = [ [(True,"x_{}".format(i))] for i in range(args.P) ] + \
                  [ [(False,"y_{}".format(i))] for i in range(args.N) ]
        return CNF(clauses,
                   header="""Singleton clauses: {} positive and {} negative""".format(args.P,args.N))


###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv):

    # Commands and subcommand lines
    cmdline = _GeneralCommandLine
    subcommands=[_PHP,_TSE,_OP,_GOP,_PEB,_RAM,_RAMLB,_KClique,_OR,_AND]

    # Python 2.6 does not have argparse library
    try:
        import argparse
    except ImportError:
        print("Sorry: %s requires `argparse` library, which is missing.\n"%argv[0],file=sys.stderr)
        print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
        print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
        print(" * http://code.google.com/p/argparse",file=sys.stderr)
        print("",file=sys.stderr)
        exit(-1)

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog='cnfgen',epilog="""
    Each <formula type> has its own command line arguments and options.
    For more information type 'cnfgen <formula type> [--help | -h ]'
    """)
    cmdline.setup_command_line(parser)
    subparsers=parser.add_subparsers(title="Available formula types",metavar='<formula type>')

    # Setup of various formula command lines options
    for sc in subcommands:
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(subcommand=sc)

    # Process the options
    args=parser.parse_args()
    cmdline.additional_options_check(args)
    args.subcommand.additional_options_check(args)

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    # Generate the basic formula
    cnf=args.subcommand.build_cnf(args)

    # Apply the lifting
    lcnf=LiftFormula(cnf,args.lift,args.liftrank)


    # Do we wnat comments or not
    output_comments=args.verbose >= 2
    output_header  =args.verbose >= 1

    if args.output_format == 'latex':
        output = lcnf.latex(add_header=output_header,
                            add_comments=output_comments)

    elif args.output_format == 'dimacs':
        output = lcnf.dimacs(add_header=output_header,
                           add_comments=output_comments)
    else:
        output = lcnf.dimacs(add_header=output_header,
                           add_comments=output_comments)

    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
