#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for simple and random formulas

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""


from cnfformula import CNF
from cnfformula import RandomKCNF

from .formula_helpers import FormulaHelper


class OR(FormulaHelper):
    """Command line helper for a single clause formula
    """

    name='or'
    description='a single disjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for single or of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build an disjunction

        Arguments:
        - `args`: command line options
        """
        clause = [ (True,"x_{}".format(i)) for i in range(args.P) ] + \
                 [ (False,"y_{}".format(i)) for i in range(args.N) ]
        orcnf =  CNF([clause])
        orcnf.header = "Clause with {} positive and {} negative literals\n\n".format(args.P,args.N) + \
                       orcnf.header
        return orcnf


class AND(FormulaHelper):
    """Command line helper for a 1-CNF (i.e. conjunction)
    """
    name='and'
    description='a single conjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        clauses = [ [(True,"x_{}".format(i))] for i in range(args.P) ] + \
                  [ [(False,"y_{}".format(i))] for i in range(args.N) ]
        andcnf =  CNF(clauses)
        andcnf.header = "Singleton clauses: {} positive and {} negative\n\n""".format(args.P,args.N) +\
                        andcnf.header
        return andcnf


class EMPTY(FormulaHelper):
    """Command line helper for the empty CNF (no clauses)
    """

    name='empty'
    description='empty CNF formula'

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
        return CNF()

class EMPTY_CLAUSE(FormulaHelper):
    """Command line helper for the contradiction (one empty clause)  
    """

    name='emptyclause'
    description='one empty clause'

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
        return CNF([[]])


class RandCmdHelper(FormulaHelper):
    """Command line helper for random formulas
    """
    name='randkcnf'
    description='random k-CNF'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,help="clause width")
        parser.add_argument('n',metavar='<n>',type=int,help="number of variables")
        parser.add_argument('m',metavar='<m>',type=int,help="number of clauses")

    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        return RandomKCNF(args.k, args.n, args.m)
