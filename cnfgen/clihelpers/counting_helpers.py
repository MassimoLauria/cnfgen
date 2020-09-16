#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of counting/matching formulas helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfgen.families.counting import CountingPrinciple
from cnfgen.families.counting import PerfectMatchingPrinciple
from cnfgen.families.tseitin import TseitinFormula
from cnfgen.families.subsetcardinality import SubsetCardinalityFormula

from cnfgen.clitools import ObtainSimpleGraph
from cnfgen.clitools import ObtainBipartiteGraph
from cnfgen.clitools import make_graph_from_spec

from cnfgen.clitools import CLIParser, compose_two_parsers
from cnfgen.clitools import positive_int

from .formula_helpers import FormulaHelper

import random
import argparse


class ParityCmdHelper(FormulaHelper):
    """Command line helper for Parity Principle formulas
    """
    name = 'parity'
    description = 'parity principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Parity Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N', type=int, help="domain size")

    @staticmethod
    def build_cnf(args):
        return CountingPrinciple(args.N, 2)


class PMatchingCmdHelper(FormulaHelper):
    """Command line helper for Perfect Matching Principle formulas
    """
    name = 'matching'
    description = 'perfect matching principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Perfect Matching Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument(
            'G',
            help='simple undirected graph (a file or a graph specification)',
            action=ObtainSimpleGraph)

    @staticmethod
    def build_cnf(args):
        return PerfectMatchingPrinciple(args.G)


class CountingCmdHelper(FormulaHelper):
    """Command line helper for Counting Principle formulas
    """
    name = 'count'
    description = 'counting principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Counting Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('M', metavar='<M>', type=int, help="domain size")
        parser.add_argument('p',
                            metavar='<p>',
                            type=int,
                            help="size of the parts")

    @staticmethod
    def build_cnf(args):
        """Build an Counting Principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CountingPrinciple(args.M, args.p)


class TseitinCmdHelper(FormulaHelper):
    """Command line helper for Tseitin  formulas
    """
    name = 'tseitin'
    description = 'tseitin formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Tseitin formula

        Arguments:
        - `parser`: parser to load with options.
        """
        shortcut = CLIParser()
        shortcut.add_argument('N', type=positive_int, action='store')
        shortcut.add_argument('d', type=positive_int, action='store')

        longform = CLIParser()
        longform.add_argument(
            'charge',
            metavar='charge',
            choices=['first', 'random', 'randomodd', 'randomeven'],
            help="""charge on the vertices.
                                    `first'  puts odd charge on first vertex;
                                    `random' puts a random charge on vertices;
                                    `randomodd' puts random odd  charge on vertices;
                                    `randomeven' puts random even charge on vertices.
                                     """)
        longform.add_argument(
            'G',
            help='simple undirected graph (a file or a graph specification)',
            action=ObtainSimpleGraph)

        tsaction = compose_two_parsers(shortcut, longform)
        parser.add_argument('args',
                            action=tsaction,
                            nargs='+',
                            help=argparse.SUPPRESS)

    @staticmethod
    def build_cnf(args):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        if not hasattr(args, 'G'):
            N = args.N
            d = args.d
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


class SCCmdHelper(FormulaHelper):
    name = 'subsetcard'
    description = 'subset cardinality formulas'

    @staticmethod
    def setup_command_line(parser):

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
                            action=scaction,
                            nargs='+',
                            help=argparse.SUPPRESS)

    @staticmethod
    def build_cnf(args):
        if hasattr(args, 'N'):
            N = args.N
            d = args.d
            B = make_graph_from_spec('bipartite',
                                     ['regular', N, N, d, 'addedges', 1])
        elif hasattr(args, 'B'):
            B = args.B
        return SubsetCardinalityFormula(B, args.equal)
