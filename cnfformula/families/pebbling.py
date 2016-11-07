#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the pigeonhole principle formulas
"""

from __future__ import print_function


from cnfformula.cnf import CNF
from cnfformula.graphs import is_dag,enumerate_vertices
from cnfformula.graphs import has_bipartition,bipartite_sets

from itertools import product
from collections import OrderedDict

from cnfformula.cmdline import DirectedAcyclicGraphHelper
from cnfformula.cmdline import BipartiteGraphHelper

import cnfformula.families
import cnfformula.cmdline

import sys




def _uniqify_list(seq):
    """Remove duplicates while maintaining the order.

    (due to Dave Kirby) 

    Seen on https://www.peterbe.com/plog/uniqifiers-benchmark
    """
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]



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
        peb.add_clause_unsafe([(False,p) for p in pred]+[(True,v)])

        if digraph.out_degree(v)==0: #the sink
            peb.add_clause_unsafe([(False,v)])

    return peb




def stone_formula_helper(F,D,mapping):
    """Stones formulas helper

    Builds the clauses of a stone formula given the mapping object
    between stones and vertices of the DAG. THis is not supposed to be
    called by user code, and indeed this function assumes the following facts.

    - :math:`D` is equal to `mapping.domain()`
    - :math:`D` is a DAG

    Parameters
    ----------
    F : CNF
        the CNF which will contain the clauses of the stone formula

    D : a directed acyclic graph
        it should be a directed acyclic graph.

    mapping : unary_mapping object
       mapping between stones and graph vertices


    See Also
    --------
    StoneFormula : the classic stone formula
    SparseStoneFormula : stone formula with sparse mapping
    """

    # add variables in the appropriate order
    vertices=enumerate_vertices(D)

    # Stones->Vertices variables
    for v in mapping.variables():
        F.add_variable(v)

    # Color variables
    for stone in mapping.range():
        F.add_variable("R_{{{0}}}".format(stone),
                       description="Stone ${}$ is red".format(stone))
    
    # Each vertex has some stone
    for cls in mapping.clauses():
        F.add_clause_unsafe(cls)
        
    # If predecessors have red stones, the sink must have a red stone
    for v in vertices:
        for j in mapping.images(v):
            pred=sorted(D.predecessors(v),key=lambda x:mapping.RankDomain[x])
            for stones_tuple in product(*tuple( [s for s in mapping.images(v) if s!=j  ] for v in pred)):
                F.add_clause([(False, mapping.var_name(p,s)) for (p,s) in zip(pred,stones_tuple)] +
                               [(False, mapping.var_name(v,j))] +
                               [(False, "R_{{{0}}}".format(s)) for s in _uniqify_list(stones_tuple)] +
                               [(True,  "R_{{{0}}}".format(j))],
                               strict=True)
        
        if D.out_degree(v)==0: #the sink
            for j in mapping.images(v):
                F.add_clause([ (False, mapping.var_name(v,j)),
                               (False,"R_{{{0}}}".format(j))],
                               strict = True)

    return F


@cnfformula.families.register_cnf_generator
def StoneFormula(D,nstones):
    """Stone formulas

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

    # Add variables in the appropriate order
    vertices=enumerate_vertices(D)
    position=dict((v,i) for (i,v) in enumerate(vertices))
    stones=range(1,nstones+1)

    # Caching variable names
    color_vn = {}
    stone_vn = {}
    
    # Stones->Vertices variables
    for v in vertices:
        for j in stones:
            stone_vn[(v,j)] = "P_{{{0},{1}}}".format(v,j) 
            cnf.add_variable(stone_vn[(v,j)],
                             description="Stone ${1}$ on vertex ${0}$".format(v,j))

    # Color variables
    for j in stones:
        color_vn[j] = "R_{{{0}}}".format(j)
        cnf.add_variable(color_vn[j],
                         description="Stone ${}$ is red".format(j))
    
    # Each vertex has some stone
    for v in vertices:
        cnf.add_clause_unsafe([(True,stone_vn[(v,j)]) for j in stones])
        
    # If predecessors have red stones, the sink must have a red stone
    for v in vertices:
        for j in stones:
            pred=sorted(D.predecessors(v),key=lambda x:position[x])
            for stones_tuple in product([s for s in stones if s!=j],repeat=len(pred)):
                cnf.add_clause_unsafe([(False, stone_vn[(p,s)]) for (p,s) in zip(pred,stones_tuple)] +
                                      [(False, stone_vn[(v,j)])] +
                                      [(False, color_vn[s]) for s in _uniqify_list(stones_tuple)] +
                                      [(True,  color_vn[j])])
        
        if D.out_degree(v)==0: #the sink
            for j in stones:
                cnf.add_clause_unsafe([ (False,stone_vn[(v,j)]), (False,color_vn[j])])

    return cnf

@cnfformula.families.register_cnf_generator
def SparseStoneFormula(D,B):
    """Sparse Stone formulas

    This is a variant of the :py:func:`StoneFormula`. See that for
    a description of the formula. This variant is such that each
    vertex has only a small selection of which stone can go to that
    vertex. In particular which stones are allowed on each vertex is
    specified by a bipartite graph :math:`B` on which the left
    vertices represent the vertices of DAG :math:`D` and the right
    vertices are the stones. 

    If a vertex of :math:`D` correspond to the left vertex :math:`v`
    in :math:`B`, then its neighbors describe which stones are allowed
    for it.

    The vertices in :math:`D` do not need to have the same name as the
    one on the left side of :math:`B`. It is only important that the
    number of vertices in :math:`D` is the same as the vertices in the
    left side of :math:`B`.

    In that case the element at position :math:`i` in the ordered
    sequence ``enumerate_vertices(D)`` corresponds to the element of
    rank :math:`i` in the sequence of left side vertices of
    :math:`B` according to the output of ``Left, Right =
    bipartite_sets(B)``.

    Standard :py:func:`StoneFormula` is essentially equivalent to
    a sparse stone formula where :math:`B` is the complete graph.

    Parameters
    ----------
    D : a directed acyclic graph
        it should be a directed acyclic graph.
    B : bipartite graph

    Raises
    ------
    ValueError
       if :math:`D` is not a directed acyclic graph
    
    ValueError
       if :math:`B` is not a bipartite graph

    ValueError
       when size differs between :math:`D` and the left side of
       :math:`B`

    See Also
    --------
    StoneFormula

    """
    if not is_dag(D):
        raise ValueError("Stone formulas are defined only for directed acyclic graphs.")

    if not has_bipartition(B):
        raise ValueError("Vertices to stones mapping must be specified with a bipartite graph")
    
    Left, Right = bipartite_sets(B)
    nstones = len(Right)

    if len(Left) != D.order():
        raise ValueError("Formula requires the bipartite left side to match #vertices of the DAG.")
     
    cnf = CNF()
    
    if hasattr(D, 'name'):
        cnf.header = "Sparse Stone formula of: " + D.name + "\nwith " + str(nstones) + " stones\n" + cnf.header
    else:
        cnf.header = "Sparse Stone formula with " + str(nstones) + " stones\n" + cnf.header

    # add variables in the appropriate order
    vertices=enumerate_vertices(D)
    stones=range(1,nstones+1)
    
    mapping = cnf.unary_mapping(vertices,stones,sparsity_pattern=B)

    stone_formula_helper(cnf,D,mapping)
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
        except ValueError,e:
            print("\nError: {}".format(e),file=sys.stderr)
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
        except ValueError,e :
            print("\nError: {}".format(e),file=sys.stderr)
            sys.exit(-1)

@cnfformula.cmdline.register_cnfgen_subcommand
class SparseStoneCmdHelper:
    """Command line helper for stone formulas
    """
    name='stonesparse'
    description='stone formula (sparse version)'
    __doc__ = SparseStoneFormula.__doc__
    
    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)
        BipartiteGraphHelper.setup_command_line(parser,suffix="_mapping")

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        B= BipartiteGraphHelper.obtain_graph(args,suffix="_mapping")
        try:
            return SparseStoneFormula(D,B)
        except ValueError,e:
            print("\nError: {}".format(e),file=sys.stderr)
            sys.exit(-1)

            
