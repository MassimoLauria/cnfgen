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

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Thapen's size-width tradeoff formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} [-h|--help] <a> <b> <c>".format(parser.prog)
        parser.description = """ The formula is a propositional version of the coloured polynomial
    local search principle (CPLS). A description can be found in [1].
    The difference with the formula in the paper is that here unary
    indices start from 1 instead of 0. Binary strings still counts
    from 0, therefore the mappings f[i](x)=x is actually represented
    in binary with the binary representation of x-1.

    [1] N. Thapen (2016) Trade-offs between length and width in resolution.

positional arguments:
  <a>                     number of levels
  <b>                     number of nodes per level (must be a power of two)
  <c>                     number of colours (must be a power of two)

optional arguments:
  --help, -h            show this help message and exit
"""

        parser.add_argument('a', type=positive_int)
        parser.add_argument('b', type=positive_int)
        parser.add_argument('c', type=positive_int)

    @staticmethod
    def build_formula(args):
        """Build Thapen's size-width tradeoff formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CPLSFormula(args.a, args.b, args.c)
