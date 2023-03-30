#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for simple and random formulas

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020, 2021, 2022, 2023 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfgen.formula.cnf import CNF
from cnfgen.families.randomformulas import RandomKCNF
from cnfgen.families.randomkxor import RandomKXOR
from cnfgen.clitools import nonnegative_int, positive_int
from .formula_helpers import FormulaHelper

import random


class OR(FormulaHelper):
    """Command line helper for a single clause formula
    """

    name = 'or'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for single or of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} <P> <N>".format(parser.prog)
        parser.description = """A single clause with <P> positive and <N> negative literals

positional arguments:
  <P>                  number of positive literals
  <N>                  number of negative literals

optional arguments:
  --help, -h           show this help message and exit
"""
        parser.add_argument('P', type=nonnegative_int)
        parser.add_argument('N', type=nonnegative_int)

    @staticmethod
    def build_formula(args, formula_class):
        """Build an disjunction

        Arguments:
        - `args`: command line options
        """
        description = "A clause with {} positive and {} negative literals".format(
            args.P, args.N)
        F = formula_class(description=description)
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

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} <P> <N>".format(parser.prog)
        parser.description = """A single conjunction or <P> positive and <N> negative literals

positional arguments:
  <P>                  number of positive literals
  <N>                  number of negative literals

optional arguments:
  --help, -h           show this help message and exit
"""
        parser.add_argument('P', type=nonnegative_int)
        parser.add_argument('N', type=nonnegative_int)

    @staticmethod
    def build_formula(args, formula_class):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        description = "Singleton clauses: {} positive and {} negative".format(
            args.P, args.N)
        F = formula_class(description=description)
        positive = F.new_block(args.P,label='x_{}')
        negative = F.new_block(args.N,label='y_{}')
        F.add_clauses_from([v] for v in positive)
        F.add_clauses_from([-v] for v in negative)
        return F


class TRUE(FormulaHelper):
    """Command line helper for the empty CNF (no clauses)
    """

    name = 'true'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0}".format(parser.prog)
        parser.description = """A CNF with no clauses, hence always true.

optional arguments:
  --help, -h           show this help message and exit
"""

    @staticmethod
    def build_formula(args, formula_class):
        """Build an empty CNF formula

        Parameters
        ----------
        args : ignored
             command line options
        """
        return formula_class(description='Formula with no clauses')


class FALSE(FormulaHelper):
    """Command line helper for the contradiction (one empty clause)
    """

    name = 'false'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0}".format(parser.prog)
        parser.description = """A CNF with one empty clause, hence always false.

optional arguments:
  --help, -h           show this help message and exit
"""

    @staticmethod
    def build_formula(args, formula_class):
        """Build a CNF formula with an empty clause

        Parameters
        ----------
        args : ignored
             command line options
        """
        F = formula_class(description='Formula with one empty clause')
        F.add_clause([])
        return F


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
        parser.usage = "usage:\n {0} [-h|--help] [-p|--plant] <k> <n> <m>".format(parser.prog)
        parser.description = """ Sample <m> clauses over <n> variables, each of width <k>,
uniformly at random. The sampling is done without repetition, meaning
that whenever a clause is already in the CNF, it is never
picked again.

positional arguments:
  <k>                  width of the clauses
  <n>                  number of variables in the formula
  <m>                  number of sampled clauses

optional arguments:
  --plant, -p          plant a random satisfying assignment (default: no)
  --help, -h           show this help message and exit
"""
        parser.add_argument('k', type=positive_int)
        parser.add_argument('n', type=positive_int)
        parser.add_argument('m', type=nonnegative_int)
        parser.add_argument('--plant',
                            '-p',
                            action='store_true',
                            default=False)

    @staticmethod
    def build_formula(args, formula_class):
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
                              planted_assignments=[planted],
                              formula_class=formula_class)
        else:
            return RandomKCNF(args.k, args.n, args.m,
                              formula_class=formula_class)

class RandXorHelper(FormulaHelper):
    """Command line helper for random formulas
    """
    name = 'randkxor'
    description = 'random k-XOR'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = "usage:\n {0} [-h|--help] [-p|--plant] <k> <n> <m>".format(parser.prog)
        parser.description = """ Sample <m> parity constraints over <n> variables, each of width <k>,
uniformly at random. The sampling is done without repetition, meaning
that whenever a xor is already in the formula, it is never
picked again.

positional arguments:
  <k>                  width of the parities
  <n>                  number of variables in the formula
  <m>                  number of sampled xors

optional arguments:
  --plant, -p          plant a random satisfying assignment (default: no)
  --help, -h           show this help message and exit
"""
        parser.add_argument('k', type=positive_int)
        parser.add_argument('n', type=positive_int)
        parser.add_argument('m', type=nonnegative_int)
        parser.add_argument('--plant',
                            '-p',
                            action='store_true',
                            default=False)

    @staticmethod
    def build_formula(args, formula_class):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        n = args.n
        if args.plant:
            planted = [random.choice([-1,1])*v for v in range(1,n+1)]
            return RandomKXOR(args.k,
                              args.n,
                              args.m,
                              planted_assignments=[planted],
                              formula_class=formula_class)
        else:
            return RandomKXOR(args.k, args.n, args.m,
                              formula_class=formula_class)
