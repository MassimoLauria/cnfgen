#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Thapen's size-width tradeoff formula
"""

from cnfgen.families.cpls import CPLSFormula

from cnfgen.clitools import positive_int
from .formula_helpers import FormulaHelper


class CPLSCmdHelper(FormulaHelper):
    """Command line helper for Thapen's size-width tradeoff formula"""

    name = 'cpls'
    description = 'Thapen\'s Coloured Polynomial Local Search formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Thapen's size-width tradeoff formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('a',
                            metavar='<a>',
                            type=positive_int,
                            help="Number of levels")
        parser.add_argument(
            'b',
            metavar='<b>',
            type=positive_int,
            help=
            "Number of nodes per level in the graph (must be a power of two)")
        parser.add_argument('c',
                            metavar='<c>',
                            type=int,
                            help="Number of colours (must be a power of two)")

    @staticmethod
    def build_cnf(args):
        """Build Thapen's size-width tradeoff formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CPLSFormula(args.a, args.b, args.c)
