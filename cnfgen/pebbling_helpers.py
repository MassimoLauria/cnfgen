#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some graph formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

import sys

from cnfformula import PebblingFormula
from cnfformula import StoneFormula
from cnfformula import SparseStoneFormula

from .graph_cmdline import DirectedAcyclicGraphHelper
from .graph_cmdline import BipartiteGraphHelper

from .formula_helpers import FormulaHelper


class PebblingCmdHelper(FormulaHelper):
    """Command line helper for pebbling formulas
    """
    name='peb'
    description='pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        try:
            return PebblingFormula(D)
        except ValueError as e:
            print("\nError: {}".format(e),file=sys.stderr)
            sys.exit(-1)

class StoneCmdHelper(FormulaHelper):
    """Command line helper for stone formulas
    """
    name='stone'
    description='stone formula'
    __doc__ = StoneFormula.__doc__
    
    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)
        parser.add_argument('s',metavar='<s>',type=int,help="number of stones")

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        try:
            return StoneFormula(D,args.s)
        except ValueError as e:
            print("\nError: {}".format(e),file=sys.stderr)
            sys.exit(-1)

class SparseStoneCmdHelper(FormulaHelper):
    """Command line helper for stone formulas
    """
    name='stonesparse'
    description='stone formula (sparse version)'
    __doc__ = SparseStoneFormula.__doc__
    
    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)
        BipartiteGraphHelper.setup_command_line(parser,suffix="_mapping")

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        B= BipartiteGraphHelper.obtain_graph(args,suffix="_mapping")
        try:
            return SparseStoneFormula(D,B)
        except ValueError as e:
            print("\nError: {}".format(e),file=sys.stderr)
            sys.exit(-1)

