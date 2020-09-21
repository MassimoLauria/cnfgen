#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some graph formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

import sys

from cnfgen.families.pebbling import PebblingFormula
from cnfgen.families.pebbling import StoneFormula
from cnfgen.families.pebbling import SparseStoneFormula

from cnfgen.graphs import bipartite_sets

from cnfgen.clitools import ObtainDirectedAcyclicGraph, make_graph_doc
from cnfgen.clitools import ObtainBipartiteGraph
from cnfgen.clitools import positive_int

from .formula_helpers import FormulaHelper


class PebblingCmdHelper(FormulaHelper):
    """Command line helper for pebbling formulas
    """
    name = 'peb'
    description = 'pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """

        parser.epilog = "Parameter <dag>:" + make_graph_doc('dag', parser.prog)

        parser.add_argument(
            'D',
            metavar='<dag>',
            action=ObtainDirectedAcyclicGraph,
            help='directed acyclic graph (either a file or graph specification)'
        )

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        return PebblingFormula(args.D)


class StoneCmdHelper(FormulaHelper):
    """Command line helper for stone formulas
    """
    name = 'stone'
    description = 'stone formula (dense and sparse)'
    __doc__ = StoneFormula.__doc__

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        usage_string = "{} [-h] <stones> <dag> [--sparse <mapping>]"
        parser.usage = usage_string.format(parser.prog)

        parser.epilog = "Parameter <dag>:" + make_graph_doc('dag', parser.prog)

        parser.epilog += "\n\n"
        parser.epilog += "Parameter <mapping>:" + make_graph_doc(
            'bipartite', parser.prog)

        parser.add_argument('s',
                            metavar='<stones>',
                            type=positive_int,
                            help="number of stones")
        parser.add_argument(
            'D',
            metavar='<dag>',
            action=ObtainDirectedAcyclicGraph,
            help='directed acyclic graph (either a file or graph specification)'
        )
        parser.add_argument(
            '--sparse',
            metavar='<mapping>',
            action=ObtainBipartiteGraph,
            help="mapping between vertices and stones (i.e. a bipartite graph)"
        )

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D = args.D
        if hasattr(args, 'sparse') and args.sparse is not None:
            B = args.sparse
            Left, Right = bipartite_sets(B)
            nvertices = D.order()
            nstones = args.s
            if (len(Left), len(Right)) != (nvertices, nstones):
                raise ValueError(
                    "Size of left and right sides must match #vertices in DAG and #stones, respectively."
                )
            return SparseStoneFormula(D, B)

        else:
            return StoneFormula(D, args.s)
