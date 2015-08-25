#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of simple formulas
"""

from cnfformula.cnf import CNF

import cnfformula.cmdline

@cnfformula.cmdline.register_cnfgen_subcommand
class OR(object):
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
        return CNF([clause],
                   header="Single clause with {} positive"
                          " and {} negative literals".format(args.P,args.N))


@cnfformula.cmdline.register_cnfgen_subcommand
class AND(object):
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
        return CNF(clauses,
                   header="""Singleton clauses: {} positive and {} negative""".format(args.P,args.N))


@cnfformula.cmdline.register_cnfgen_subcommand
class EMPTY(object):
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

@cnfformula.cmdline.register_cnfgen_subcommand
class EMPTY_CLAUSE(object):
    """Command line helper for the contradiction (one empty clauses)  
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

