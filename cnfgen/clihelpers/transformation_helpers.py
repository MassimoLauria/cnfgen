#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Transformation Helpers for command line

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

# Formula transformation implemented
from cnfgen.transformations.shuffle import Shuffle
from cnfgen.transformations.substitutions import AllEqualSubstitution
from cnfgen.transformations.substitutions import ExactlyOneSubstitution
from cnfgen.transformations.substitutions import FlipPolarity
from cnfgen.transformations.substitutions import FormulaLifting
from cnfgen.transformations.substitutions import IfThenElseSubstitution
from cnfgen.transformations.substitutions import MajoritySubstitution
from cnfgen.transformations.substitutions import NotAllEqualSubstitution
from cnfgen.transformations.substitutions import OrSubstitution
from cnfgen.transformations.substitutions import VariableCompression
from cnfgen.transformations.substitutions import XorSubstitution

from cnfgen.clitools import BipartiteGraphHelper


class TransformationHelper:
    """Command line helper for a formula family"""
    name = None
    description = None

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line parser for this transformation subcommand"""
        raise NotImplementedError(
            "Transformation family helper must be subclassed")

    @staticmethod
    def transform_cnf(F, args):
        """Build the new CNF by applying the transformation"""
        raise NotImplementedError(
            "Transformation family helper must be subclassed")


class ShuffleCmd(TransformationHelper):
    """Shuffle 
    """
    name = 'shuffle'
    description = 'Permute variables, clauses and polarity of literals at random'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('--no-polarity-flips',
                            '-p',
                            action='store_true',
                            default=False,
                            dest='no_polarity_flips',
                            help="No polarity flips")
        parser.add_argument('--no-variables-permutation',
                            '-v',
                            action='store_true',
                            default=False,
                            dest='no_variables_permutation',
                            help="No permutation of variables")
        parser.add_argument('--no-clauses-permutation',
                            '-c',
                            action='store_true',
                            default=False,
                            dest='no_clauses_permutation',
                            help="No permutation of clauses")

    @staticmethod
    def transform_cnf(F, args):
        return Shuffle(
            F,
            variables_permutation=None
            if not args.no_variables_permutation else list(F.variables()),
            clauses_permutation=None
            if not args.no_clauses_permutation else list(range(len(F))),
            polarity_flips=None if not args.no_polarity_flips else [1] *
            len(list(F.variables())))


#
# Command line helpers for these substitutions
#


class NoSubstitutionCmd(TransformationHelper):
    name = 'none'
    description = 'no transformation'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def transform_cnf(F, args):
        return F


class OrSubstitutionCmd(TransformationHelper):
    name = 'or'
    description = 'substitute variable x with OR(x1,x2,...,xN)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',
                            type=int,
                            nargs='?',
                            default=2,
                            action='store',
                            help="arity (default: 2)")

    @staticmethod
    def transform_cnf(F, args):
        return OrSubstitution(F, args.N)


class XorSubstitutionCmd(TransformationHelper):
    name = 'xor'
    description = 'substitute variable x with XOR(x1,x2,...,xN)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',
                            type=int,
                            nargs='?',
                            default=2,
                            action='store',
                            help="arity (default: 2)")

    @staticmethod
    def transform_cnf(F, args):
        return XorSubstitution(F, args.N)


class AllEqualsSubstitutionCmd(TransformationHelper):
    name = 'eq'
    description = 'substitute variable x with predicate x1==x2==...==xN (i.e. all equals)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',
                            type=int,
                            nargs='?',
                            default=3,
                            action='store',
                            help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F, args):
        return AllEqualSubstitution(F, args.N)


class NeqSubstitutionCmd(TransformationHelper):
    name = 'neq'
    description = 'substitute variable x with predicate |{x1,x2,...,xN}|>1 (i.e. not all equals)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',
                            type=int,
                            nargs='?',
                            default=3,
                            action='store',
                            help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F, args):
        return NotAllEqualSubstitution(F, args.N)


class MajSubstitution(TransformationHelper):
    name = 'maj'
    description = 'substitute variable x with predicate Majority(x1,x2,...,xN)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',
                            type=int,
                            nargs='?',
                            default=3,
                            action='store',
                            help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F, args):
        return MajoritySubstitution(F, args.N)


class IfThenElseSubstitutionCmd(TransformationHelper):
    name = 'ite'
    description = 'substitute variable x with predicate "if X then Y else Z"'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def transform_cnf(F, args):
        return IfThenElseSubstitution(F)


class ExactlyOneSubstitutionCmd(TransformationHelper):
    name = 'one'
    description = 'substitute variable x with predicate x1+x2+...+xN = 1'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',
                            type=int,
                            nargs='?',
                            default=3,
                            action='store',
                            help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F, args):
        return ExactlyOneSubstitution(F, args.N)


# Technically lifting is not a substitution, therefore it should be in
# another file. Unfortunately there is a lot of dependency from
# this one.


class FormulaLiftingCmd(TransformationHelper):
    """Lifting 
    """
    name = 'lift'
    description = 'one dimensional lifting  x -->  x1 y1  OR ... OR xN yN, with y1+..+yN = 1'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',
                            type=int,
                            nargs='?',
                            default=3,
                            action='store',
                            help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F, args):
        return FormulaLifting(F, args.N)


class FlipCmd(TransformationHelper):
    name = 'flip'
    description = 'negate all variables in the formula'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def transform_cnf(F, args):

        return FlipPolarity(F)


class XorCompressionCmd(TransformationHelper):
    name = 'xorcomp'
    description = 'variable compression using XOR'

    @staticmethod
    def setup_command_line(parser):
        BipartiteGraphHelper.setup_command_line(parser)

    @staticmethod
    def transform_cnf(F, args):
        B = BipartiteGraphHelper.obtain_graph(args)

        return VariableCompression(F, B, function='xor')


class MajCompressionCmd(TransformationHelper):
    name = 'majcomp'
    description = 'variable compression using Majority'

    @staticmethod
    def setup_command_line(parser):
        BipartiteGraphHelper.setup_command_line(parser)

    @staticmethod
    def transform_cnf(F, args):
        B = BipartiteGraphHelper.obtain_graph(args)

        return VariableCompression(F, B, function='maj')
