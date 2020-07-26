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
from .cmdline import positive_int, nonnegative_int

import argparse

usage_string = """Pigeonhole Principle

Pigeonhole principle claims that P pigeons can fly to H holes with no
two pigeons in the same hole. This is unsatisfiable when P > H. It is
possible to specify a bipartite graph that specifies which pigeons can
fly to which holes.

positional arguments:
 {0} N           --- N+1 pigeons fly to N holes
 {0} M N         --- M pigeons fly to N holes
 {0} M N D       --- M pigeons fly to N holes, pigeon left degree D
 """

example_string = """examples:
 {0} 100           --- 101 pigeons and 100 holes (unsat)
 {0} 14 10         --- 14 pigeons and 10 holes (unsat)
 {0} 9  10         --- 9  pigeons and 10 holes (sat)
 {0} 12 10 3       --- 12 pigeons and 10 holes,
 {1}                   pigeon can go to 3 random holes
 """


class PHPArgs(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        if len(values) == 0:
            parser.error('php formula needs <pigeons> <holes> specification')

        if len(values) > 3:
            parser.error('too many arguments for php formula')

        try:
            intvalues = [int(x) for x in values]
            if not all([x >= 0 for x in intvalues]):
                raise ValueError
        except ValueError:
            parser.error('php arguments must be positive integers')

        if len(intvalues) == 1:
            setattr(args, "pigeons", intvalues[0] + 1)
            setattr(args, "holes", intvalues[0])
            setattr(args, "degree", intvalues[0])
        elif len(intvalues) == 2:
            setattr(args, "pigeons", intvalues[0])
            setattr(args, "holes", intvalues[1])
            setattr(args, "degree", intvalues[1])
        else:
            setattr(args, "pigeons", intvalues[0])
            setattr(args, "holes", intvalues[1])
            setattr(args, "degree", intvalues[2])

            if intvalues[1] < intvalues[2]:
                parser.error("degree must be at most the number of holes")


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
        parser.usage = usage_string.format(parser.prog)
        parser.description = example_string.format(parser.prog,
                                                   " " * len(parser.prog))
        parser.add_argument('pigeonholes',
                            action=PHPArgs,
                            nargs='*',
                            help=argparse.SUPPRESS)
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
        if args.holes == args.degree:
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
                            type=positive_int,
                            help="Number of pigeons")
        parser.add_argument('holes',
                            metavar='<holes>',
                            type=positive_int,
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
                            type=nonnegative_int,
                            help="Number of vertices")
        parser.add_argument('k',
                            metavar='<k>',
                            type=positive_int,
                            help="Clique size")
        parser.add_argument('c',
                            metavar='<c>',
                            type=positive_int,
                            help="Coloring size")

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
                            type=positive_int,
                            help="Forbidden independent set size")
        parser.add_argument('k',
                            metavar='<k>',
                            type=positive_int,
                            help="Forbidden independent clique")
        parser.add_argument('N',
                            metavar='<N>',
                            type=nonnegative_int,
                            help="Graph size")

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
                            type=nonnegative_int,
                            help="Size of the domain")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PythagoreanTriples(args.N)
