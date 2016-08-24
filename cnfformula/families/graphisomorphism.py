#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Graph isomorphimsm/automorphism formulas
"""

from cnfformula.cnf import CNF
from cnfformula.cmdline import SimpleGraphHelper

from cnfformula.cmdline  import register_cnfgen_subcommand
from cnfformula.families import register_cnf_generator

from cnfformula.graphs import enumerate_vertices
from itertools import combinations,product




def _graph_isomorphism_var(u, v):
    """Standard variable name"""
    return "x_{{{0},{1}}}".format(u, v)

@register_cnf_generator
def GraphIsomorphism(G1, G2):
    """Graph Isomorphism formula

    The formula is the CNF encoding of the statement that two simple
    graphs G1 and G2 are isomorphic.

    Parameters
    ----------
    G1 : networkx.Graph
        an undirected graph object
    G2 : networkx.Graph
        an undirected graph object

    Returns
    -------
    A CNF formula which is satiafiable if and only if graphs G1 and G2
    are isomorphic.

    """
    F = CNF()
    F.header = "Graph Isomorphism problem between graphs " +\
               G1.name + " and " + G2.name + "\n" + F.header

    U=enumerate_vertices(G1)
    V=enumerate_vertices(G2)
    var = _graph_isomorphism_var

    for (u, v) in product(U,V):
        F.add_variable(var(u, v))

    # Defined on both side
    for u in U:
        F.add_clause([(True, var(u, v)) for v in V], strict=True)

    for v in V:
        F.add_clause([(True, var(u, v)) for u in U], strict=True)

    # Injective on both sides
    for u in U:
        for v1, v2 in combinations(V, 2):
            F.add_clause([(False, var(u, v1)),
                          (False, var(u, v2))], strict=True)
    for v in V:
        for u1, u2 in combinations(U, 2):
            F.add_clause([(False, var(u1, v)),
                          (False, var(u2, v))], strict=True)

    # Edge consistency
    for u1, u2 in combinations(U, 2):
        for v1, v2 in combinations(V, 2):
            if G1.has_edge(u1, u2) != G2.has_edge(v1, v2):
                F.add_clause([(False, var(u1, v1)),
                              (False, var(u2, v2))], strict=True)
                F.add_clause([(False, var(u1, v2)),
                              (False, var(u2, v1))], strict=True)

    return F

@register_cnf_generator
def GraphAutomorphism(G):
    """Graph Automorphism formula

    The formula is the CNF encoding of the statement that a graph G
    has a nontrivial automorphism, i.e. an automorphism different from
    the idential one.

    Parameter
    ---------
    G : a simple graph

    Returns
    -------
    A CNF formula which is satiafiable if and only if graph G has a
    nontrivial automorphism.
    """
    tmp = CNF()
    header = "Graph automorphism formula for graph "+ G.name +"\n"+ tmp.header
    F = GraphIsomorphism(G, G)
    F.header = header

    var = _graph_isomorphism_var

    F.add_clause([(False, var(u, u)) for u in enumerate_vertices(G)], strict=True)

    return F



@register_cnfgen_subcommand
class GAutoCmdHelper(object):
    """Command line helper for Graph Automorphism formula
    """
    name='gauto'
    description='graph automorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph automorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return GraphAutomorphism(G)



@register_cnfgen_subcommand
class GIsoCmdHelper(object):
    """Command line helper for Graph Isomorphism formula
    """
    name='giso'
    description='graph isomorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser,suffix="1",required=True)
        SimpleGraphHelper.setup_command_line(parser,suffix="2",required=True)


    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G1 = SimpleGraphHelper.obtain_graph(args,suffix="1")
        G2 = SimpleGraphHelper.obtain_graph(args,suffix="2")
        return GraphIsomorphism(G1,G2)


