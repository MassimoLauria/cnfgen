#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for pigeonhole principle formulas

Copyright (C) 2012-2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfformula import CliqueColoring
from cnfformula import RamseyLowerBoundFormula
from cnfformula import PythagoreanTriples

from cnfformula import PigeonholePrinciple
from cnfformula import GraphPigeonholePrinciple
from cnfformula import BinaryPigeonholePrinciple

from cnfformula.graphs import bipartite_random_left_regular

from .graph_cmdline import BipartiteGraphHelper
from .formula_helpers import FormulaHelper


class PHPCmdHelper(FormulaHelper):
    """Command line helper for the Pigeonhole principle CNF"""

    name = 'php'
    description = 'pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('pigeons',
                            metavar='<pigeons>',
                            type=int,
                            help="Number of pigeons")
        parser.add_argument('holes',
                            metavar='<holes>',
                            type=int,
                            default=None,
                            nargs='?',
                            help="Number of holes (default: pigeons-1 )")
        parser.add_argument('degree',
                            metavar='<degree>',
                            type=int,
                            default=None,
                            nargs='?',
                            help="Left degree of pigeons (default: holes)")
        parser.add_argument('--functional',
                            action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',
                            action='store_true',
                            help="every hole has a sitting pigeon")

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        if args.holes is None:
            args.holes = args.pigeons - 1
        if args.degree is None:
            return PigeonholePrinciple(args.pigeons,
                                       args.holes,
                                       functional=args.functional,
                                       onto=args.onto)
        else:
            G = bipartite_random_left_regular(args.pigeons, args.holes,
                                              args.degree)
            return GraphPigeonholePrinciple(G,
                                            functional=args.functional,
                                            onto=args.onto)


class GPHPCmdHelper(FormulaHelper):
    """Command line helper for the Pigeonhole principle on graphs"""

    name = 'gphp'
    description = 'graph pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula over graphs

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--functional',
                            action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',
                            action='store_true',
                            help="every hole has a sitting pigeon")
        BipartiteGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build a Graph PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = BipartiteGraphHelper.obtain_graph(args)
        return GraphPigeonholePrinciple(G,
                                        functional=args.functional,
                                        onto=args.onto)


class BPHPCmdHelper(FormulaHelper):
    """Command line helper for the Pigeonhole principle CNF"""

    name = 'bphp'
    description = 'binary pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('pigeons',
                            metavar='<pigeons>',
                            type=int,
                            help="Number of pigeons")
        parser.add_argument('holes',
                            metavar='<holes>',
                            type=int,
                            help="Number of holes")

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return BinaryPigeonholePrinciple(args.pigeons, args.holes)


class CliqueColoringCmdHelper(FormulaHelper):
    """Command line helper for the Clique-coclique CNF"""

    name = 'cliquecoloring'
    description = 'There is a graph G with a k-clique and a c-coloring'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for clique-coloring formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('n',
                            metavar='<n>',
                            type=int,
                            help="Number of vertices")
        parser.add_argument('k', metavar='<k>', type=int, help="Clique size")
        parser.add_argument('c', metavar='<c>', type=int, help="Coloring size")

    @staticmethod
    def build_cnf(args):
        """Build a Clique-coclique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CliqueColoring(args.n, args.k, args.c)


class RamseyCmdHelper(FormulaHelper):
    """Command line helper for RamseyNumber formulas
    """
    name = 'ram'
    description = 'ramsey number principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('s',
                            metavar='<s>',
                            type=int,
                            help="Forbidden independent set size")
        parser.add_argument('k',
                            metavar='<k>',
                            type=int,
                            help="Forbidden independent clique")
        parser.add_argument('N', metavar='<N>', type=int, help="Graph size")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RamseyLowerBoundFormula(args.s, args.k, args.N)


class PTNCmdHelper(FormulaHelper):
    """Command line helper for PTN formulas
    """
    name = 'ptn'
    description = 'Bicoloring of N with no monochromatic Pythagorean Triples'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for PTN formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',
                            metavar='<N>',
                            type=int,
                            help="Size of the domain")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PythagoreanTriples(args.N)
