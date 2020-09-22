#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some Ordering principle helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

import argparse

from cnfgen.families.ordering import OrderingPrinciple
from cnfgen.families.ordering import GraphOrderingPrinciple

from cnfgen.clitools import ObtainSimpleGraph
from cnfgen.clitools import CLIParser, compose_two_parsers
from cnfgen.clitools import make_graph_from_spec, make_graph_doc

from .formula_helpers import FormulaHelper

help_usage = """{0} [-h] [--total] [--smart] 
                 [--knuth2] [--knuth3] [--plant] N

usage variants:
 {0} N         --- ordering principle on domain of size N
 {0} N d       --- graph ordering principle on random d-regular graph with N vertices.
 {0} <graph>   --- graph ordering principle on <graph> (see 'cnfgen --help-graph')
"""

help_description = """The ordering principle (OP) claims that a partially ordered set of
size N must have a minimal element. This formula translate this into
an unsatisfiable CNF. The graph ordering principle (GOP) is similar:
it claims that any partial order on the vertices of a graph induces
a vertex which is minimal with respect to its neighborhood.

There are variants in which for example we consider total assignment
(see '--total' flag), or where we optimize or reduce the formula in
various ways (see '--smart', --knuth2' and '--knuth3') while keeping
it unsatisfiable.

examples:
 {0} 50                    --- Ordering principle on 50 elements
 {0} 100 4                 --- GOP on 4-regular graph of size 100
 {0} gnm 20 60             --- GOP on random graph with 20 vertices and 60 edges
 {0} file.dot --plant      --- GOP on graph in 'file.dot', satisfiable variant
"""


class OPCmdHelper(FormulaHelper):
    """Command line helper for Ordering principle formulas
    """
    name = 'op'
    description = 'ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """

        parser.usage = help_usage.format(parser.prog)
        parser.description = help_description.format(parser.prog,
                                                     " " * len(parser.prog))

        g = parser.add_mutually_exclusive_group()
        g.add_argument('--total',
                       '-t',
                       default=False,
                       action='store_true',
                       help="assume a total order")
        g.add_argument(
            '--smart',
            '-s',
            default=False,
            action='store_true',
            help=
            "encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument(
            '--knuth2',
            action='store_const',
            dest='knuth',
            const=2,
            help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument(
            '--knuth3',
            action='store_const',
            dest='knuth',
            const=3,
            help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant',
                            '-p',
                            default=False,
                            action='store_true',
                            help="allow a minimum element (makes satisiable)")

        gtparser = CLIParser()
        gtparser.add_argument('N', metavar='<N>', type=int, help="domain size")
        gtparser.add_argument('d',
                              metavar='<N>',
                              nargs='?',
                              type=int,
                              help="degree",
                              default=None)
        gopparser = CLIParser()
        gopparser.add_argument('G',
                               metavar="<graph>",
                               action=ObtainSimpleGraph,
                               help='a simple undirected graph')
        opaction = compose_two_parsers(gtparser, gopparser)
        parser.add_argument('args',
                            action=opaction,
                            nargs='*',
                            help=argparse.SUPPRESS)

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        if hasattr(args, 'G'):
            return GraphOrderingPrinciple(args.G, args.total, args.smart,
                                          args.plant, args.knuth)
        elif hasattr(args, 'd') and args.d is not None:
            N = args.N
            d = args.d
            if N * d % 2 == 1:
                raise ValueError(
                    "There are no {}-regular graphs with {} vertices".format(
                        d, N))
            G = make_graph_from_spec('simple', ['gnd', N, d])
            return GraphOrderingPrinciple(G, args.total, args.smart,
                                          args.plant, args.knuth)
        else:
            return OrderingPrinciple(args.N, args.total, args.smart,
                                     args.plant, args.knuth)
