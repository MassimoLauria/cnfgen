#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for simple and random formulas

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020, 2021 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfgen.formula.cnf import CNF
from cnfgen.families.randomformulas import RandomKCNF

from .formula_helpers import FormulaHelper

import random


class OR(FormulaHelper):
    """Command line helper for a single clause formula
    """

    name = 'or'
    description = 'a single disjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for single or of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',
                            metavar='<P>',
                            type=int,
                            help="positive literals")
        parser.add_argument('N',
                            metavar='<N>',
                            type=int,
                            help="negative literals")

    @staticmethod
    def build_cnf(args):
        """Build an disjunction

        Arguments:
        - `args`: command line options
        """
        description = "A clause with {} positive and {} negative literals".format(
            args.P, args.N)
        F = CNF(description=description)
        positive = F.new_block(args.P,label='x_{}')
        negative = F.new_block(args.N,label='y_{}')
        clause = []
        clause.extend(positive)
        clause.extend(-v for v in negative)
        F.add_clause(clause)
        return F


class AND(FormulaHelper):
    """Command line helper for a 1-CNF (i.e. conjunction)
    """
    name = 'and'
    description = 'a single conjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',
                            metavar='<P>',
                            type=int,
                            help="positive literals")
        parser.add_argument('N',
                            metavar='<N>',
                            type=int,
                            help="negative literals")

    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        description = "Singleton clauses: {} positive and {} negative".format(
            args.P, args.N)
        F = CNF(description=description)
        positive = F.new_block(args.P,label='x_{}')
        negative = F.new_block(args.N,label='y_{}')
        F.add_clauses_from([v] for v in positive)
        F.add_clauses_from([-v] for v in negative)
        return F


class TRUE(FormulaHelper):
    """Command line helper for the empty CNF (no clauses)
    """

    name = 'true'
    description = 'CNF formula with no clauses'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def build_cnf(args):
        """Build an empty CNF formula

        Parameters
        ----------
        args : ignored
             command line options
        """
        return CNF(description='Formula with no clauses')


class FALSE(FormulaHelper):
    """Command line helper for the contradiction (one empty clause)
    """

    name = 'false'
    description = 'CNF with one empty clause'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def build_cnf(args):
        """Build a CNF formula with an empty clause

        Parameters
        ----------
        args : ignored
             command line options
        """
        return CNF([[]], description='Formula with one empty clause')


class RandCmdHelper(FormulaHelper):
    """Command line helper for random formulas
    """
    name = 'randkcnf'
    description = 'random k-CNF'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k', metavar='<k>', type=int, help="clause width")
        parser.add_argument('n',
                            metavar='<n>',
                            type=int,
                            help="number of variables")
        parser.add_argument('m',
                            metavar='<m>',
                            type=int,
                            help="number of clauses")
        parser.add_argument('--plant',
                            '-p',
                            action='store_true',
                            default=False,
                            help="plant a sat assignment at random")

    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        n = args.n
        if args.plant:
            planted = [random.choice([-1,1])*v for v in range(1,n+1)]
            return RandomKCNF(args.k,
                              args.n,
                              args.m,
                              planted_assignments=[planted])
        else:
            return RandomKCNF(args.k, args.n, args.m)
