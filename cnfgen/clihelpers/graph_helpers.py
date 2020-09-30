#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some graph formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""
import argparse

from cnfgen.families.coloring import GraphColoringFormula
from cnfgen.families.coloring import EvenColoringFormula

from cnfgen.families.dominatingset import DominatingSet
from cnfgen.families.dominatingset import Tiling

from cnfgen.families.graphisomorphism import GraphIsomorphism
from cnfgen.families.graphisomorphism import GraphAutomorphism

from cnfgen.families.subgraph import CliqueFormula
from cnfgen.families.subgraph import BinaryCliqueFormula
from cnfgen.families.subgraph import SubgraphFormula
from cnfgen.families.subgraph import RamseyWitnessFormula

from cnfgen.clitools import ObtainSimpleGraph, positive_int, make_graph_doc
from .formula_helpers import FormulaHelper


class KColorCmdHelper(FormulaHelper):
    """Command line helper for k-color formula
    """
    name = 'kcolor'
    description = 'k-colorability formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-color formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',
                            type=positive_int,
                            action='store',
                            help="number of available colors")
        parser.add_argument(
            'G',
            help='simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        """Build a k-colorability formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return GraphColoringFormula(args.G, list(range(1, args.k + 1)))


class ECCmdHelper(FormulaHelper):
    name = 'ec'
    description = 'even coloring formulas'

    @staticmethod
    def setup_command_line(parser):

        parser.add_argument(
            'G',
            help='simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        return EvenColoringFormula(args.G)


class DominatingSetCmdHelper(FormulaHelper):
    """Command line helper for k-dominating set
    """
    name = 'domset'
    description = 'k-Dominating set'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for dominating set formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--alternative',
                            '-a',
                            action='store_true',
                            default=False,
                            help="produce the provably hard version")
        parser.add_argument('d',
                            type=int,
                            action='store',
                            help="size of the dominating set")
        parser.add_argument(
            'G',
            help='simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        """Build the k-dominating set formula

        Arguments:
        - `args`: command line options
        """
        return DominatingSet(args.G, args.d, alternative=args.alternative)


class TilingCmdHelper(FormulaHelper):
    """Command line helper for tiling
    """
    name = 'tiling'
    description = 'tiling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for tiling formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument(
            'G',
            help='simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        """Build the tiling formula

        Arguments:
        - `args`: command line options
        """
        return Tiling(args.G)


iso_description = """The formula takes one or two graphs as input.

 {0} G1           --- test if G1 has nontrivial automorphisms
 {0} G1 -e G2     --- test if G1 and G2 are isomorphic

examples:
 {0} grid 3 3
 {0} complete 4 -e empty 4 plantclique 4
 {0} first.gml -e second.gml
 {0} gnm 10 5
"""


class GIsoCmdHelper(FormulaHelper):
    """Command line helper for Graph Isomorphism formula
    """
    name = 'iso'
    description = 'graph isomorphism/automorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = '{} [-h] G1 [-e G2]'.format(parser.prog)
        parser.description = iso_description.format(parser.prog)

        parser.add_argument(
            'G1',
            help='a simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)
        parser.add_argument(
            '-e',
            metavar='G2',
            action=ObtainSimpleGraph,
            help='another simple undirected graph (see \'cnfgen --help-graph\')'
        )

    @staticmethod
    def build_cnf(args):
        G = args.G
        if hasattr(args, 'equiv'):
            G2 = args.equiv
            return GraphIsomorphism(G, G2)
        else:
            return GraphAutomorphism(G)


class KCliqueCmdHelper(FormulaHelper):
    """Command line helper for k-clique formula
    """
    name = 'kclique'
    description = 'k clique formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',
                            type=int,
                            action='store',
                            help="size of the clique to be found")
        parser.add_argument(
            'G',
            help='a simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CliqueFormula(args.G, args.k)


class BinaryKCliqueCmdHelper(FormulaHelper):
    """Command line helper for k-clique formula
    """
    name = 'kcliquebin'
    description = 'Binary k clique formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula

        Arguments:
        - `parser`: parser to load with options.
        """

        parser.add_argument('k',
                            type=int,
                            action='store',
                            help="size of the clique to be found")
        parser.add_argument(
            'G',
            help='a simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return BinaryCliqueFormula(args.G, args.k)


class RWCmdHelper(FormulaHelper):
    """Command line helper for ramsey graph formula
    """
    name = 'ramlb'
    description = 'unsat if G witnesses that r(k,s)>|V(G)| (i.e. G has not k-clique nor s-stable)'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for ramsey witness formula

        Arguments:
        - `parser`: parser to load with options.
        """

        parser.add_argument('k',
                            metavar='<k>',
                            type=int,
                            action='store',
                            help="size of the clique to be found")
        parser.add_argument('s',
                            metavar='<s>',
                            type=int,
                            action='store',
                            help="size of the stable to be found")
        parser.add_argument(
            'G',
            help='a simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        return RamseyWitnessFormula(args.G, args.k, args.s)


subgraph_description = """The formula takes two graphs: a main <graph> 
and a candidate <subgraph>, and claims that
the latter is indeed a subgraph of the former.

positional arguments:
 -G <graph>      --- main graph         (see \'cnfgen --help-graph\')
 -H <subgraph>   --- candidate subgraph (see \'cnfgen --help-graph\')

examples:
 {0} -G grid 4 4 -H grid 2 2
 {0} -G gnd 10 4 -H complete 5  (decides whether there is a 5-clique)
 {0} -G large.gml -H small.dot
"""


class SubGraphCmdHelper(FormulaHelper):
    """Command line helper for Graph Isomorphism formula
    """
    name = 'subgraph'
    description = 'subgraph formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = '{} [-h] -G <graph> -H <subgraph>'.format(parser.prog)
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
    def build_cnf(args):
        """Build a subgraph formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return SubgraphFormula(args.G, [args.H], symmetric=False)
