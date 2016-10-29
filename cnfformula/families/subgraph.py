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
from itertools import permutations
from cnfformula.graphs import enumerate_vertices

from math import log,ceil

from networkx  import complete_graph
from networkx  import empty_graph

from textwrap import dedent

@cnfformula.families.register_cnf_generator
def SubgraphFormula(graph,templates, symmetric=False):
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

    symmetric:
        all template graphs are symmetric wrt permutations of
        vertices. This allows some optimization in the search space of
        the assignments.

    induce: 
        force the subgraph to be induced (i.e. no additional edges are allowed)


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
        for cls in F.equal_to_constraint(selectors,1):
            F.add_clause( cls , strict=True )

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

    var_name = lambda i,j: "S_{{{0},{1}}}".format(i,j)

    if symmetric:
        mapping = F.unary_mapping(range(k),range(N),var_name=var_name,
                                  functional=True,injective=True,
                                  nondecreasing=True)
    else:
        mapping = F.unary_mapping(range(k),range(N),var_name=var_name,
                                  functional=True,injective=True,
                                  nondecreasing=False)

    for v in mapping.variables():
        F.add_variable( v )

    for cls in mapping.clauses():
        F.add_clause( cls, strict=True )
        
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
    gV = enumerate_vertices(graph)

    for i in range(len(templates)):

        k  = templates[i].order()
        tV = enumerate_vertices(templates[i])

        if symmetric:
            # Using non-decreasing map to represent a subset
            localmaps = product(combinations(range(k),2),
                                combinations(range(N),2))
        else:
            localmaps = product(combinations(range(k),2),
                                permutations(range(N),2))
       

        for (i1,i2),(j1,j2) in localmaps:

            # check if this mapping is compatible
            tedge=templates[i].has_edge(tV[i1],tV[i2])
            gedge=graph.has_edge(gV[j1],gV[j2])
            if tedge == gedge:
                continue

            # if it is not, add the corresponding
            F.add_clause(activation_prefixes[i] + \
                         [(False,var_name(i1,j1)),
                          (False,var_name(i2,j2)) ],strict=True)

    return F



@cnfformula.families.register_cnf_generator
def CliqueFormula(G,k):
    """Test whether a graph has a k-clique.

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
    return SubgraphFormula(G,[complete_graph(k)],symmetric=True)


@cnfformula.families.register_cnf_generator
def BinaryCliqueFormula(G,k):
    """Test whether a graph has a k-clique.

    Given a graph :math:`G` and a non negative value :math:`k`, the
    CNF formula claims that :math:`G` contains a :math:`k`-clique.
    This formula uses the binary encoding, in the sense that the
    clique elements are indexed by strings of bits.

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
    F=CNF()
    F.header="Binary {0}-clique formula\n".format(k) + F.header
    
    clauses_gen=F.binary_mapping(xrange(1,k+1), G.nodes(),
                                 injective = True,
                                 nondecreasing = True)

    for v in clauses_gen.variables():
        F.add_variable(v)
        
    for c in clauses_gen.clauses():
        F.add_clause(c,strict=True)

    for (i1,i2),(v1,v2) in product(combinations(xrange(1,k+1),2),
                                   combinations(G.nodes(),2)):
    
        if not G.has_edge(v1,v2):
            F.add_clause( clauses_gen.forbid_image(i1,v1) + clauses_gen.forbid_image(i2,v2),strict=True)

    return F


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
    return SubgraphFormula(G,[complete_graph(k),empty_graph(s)],symmetric=True)


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
class BinaryKCliqueCmdHelper(object):
    """Command line helper for k-clique formula
    """
    name='kcliquebin'
    description='Binary k clique formula'

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
        return BinaryCliqueFormula(G,args.k)

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
        return RamseyWitnessFormula(G,args.k,args.s)

@cnfformula.cmdline.register_cnfgen_subcommand
class SubGraphCmdHelper(object):
    """Command line helper for Graph Isomorphism formula
    """
    name='subgraph'
    description='subgraph formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser,suffix="",required=True)
        SimpleGraphHelper.setup_command_line(parser,suffix="T",required=True)


    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args,suffix="")
        T = SimpleGraphHelper.obtain_graph(args,suffix="T")
        return SubgraphFormula(G,[T],symmetric=False)


