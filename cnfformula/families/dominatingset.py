#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formulas that encode coloring related problems
"""


from cnfformula.cnf import CNF
from cnfformula.cnf import less_or_equal_constraint
from cnfformula.cmdline import SimpleGraphHelper

from cnfformula.cmdline  import register_cnfgen_subcommand
from cnfformula.families import register_cnf_generator

from itertools import combinations,product


@register_cnf_generator
def DominatingSet(G,d, alternative = False):
    r"""Generates the clauses for a dominating set for G of size <= d

    The formula encodes the fact that the graph :math:`G` has
    a dominating set of size :math:`d`. This means that it is possible
    to pick at most :math:`d` vertices in :math:`V(G)` so that all remaining
    vertices have distance at most one from the selected ones.

    Parameters
    ----------
    G : networkx.Graph
        a simple undirected graph
    d : a positive int
        the size limit for the dominating set
    alternative : bool
        use an alternative construction that 
        is provably hard from resolution proofs.

    Returns
    -------
    CNF
       the CNF encoding for dominating of size :math:`\leq d` for graph :math:`G`

    """
    F=CNF()

    if not isinstance(d,int) or d<1:
        ValueError("Parameter \"d\" is expected to be a positive integer")
    
    # Describe the formula
    name="{}-dominating set".format(d)
    
    if hasattr(G,'name'):
        F.header=name+" of graph:\n"+G.name+".\n\n"+F.header
    else:
        F.header=name+".\n\n"+F.header

    # Fix the vertex order
    V=sorted(G.nodes())
    

    def D(v):
        return "x_{{{0}}}".format(v)

    def M(v,i):
        return "g_{{{0},{1}}}".format(v,i)

    def N(v):
        return tuple(sorted([ v ] + [ u for u in G.neighbors(v) ]))
    
    # Create variables
    for v in V:
        F.add_variable(D(v))
    for i,v in product(range(1,d+1),V):
        F.add_variable(M(v,i))
    
    # No two (active) vertices map to the same index
    if alternative:
        for u,v in combinations(V,2):
            for i in range(1,d+1):
                F.add_clause( [ (False,D(u)),(False,D(v)), (False,M(u,i)), (False,M(v,i))    ])
    else:
        for i in range(1,d+1):
            for c in less_or_equal_constraint([M(v,i) for v in V],1):
                F.add_clause(c)
                
    # (Active) Vertices in the sequence are not repeated
    if alternative:
        for v in V:
            for i,j in combinations(range(1,d+1),2):
                F.add_clause([(False,D(v)),(False,M(v,i)),(False,M(v,j))])
    else:
        for i,j in combinations(range(1,d+1),2):
            i,j = min(i,j),max(i,j)
            for u,v in combinations(V,2):
                u,v = max(u,v),min(u,v)
                F.add_clause([(False,M(u,i)),(False,M(v,j))])

    # D(v) = M(v,1) or M(v,2) or ... or M(v,d)        
    if not alternative:
        for i,v in product(range(1,d+1),V):
            F.add_clause([(False,M(v,i)),(True,D(v))])
    for v in V:
        F.add_clause([(False,D(v))] + [(True,M(v,i)) for i in range(1,d+1)])
    
        
    # Every neighborhood must have a true D variable
    neighborhoods = sorted( set(N(v) for v in V) )
    for N in neighborhoods:
        F.add_clause([ (True,D(v)) for v in N])
        
    return F


@register_cnfgen_subcommand
class DominatingSetCmdHelper(object):
    """Command line helper for k-dominating set
    """
    name='dominating'
    description='k-Dominating set'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for dominating set formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('d',metavar='<d>',type=int,action='store',help="size of the dominating set")
        parser.add_argument('--alternative','-a',action='store_true',default=False,help="produce the provably hard version")
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build the k-dominating set formula

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return DominatingSet(G, args.d, alternative = args.alternative )



