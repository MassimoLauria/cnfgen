#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some graph formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020, 2021, 2022 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""
import argparse

from cnfgen.families.coloring import GraphColoringFormula
from cnfgen.families.coloring import EvenColoringFormula

from cnfgen.families.dominatingset import DominatingSet
from cnfgen.families.dominatingset import Tiling

from cnfgen.families.graphisomorphism import GraphIsomorphism
from cnfgen.families.graphisomorphism import GraphAutomorphism

from cnfgen.families.subgraph import SubgraphFormula
from cnfgen.families.subgraph import CliqueFormula
from cnfgen.families.subgraph import BinaryCliqueFormula
from cnfgen.families.subgraph import RamseyWitnessFormula

from cnfgen.clitools import ObtainSimpleGraph, positive_int, nonnegative_int, make_graph_doc
from cnfgen.clihelpers.formula_helpers import FormulaHelper


class KColorCmdHelper(FormulaHelper):
    """Command line helper for k-color formula
    """
    name = 'kcolor'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-color formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} [-h|--help] k G".format(parser.prog)

        parser.description = """The formula encodes the fact that the graph G has a k-coloring.
This means that it is possible to assign one among the k colors to
that each vertex of the graph such that no two adjacent vertices get
the same color.

positional arguments:
  k                       number of available colors
  G                       a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h              show this help message and exit
"""

        parser.add_argument('k', type=positive_int, action='store')
        parser.add_argument('G', action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args):
        """Build a k-colorability formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return GraphColoringFormula(args.G, args.k)


class ECCmdHelper(FormulaHelper):
    name = 'ec'

    @staticmethod
    def setup_command_line(parser):

        parser.usage = "usage:\n {0} [-h|--help] G".format(parser.prog)

        parser.description = """The formula is defined on a graph G and claims that it is possible
to split the edges of the graph in two parts, so that each vertex has
an equal number of incident edges in each part.

The formula is well defined as long as all vertices have even degree
(i.e. each connected component has an Eulerian circuit). The formula
is satisfiable if and only if there is an even number of edges in each
connected component (i.e. each such circuit has even length).
The formula originate from the paper 'Locality and Hard SAT-instances'
by Klas Markstrom (2006).

positional arguments:
  G                       a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h              show this help message and exit
"""
        parser.add_argument('G', action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args):
        return EvenColoringFormula(args.G)


class DominatingSetCmdHelper(FormulaHelper):
    """Command line helper for k-dominating set
    """
    name = 'domset'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for dominating set formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:
 {0} [-h|--help] [-a|--alternative] d G""".format(parser.prog)

        parser.description = """The formula encodes the fact that the graph G has a dominating set
of size d. This means that it is possible to pick at most d vertices
in G so that all remaining vertices have distance at most one
from them.

positional arguments:
  d                       size of the dominating set
  G                       a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h              show this help message and exit
  --alternative, -a       produces a provably hard version (default: false)
"""
        parser.add_argument('--alternative',
                            '-a',
                            action='store_true',
                            default=False)
        parser.add_argument('d',
                            type=positive_int,
                            action='store')
        parser.add_argument(
            'G', action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args):
        """Build the k-dominating set formula

        Arguments:
        - `args`: command line options
        """
        return DominatingSet(args.G, args.d, alternative=args.alternative)


class TilingCmdHelper(FormulaHelper):
    """Command line helper for tiling
    """
    name = 'tiling'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for tiling formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:\n {0} [-h|--help] G""".format(parser.prog)

        parser.description = """The formula encodes the fact that the graph G has a tiling.
This means that it is possible to pick a subset of vertices D so that
all vertices have distance at most one from exactly one verteix in D.

positional arguments:
  G                       a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h              show this help message and exit
"""
        parser.add_argument('G', action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args):
        """Build the tiling formula

        Arguments:
        - `args`: command line options
        """
        return Tiling(args.G)


iso_description = """The formula takes one or two graphs as input.

 {0} G1           --- test if G1 has nontrivial automorphisms
 {0} G1 -e G2     --- test if G1 and G2 are isomorphic

where G1 and G2 are simple graph (see 'cnfgen --help-graph')

examples:
 {0} grid 3 3
 {0} complete 4 -e empty 4 plantclique 4
 {0} first.gml -e second.gml
 {0} gnm 10 5

optiona arguments:
  --help, -h               show this help message and exit
"""


class GIsoCmdHelper(FormulaHelper):
    """Command line helper for Graph Isomorphism formula
    """
    name = 'iso'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = 'usage:\n {} [-h] G1 [-e G2]'.format(parser.prog)
        parser.description = iso_description.format(parser.prog)

        parser.add_argument('G',action=ObtainSimpleGraph)
        parser.add_argument('-e', metavar='G2',action=ObtainSimpleGraph)


    @staticmethod
    def build_formula(args):
        G = args.G
        if hasattr(args, 'G2'):
            G2 = args.G2
            return GraphIsomorphism(G, G2)
        else:
            return GraphAutomorphism(G)


class KCliqueCmdHelper(FormulaHelper):
    """Command line helper for k-clique formula
    """
    name = 'kclique'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula
        """
        parser.usage = "usage:\n {0} [-h|--help] k G".format(parser.prog)

        parser.description = """The formula is satiafiable if and only if graph G contains
a clique of size at least k, i.e. a set of k distinct vertices so that
every pair of them are connected by an edge.

positional arguments:
  k                       size of the clique to be found
  G                       a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h              show this help message and exit
  --no-symmetry-breaking  do not break symmetries by enforcing the
                          solution to be in increasing order (default: on)
"""

        parser.add_argument('k', type=nonnegative_int, action='store')
        parser.add_argument('G', action=ObtainSimpleGraph)
        parser.add_argument('--no-symmetry-breaking',
                            action='store_false',
                            default=True,
                            dest='symmetrybreaking')

    @staticmethod
    def build_formula(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CliqueFormula(args.G, args.k, args.symmetrybreaking)


class BinaryKCliqueCmdHelper(FormulaHelper):
    """Command line helper for k-clique formula
    """
    name = 'kcliquebin'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula

        Arguments:
        - `parser`: parser to load with options.
        """

        parser.usage = "usage:\n {0} [-h|--help] k G".format(parser.prog)

        parser.description = """The formula is satiafiable if and only if graph G contains a clique
of size at least k, i.e. a set of k distinct vertices so that every
pair of them are connected by an edge. The encoding is different from
the 'kclique' formula in the sense that every clique element is
indexed by a binary string of log(|V(G)|) variables.

positional arguments:
  k                       size of the clique to be found
  G                       a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h              show this help message and exit
"""

        parser.add_argument('k', type=nonnegative_int, action='store')
        parser.add_argument('G', action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return BinaryCliqueFormula(args.G, args.k)


class RWCmdHelper(FormulaHelper):
    """Command line helper for ramsey graph formula
    """
    name = 'ramlb'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for ramsey witness formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} [-h|--help] k s G".format(parser.prog)

        parser.description = """The formula is satiafiable when graph G contains either a clique of
size at least k, or an independent set of size s. Notice that any
graph with r(k,s) vertices or more must contain one or the other.
Therefore the formula is unsatifiable only for a graph G such that

  r(k,s) > |V(G)|.


positional arguments:
  k                       size of the clique to be found
  s                       size of the independent set to be found
  G                       a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h              show this help message and exit
"""

        parser.add_argument('k',
                            type=nonnegative_int,
                            action='store')
        parser.add_argument('s',
                            type=nonnegative_int,
                            action='store')
        parser.add_argument(
            'G',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        return RamseyWitnessFormula(args.G, args.k, args.s)


subgraph_description = """The formula takes two graphs: a main <graph>
and a candidate <subgraph>, and claims that
the latter is indeed a subgraph of the former.

examples:
 {0} -G grid 4 4 -H grid 2 2
 {0} -G gnd 10 4 -H complete 5  (decides whether there is a 5-clique)
 {0} -G large.gml -H small.dot

positional arguments:
 -G <graph>           main graph         (see \'cnfgen --help-graph\')
 -H <subgraph>        candidate subgraph (see \'cnfgen --help-graph\')

optional arguments:
 --help, -h           show this help message and exit
"""


class SubGraphCmdHelper(FormulaHelper):
    """Command line helper for Graph Isomorphism formula
    """
    name = 'subgraph'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = '{} [-h|--help] -G <graph> -H <subgraph>'.format(parser.prog)
        parser.description = subgraph_description.format(parser.prog)

        parser.add_argument('-G',
                            metavar='<graph>',
                            required=True,
                            help=argparse.SUPPRESS,
                            action=ObtainSimpleGraph)
        parser.add_argument('-H',
                            metavar='<subgraph>',
                            required=True,
                            help=argparse.SUPPRESS,
                            action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args):
        """Build a subgraph formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return SubgraphFormula(args.G, args.H, induced=False, symbreak=False)
