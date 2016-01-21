#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the pigeonhole principle formulas
"""

from __future__ import print_function


from cnfformula.cnf import CNF
from cnfformula.graphs import is_dag,enumerate_vertices

from itertools import product
from collections import OrderedDict

from cnfformula.cmdline import DirectedAcyclicGraphHelper

import cnfformula.families
import cnfformula.cmdline

import sys




def _uniqify_list(x):
    """Remove duplicates while maintaining the order."""
    x=OrderedDict.fromkeys(x)
    return x.keys()



@cnfformula.families.register_cnf_generator
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
    position=dict((v,i) for (i,v) in enumerate(vertices))

    for v in vertices:
        peb.add_variable(v,description="There is a pebble on vertex ${}$".format(v))

    # add the clauses
    for v in vertices:

        # If predecessors are pebbled the vertex must be pebbled
        pred=sorted(digraph.predecessors(v),key=lambda x:position[x])
        peb.add_clause([(False,p) for p in pred]+[(True,v)],strict=True)

        if digraph.out_degree(v)==0: #the sink
            peb.add_clause([(False,v)],strict=True)

    return peb



@cnfformula.families.register_cnf_generator
def StoneFormula(D,nstones):
    """Stones formulas

    The stone formulas have been introduced in [2]_ and generalized in
    [1]_. They are one of the classic examples that separate regular
    resolutions from general resolution [1]_.

    A \"Stones formula\" from a directed acyclic graph :math:`D`
    claims that each vertex of the graph is associated with one on
    :math:`s` stones (not necessarily in an injective way).
    In particular for each vertex :math:`v` in :math:`V(D)` and each
    stone :math:`j` we have a variable :math:`P_{v,j}` that claims
    that stone :math:`j` is associated to vertex :math:`v`.

    Each stone can be either red or blue, and not both.
    The propositional variable :math:`R_j` if true when the stone
    :math:`j` is red and false otherwise.

    The clauses of the formula encode the following constraints.
    If a stone is on a source vertex (i.e. a vertex with no incoming
    edges), then it must be red. If all stones on the predecessors of
    a vertex are red, then the stone of the vertex itself must be red.

    The formula furthermore enforces that the stones on the sinks
    (i.e. vertices with no outgoing edges) are blue.

    .. note:: The exact formula structure depends by the graph and on
              its topological order, which is determined by the
              ``enumerate_vertices(D)``.

    Parameters
    ----------
    D : a directed acyclic graph
        it should be a directed acyclic graph.
    nstones : int
       the number of stones.

    Raises
    ------
    ValueError
       if :math:`D` is not a directed acyclic graph
    
    ValueError
       if the number of stones is negative

    References
    ----------
    .. [1] M. Alekhnovich, J. Johannsen, T. Pitassi and A. Urquhart
    	   An Exponential Separation between Regular and General Resolution.
           Theory of Computing (2007)
    .. [2] R. Raz and P. McKenzie
           Separation of the monotone NC hierarchy.
           Combinatorica (1999)

    """
    if not is_dag(D):
        raise ValueError("Stone formulas are defined only for directed acyclic graphs.")
    
    if nstones<0:
        raise ValueError("There must be at least one stone.")

    cnf = CNF()

    if hasattr(D, 'name'):
        cnf.header = "Stone formula of: " + D.name + "\nwith " + str(nstones) + " stones\n" + cnf.header
    else:
        cnf.header = "Stone formula with " + str(nstones) + " stones\n" + cnf.header

    # add variables in the appropriate order
    vertices=enumerate_vertices(D)
    position=dict((v,i) for (i,v) in enumerate(vertices))
    stones=range(1,nstones+1)
    
    # Stones->Vertices variables
    for v in vertices:
        for j in stones:
            cnf.add_variable("P_{{{0},{1}}}".format(v,j),
                             description="Stone ${1}$ on vertex ${0}$".format(v,j))

    # Color variables
    for j in stones:
        cnf.add_variable("R_{{{0}}}".format(j),
                         description="Stone ${}$ is red".format(j))
    
    # Each vertex has some stone
    for v in vertices:
        cnf.add_clause([(True,"P_{{{0},{1}}}".format(v,j)) for j in stones])
        
    # If predecessors have red stones, the sink must have a red stone
    for v in vertices:
        for j in stones:
            pred=sorted(D.predecessors(v),key=lambda x:position[x])
            for stones_tuple in product([s for s in stones if s!=j],repeat=len(pred)):
                cnf.add_clause([(False, "P_{{{0},{1}}}".format(p,s)) for (p,s) in zip(pred,stones_tuple)] +
                               [(False, "P_{{{0},{1}}}".format(v,j))] +
                               [(False, "R_{{{0}}}".format(s)) for s in _uniqify_list(stones_tuple)] +
                               [(True,  "R_{{{0}}}".format(j))],
                               strict=True)
        
        if D.out_degree(v)==0: #the sink
            for j in stones:
                cnf.add_clause([ (False,"P_{{{0},{1}}}".format(v,j)),
                                 (False,"R_{{{0}}}".format(j))],
                               strict = True)

    return cnf



@cnfformula.cmdline.register_cnfgen_subcommand
class PebblingCmdHelper:
    """Command line helper for pebbling formulas
    """
    name='peb'
    description='pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        try:
            return PebblingFormula(D)
        except ValueError:
            print("\nError: input graph must be directed and acyclic.",file=sys.stderr)
            sys.exit(-1)

@cnfformula.cmdline.register_cnfgen_subcommand
class StoneCmdHelper:
    """Command line helper for stone formulas
    """
    name='stone'
    description='stone formula'
    __doc__ = StoneFormula.__doc__
    
    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)
        parser.add_argument('s',metavar='<s>',type=int,help="number of stones")

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        try:
            return StoneFormula(D,args.s)
        except ValueError:
            print("\nError: Input graph must be a DAG, and a non negative # of stones.",file=sys.stderr)
            sys.exit(-1)
