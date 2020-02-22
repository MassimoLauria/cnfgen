#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some graph formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfformula import GraphColoringFormula
from cnfformula import EvenColoringFormula

from cnfformula import DominatingSet

from cnfformula import GraphIsomorphism
from cnfformula import GraphAutomorphism

from cnfformula import CliqueFormula
from cnfformula import BinaryCliqueFormula
from cnfformula import SubgraphFormula
from cnfformula import RamseyWitnessFormula

from .graph_cmdline import SimpleGraphHelper
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
                            metavar='<k>',
                            type=int,
                            action='store',
                            help="number of available colors")
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build a k-colorability formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return GraphColoringFormula(G, list(range(1, args.k + 1)))


class ECCmdHelper(FormulaHelper):
    name = 'ec'
    description = 'even coloring formulas'

    @staticmethod
    def setup_command_line(parser):
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        G = SimpleGraphHelper.obtain_graph(args)
        return EvenColoringFormula(G)


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
        parser.add_argument('d',
                            metavar='<d>',
                            type=int,
                            action='store',
                            help="size of the dominating set")
        parser.add_argument('--alternative',
                            '-a',
                            action='store_true',
                            default=False,
                            help="produce the provably hard version")
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the k-dominating set formula

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return DominatingSet(G, args.d, alternative=args.alternative)


class GAutoCmdHelper(FormulaHelper):
    """Command line helper for Graph Automorphism formula
    """
    name = 'gauto'
    description = 'graph automorphism formula'

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


class GIsoCmdHelper(FormulaHelper):
    """Command line helper for Graph Isomorphism formula
    """
    name = 'giso'
    description = 'graph isomorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser, suffix="1", required=True)
        SimpleGraphHelper.setup_command_line(parser, suffix="2", required=True)

    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G1 = SimpleGraphHelper.obtain_graph(args, suffix="1")
        G2 = SimpleGraphHelper.obtain_graph(args, suffix="2")
        return GraphIsomorphism(G1, G2)


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
                            metavar='<k>',
                            type=int,
                            action='store',
                            help="size of the clique to be found")
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return CliqueFormula(G, args.k)


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
                            metavar='<k>',
                            type=int,
                            action='store',
                            help="size of the clique to be found")
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return BinaryCliqueFormula(G, args.k)


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
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return RamseyWitnessFormula(G, args.k, args.s)


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
        SimpleGraphHelper.setup_command_line(parser, suffix="", required=True)
        SimpleGraphHelper.setup_command_line(parser, suffix="T", required=True)

    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args, suffix="")
        T = SimpleGraphHelper.obtain_graph(args, suffix="T")
        return SubgraphFormula(G, [T], symmetric=False)
