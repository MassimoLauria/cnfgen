#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of counting/matching formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020, 2021, 2022 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfgen.families.counting import CountingPrinciple
from cnfgen.families.counting import PerfectMatchingPrinciple
from cnfgen.families.tseitin import TseitinFormula
from cnfgen.families.subsetcardinality import SubsetCardinalityFormula

from cnfgen.clitools import ObtainSimpleGraph
from cnfgen.clitools import ObtainBipartiteGraph
from cnfgen.clitools import make_graph_from_spec, make_graph_doc

from cnfgen.clitools import CLIParser, compose_two_parsers
from cnfgen.clitools import positive_int, nonnegative_int

from .formula_helpers import FormulaHelper

import random
import argparse


class ParityCmdHelper(FormulaHelper):
    """Command line helper for Parity Principle formulas
    """
    name = 'parity'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Parity Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} N".format(parser.prog)
        parser.description = """The formula claims that a set of N elements can
be grouped in pairs. This is of course possible only if N is even.

positional arguments:
  N                       number of elements

optional arguments:
  --help, -h              show this help message and exit
"""
        parser.add_argument('N', type=nonnegative_int)

    @staticmethod
    def build_formula(args, formula_class):
        return CountingPrinciple(args.N, 2)


class PMatchingCmdHelper(FormulaHelper):
    """Command line helper for Perfect Matching Principle formulas
    """
    name = 'matching'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Perfect Matching Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} [-h|--help] G".format(parser.prog)
        parser.description = """The perfect matching principle claims that
a graph G has a perfect matching.

positional arguments:
  G                     a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h            show this help message and exit
"""
        parser.add_argument('G',action=ObtainSimpleGraph)

    @staticmethod
    def build_formula(args, formula_class):
        return PerfectMatchingPrinciple(args.G)


class CountingCmdHelper(FormulaHelper):
    """Command line helper for Counting Principle formulas
    """
    name = 'count'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Counting Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} [-h|--help] M p".format(parser.prog)
        parser.description = """The formula claims that a set of M elements can be partitioned in sets
of size p each. This is of course possible only if p divides M.

positional arguments:
  M                       domain size
  p                       size of each part
optional arguments:
  --help, -h              show this help message and exit
"""
        parser.add_argument('M', type=nonnegative_int)
        parser.add_argument('p', type=positive_int)

    @staticmethod
    def build_formula(args, formula_class):
        """Build an Counting Principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CountingPrinciple(args.M, args.p)


tse_help_usage = """usage:
 {0} N                --- random 4-regular graph with N vertices.
 {1}                      Random odd charge
 {0} N d              --- random d-regular graph with N vertices.
 {1}                      Random odd charge
 {0} <charge> <graph> --- specific <charge> on specific <graph>
"""

tse_help_description = """A Tseitin formula is defined over a simple undirected graph G.
Each vertex has a {{0,1}} charge and the variables of the formula are
graph's edges. Formula asks to set all edges so that the charge of
each vertex is equal (mod 2) with the sum of the values of the edges
adjacent to that edge.

examples:

 {0} 100 4                 --- Random odd charge on 4-regular graph of size 100
 {0} randomeven gnd 20 6   --- Random odd charge on 6-regular graph of size 20
 {0} first file.dot        --- Put odd charge just on first vertex on graph in 'file.dot'

positional arguments:
  <charge>       --- It can be one of the following:
                     `first'  puts odd charge on first vertex;
                     `random' puts a random charge on vertices;
                     `randomodd' puts random odd  charge on vertices;
                     `randomeven' puts random even charge on vertices.
  <graph>        --- a simple undirected graph (see 'cnfgen --help-graph')

optional arguments:
  --help, -h            show this help message and exit
"""


class TseitinCmdHelper(FormulaHelper):
    """Command line helper for Tseitin  formulas
    """
    name = 'tseitin'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Tseitin formula

        Arguments:
        - `parser`: parser to load with options.
        """

        parser.usage = tse_help_usage.format(
            parser.prog, " " * len(parser.prog))
        parser.description = tse_help_description.format(
            parser.prog, " " * len(parser.prog))

        shortcut = CLIParser()
        shortcut.add_argument('N', type=positive_int, action='store')
        shortcut.add_argument('d',
                              nargs='?',
                              type=positive_int,
                              action='store',
                              default=4)

        longform = CLIParser()
        longform.add_argument(
            'charge',
            metavar='<charge>',
            choices=['first', 'random', 'randomodd', 'randomeven'],
            help="""charge on the vertices.
                                    `first'  puts odd charge on first vertex;
                                    `random' puts a random charge on vertices;
                                    `randomodd' puts random odd  charge on vertices;
                                    `randomeven' puts random even charge on vertices.
                                     """)
        longform.add_argument(
            'G',
            metavar='<graph>',
            help='a simple undirected graph (see \'cnfgen --help-graph\')',
            action=ObtainSimpleGraph)

        tsaction = compose_two_parsers(shortcut, longform)
        parser.add_argument('args',
                            action=tsaction,
                            nargs='*',
                            help=argparse.SUPPRESS)

    @staticmethod
    def build_formula(args, formula_class):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        if not hasattr(args, 'G'):
            N = args.N
            d = args.d
            if N <= d:
                raise ValueError(
                    "There are no {}-regular graphs with {} vertices.\n"
                    "The graph order must be larger than degree.".format(d, N))
            if N * d % 2 == 1:
                raise ValueError(
                    "There are no {}-regular graphs with {} vertices.\n"
                    "Either the order or the degree must be even.".format(
                        d, N))
            G = make_graph_from_spec('simple', ["gnd", N, d])
            charge = [random.randint(0, 1) for _ in range(G.order() - 1)]
            charge.append(1 - sum(charge) % 2)
        else:
            G = args.G

        if G.order() < 1:
            charge = None

        elif not hasattr(args, 'charge'):

            pass

        elif args.charge == 'first':

            charge = [1] + [0] * (G.order() - 1)

        else:  # random vector
            charge = [random.randint(0, 1) for _ in range(G.order() - 1)]

            parity = sum(charge) % 2

            if args.charge == 'random':
                charge.append(random.randint(0, 1))
            elif args.charge == 'randomodd':
                charge.append(1 - parity)
            elif args.charge == 'randomeven':
                charge.append(parity)
            else:
                raise ValueError(
                    'Illegal charge specification on command line')

        return TseitinFormula(G, charge)


ssc_help_usage = """usage:
 {0} N               --- unsat instance of width 3
 {0} N d             --- unsat instance of width d//2 + 1
 {0} <bipartite>     --- formula over a bipartite graph
 {1}                     (see 'cnfgen --help-bipartite')"""

ssc_help_description = """Subset cardinality formula is defined over a bipartite graph: boolean
values are associated to the edges of the graph are set to {{0,1}}.
The formula claims that all vertices on the left have the (loose)
majority of edges set to 1, and all vertices on the right have the
(loose) majority of edges set to 0. The hard unsat cases are when the
graph is a (N,N)-bipartite d-regular graph with an additional edge.
 In particular with d=4 such formula is an unsat 3-CNF, typically hard
for resolution.

examples:
 {0} 100             --- (100,100)-bipartite 4-regular + 1 edge
 {0} 20 6            --- (20,20)-bipartite 4-regular + 1 edge
 {0} scheme.matrix   --- edges of the graphs are specificed by
 {1}                     graph in 'scheme.matrix'

positional arguments:
  N                  --- size of the bipartite graph
  d                  --- size of each constraint
  <bipartite>        --- bipartite graph underlying the formula

optional arguments:
  --equal, -e        encode cardinality constraints as equations
  --help, -h         show this help message and exit
"""
class SCCmdHelper(FormulaHelper):
    name = 'subsetcard'

    @staticmethod
    def setup_command_line(parser):

        parser.usage = ssc_help_usage.format(
            parser.prog, " " * len(parser.prog))
        parser.description = ssc_help_description.format(
            parser.prog, " " * len(parser.prog))

        # now we setup the main parser for the formula generation command
        firstparser = CLIParser()
        firstparser.add_argument('N', type=positive_int, action='store')
        firstparser.add_argument('d',
                                 nargs='?',
                                 type=positive_int,
                                 action='store',
                                 default=4)
        secondparser = CLIParser()
        secondparser.add_argument('B', action=ObtainBipartiteGraph)

        scaction = compose_two_parsers(firstparser, secondparser)

        parser.add_argument('--equal',
                            '-e',
                            default=False,
                            action='store_true',
                            help="encode cardinality constraints as equations")
        parser.add_argument('args',
                            metavar='<graph_description>',
                            action=scaction,
                            nargs='*',
                            help=argparse.SUPPRESS)

    @staticmethod
    def build_formula(args, formula_class):
        if hasattr(args, 'N'):
            N = args.N
            d = args.d
            B = make_graph_from_spec('bipartite',
                                     ['regular', N, N, d, 'addedges', 1])
        elif hasattr(args, 'B'):
            B = args.B
        return SubsetCardinalityFormula(B, args.equal,
                                        formula_class=formula_class)
