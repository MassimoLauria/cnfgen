#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some graph formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020, 2021, 2022 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

import sys

from cnfgen.families.pebbling import PebblingFormula
from cnfgen.families.pebbling import StoneFormula
from cnfgen.families.pebbling import SparseStoneFormula

from cnfgen.graphs import bipartite_random_left_regular

from cnfgen.clitools import ObtainDirectedAcyclicGraph, make_graph_doc
from cnfgen.clitools import ObtainBipartiteGraph
from cnfgen.clitools import positive_int

from .formula_helpers import FormulaHelper


class PebblingCmdHelper(FormulaHelper):
    """Command line helper for pebbling formulas
    """
    name = 'peb'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """

        parser.usage = "usage:\n {} [-h|--help] <dag>".format(parser.prog)

        parser.description = """The Pebbling Formula is defined on a directed acyclic graph <dag>
and claims that (1) each source vertex of <dag> (i.e. with no
predecessors) has a pebble on it; (2) if all predecessors of a vertex
are pebbled, the vertex is pebbled too; (3) the sink is not pebbled.
This is clearly unsatisfiable.

positional arguments:
  <stones>            number of stones
  <dag>               a directed acyclic graph (see \'cnfgen --help-dag\')

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('D', action=ObtainDirectedAcyclicGraph)

    @staticmethod
    def build_formula(args, formula_class):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        return PebblingFormula(args.D)


class StoneCmdHelper(FormulaHelper):
    """Command line helper for stone formulas
    """
    name = 'stone'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:
 {} [-h|--help] <stones> <dag> [--sparse <degree>]""".format(parser.prog)

        parser.description = """A Stones formula claims that each vertex of a directed acyclic
graph <dag> is associated with one among <stones> stones.
Each stone can be either red or blue, and not both. The clauses of
the formula encode the following constraints. (1) if a stone is on
a vertex with no incoming edges, then it must be red. (2) if all
stones on the predecessors of a vertex are red, then the stone of
the vertex itself must be red. (3) the formula furthermore
enforces that the stones on the sinks (i.e. vertices with no
outgoing edges) are blue.

In the sparse variant of the Stone Formula each vertex has only
<degree> choices of stones to which it can be associated. This avoid
large clauses in the formula.

positional arguments:
  <stones>            number of stones
  <dag>               a directed acyclic graph (see \'cnfgen --help-dag\')

optional arguments:
  --sparse <degree>   each vertex can only choose among <degree> many stones
  --help, -h          show this help message and exit
"""
        parser.add_argument('s', type=positive_int)
        parser.add_argument('D', action=ObtainDirectedAcyclicGraph)
        parser.add_argument('--sparse', metavar='<degree>', type=positive_int)

    @staticmethod
    def build_formula(args, formula_class):
        """Build the stone formula

        Arguments:
        - `args`: command line options
        """
        D = args.D
        if hasattr(args, 'sparse') and args.sparse is not None:
            degree = args.sparse
            nvertices = D.order()
            nstones = args.s
            if degree > nstones:
                raise ValueError("It must hold that <degree> <= <stones>")
            B = bipartite_random_left_regular(nvertices, nstones, degree)
            return SparseStoneFormula(D, B)
        else:
            return StoneFormula(D, args.s)
