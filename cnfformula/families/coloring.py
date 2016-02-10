#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formulas that encode coloring related problems
"""


from cnfformula.cnf import CNF
from cnfformula.cnf import equal_to_constraint
from cnfformula.cmdline import SimpleGraphHelper

from cnfformula.cmdline  import register_cnfgen_subcommand
from cnfformula.families import register_cnf_generator

from itertools import combinations
import collections


@register_cnf_generator
def GraphColoringFormula(G,colors,functional=True):
    """Generates the clauses for colorability formula

    The formula encodes the fact that the graph :math:`G` has a coloring
    with color set ``colors``. This means that it is possible to
    assign one among the elements in ``colors``to that each vertex of
    the graph such that no two adjacent vertices get the same color.

    Parameters
    ----------
    G : networkx.Graph
        a simple undirected graph
    colors : list or positive int
        a list of colors or a number of colors

    Returns
    -------
    CNF
       the CNF encoding of the coloring problem on graph ``G``

    """
    col=CNF()

    if isinstance(colors,int) and colors>=0:
        colors = range(1,colors+1)
    
    if not isinstance(list, collections.Iterable):
        ValueError("Parameter \"colors\" is expected to be a iterable")
    
    # Describe the formula
    name="graph colorability"
    
    if hasattr(G,'name'):
        col.header=name+" of graph:\n"+G.name+".\n\n"+col.header
    else:
        col.header=name+".\n\n"+col.header

    # Fix the vertex order
    V=G.nodes()

    # Each vertex has a color
    for vertex in V:
        clause = []
        for color in colors:
            clause += [(True,'x_{{{0},{1}}}'.format(vertex,color))]
        col.add_clause(clause)
        
        # unique color per vertex
        if functional:
            for (c1,c2) in combinations(colors,2):
                col.add_clause([
                    (False,'x_{{{0},{1}}}'.format(vertex,c1)),
                    (False,'x_{{{0},{1}}}'.format(vertex,c2))],strict=True)

    # This is a legal coloring
    for (v1,v2) in G.edges():
        for c in colors:
            col.add_clause([
                (False,'x_{{{0},{1}}}'.format(v1,c)),
                (False,'x_{{{0},{1}}}'.format(v2,c))],strict=True)
            
    return col



@register_cnf_generator
def EvenColoringFormula(G):
    """Even coloring formula

    The formula is defined on a graph :math:`G` and claims that it is
    possible to split the edges of the graph in two parts, so that
    each vertex has an equal number of incident edges in each part.

    The formula is defined on graphs where all vertices have even
    degree. The formula is satisfiable only on those graphs with an
    even number of vertices in each connected component [1]_.

    Arguments
    ---------
    G : networkx.Graph 
       a simple undirected graph where all vertices have even degree

    Raises
    ------
    ValueError
       if the graph in input has a vertex with odd degree

    Returns
    -------
    CNF object

    References
    ----------
    .. [1] Locality and Hard SAT-instances, Klas Markstrom
       Journal on Satisfiability, Boolean Modeling and Computation 2 (2006) 221-228

    """
    F = CNF()
    F.header = "Even coloring formula on graph " + G.name + "\n" + F.header

    def var_name(u,v):
        if u<=v:
            return 'x_{{{0},{1}}}'.format(u,v)
        else:
            return 'x_{{{0},{1}}}'.format(v,u)
    
    for (u, v) in G.edges():
        F.add_variable(var_name(u, v))

    # Defined on both side
    for v in G.nodes():

        if G.degree(v) % 2 == 1:
            raise ValueError("Markstrom formulas requires all vertices to have even degree.")

        edge_vars = [ var_name(*e) for e in G.edges(v) ]
        
        for cls in equal_to_constraint(edge_vars,
                                       len(edge_vars)/2):
            F.add_clause(cls,strict=True)

    return F


@register_cnfgen_subcommand
class KColorCmdHelper(object):
    """Command line helper for k-color formula
    """
    name='kcolor'
    description='k-colorability formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-color formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="number of available colors")
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-colorability formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return GraphColoringFormula(G,range(1,args.k+1))



@register_cnfgen_subcommand
class ECCmdHelper(object):
    name='ec'
    description='even coloring formulas'

    @staticmethod
    def setup_command_line(parser):
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        G = SimpleGraphHelper.obtain_graph(args) 
        return EvenColoringFormula(G)
