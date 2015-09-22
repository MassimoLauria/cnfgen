#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of formulas that check for subgraphs
"""

from cnfformula.cnf import CNF
from cnfformula.cmdline import SimpleGraphHelper

import cnfformula.families
import cnfformula.cmdline

from itertools import combinations
from itertools import product
from itertools import combinations_with_replacement

from networkx  import complete_graph
from networkx  import empty_graph

from textwrap import dedent

@cnfformula.families.register_cnf_generator
def SubgraphFormula(graph,templates):
    """Test whether a graph contains one of the templates.

    Given a graph :math:`G` and a sequence of template graphs
    :math:`H_1`, :math:`H_2`, ..., :math:`H_t`, the CNF formula claims
    that :math:`G` contains an isomorphic copy of at least one of the
    template graphs.

    E.g. when :math:`H_1` is the complete graph of :math:`k` vertices
    and it is the only template, the formula claims that :math:`G`
    contains a :math:`k`-clique.

    Parameters
    ----------
    graph : networkx.Graph
        a simple graph
    templates : list-like object
        a sequence of graphs.

    Returns
    -------
    a CNF object
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

    for s in selectors:
        F.add_variable(s)
        
    if len(selectors)>1:

        # Exactly one of the graphs must be selected as subgraph
        F.add_clause([(True,v) for v in selectors],strict=True)

        for (a,b) in combinations(selectors):
            F.add_clause( [ (False,a), (False,b) ], strict=True )

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
        F.add_clause([(True,"S_{{{0}}}{{{1}}}".format(i,j)) for j in range(N)],strict=True)

    # ...and exactly one
    for i,(a,b) in product(range(k),combinations(range(N),2)):
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(i,a)),
                      (False,"S_{{{0}}}{{{1}}}".format(i,b))  ], strict = True)

 
    # Mapping is strictly monotone increasing (so it is also injective)
    localmaps = product(combinations(range(k),2),
                        combinations_with_replacement(range(N),2))

    for (a,b),(i,j) in localmaps:
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(min(a,b),max(i,j))),
                      (False,"S_{{{0}}}{{{1}}}".format(max(a,b),min(i,j)))  ],strict=True)


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
                          (False,"S_{{{0}}}{{{1}}}".format(max(i1,i2),max(j1,j2))) ],strict=True)

    return F



@cnfformula.families.register_cnf_generator
def CliqueFormula(G,k):
    """Test whether a graph contains one of the templates.

    Given a graph :math:`G` and a non negative value :math:`k`, the
    CNF formula claims that :math:`G` contains a :math:`k`-clique.

    Parameters
    ----------
    G : networkx.Graph
        a simple graph
    k : a non negative integer
        clique size

    Returns
    -------
    a CNF object

    """
    return SubgraphFormula(G,[complete_graph(k)])

@cnfformula.families.register_cnf_generator
def RamseyWitnessFormula(G,k,s):
    """Test whether a graph contains one of the templates.

    Given a graph :math:`G` and a non negative values :math:`k` and
    :math:`s`, the CNF formula claims that :math:`G` contains
    a neither a :math:`k`-clique nor an independet set of size
    :math:`s`.

    Parameters
    ----------
    G : networkx.Graph
        a simple graph
    k : a non negative integer
        clique size
    s : a non negative integer
        independet set size

    Returns
    -------
    a CNF object

    """
    return SubgraphFormula(G,[complete_graph(k),empty_graph(s)])


@cnfformula.cmdline.register_cnfgen_subcommand
class KCliqueCmdHelper(object):
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
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return CliqueFormula(G,args.k)


@cnfformula.cmdline.register_cnfgen_subcommand
class RWCmdHelper(object):
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
        parser.add_argument('k',metavar='<k>',type=int,
                            action='store',help="size of the clique to be found")
        parser.add_argument('s',metavar='<s>',type=int,
                            action='store',help="size of the stable to be found")
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[complete_graph(args.k),
                                  empty_graph(args.s)])

