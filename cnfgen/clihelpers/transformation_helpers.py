#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Transformation Helpers for command line

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020, 2021 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

import argparse

# Formula transformation implemented
from cnfgen.transformations.shuffle import Shuffle
from cnfgen.transformations.substitutions import AllEqualSubstitution
from cnfgen.transformations.substitutions import ExactlyOneSubstitution
from cnfgen.transformations.substitutions import ExactlyKSubstitution
from cnfgen.transformations.substitutions import AnythingButKSubstitution
from cnfgen.transformations.substitutions import AtMostKSubstitution
from cnfgen.transformations.substitutions import AtLeastKSubstitution
from cnfgen.transformations.substitutions import FlipPolarity
from cnfgen.transformations.substitutions import FormulaLifting
from cnfgen.transformations.substitutions import IfThenElseSubstitution
from cnfgen.transformations.substitutions import MajoritySubstitution
from cnfgen.transformations.substitutions import NotAllEqualSubstitution
from cnfgen.transformations.substitutions import OrSubstitution
from cnfgen.transformations.substitutions import VariableCompression
from cnfgen.transformations.substitutions import XorSubstitution

from cnfgen.clitools import ObtainBipartiteGraph, make_graph_doc, make_graph_from_spec
from cnfgen.clitools import CLIParser, positive_int, compose_two_parsers


class TransformationHelper:
    """Command line helper for a formula family"""
    name = ""

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

    @staticmethod
    def setup_command_line(parser):

        parser.usage="""usage:
 {0} [-p] [-v] [-c]""".format(parser.prog)

        parser.description= """Randomly reorder the formula, shuffling the variables, the clauses and
flipping the polarity of literal.

optional arguments:
  --no-polarity-flips, -p
                        Suppress polarity flips (default: active)
  --no-variables-permutation, -v
                        Suppress variable permutations (default: active)
  --no-clauses-permutation, -c
                        Suppress clauses permutations (default: active)
  --help, -h          show this help message and exit
"""

        parser.add_argument('--no-polarity-flips',
                            '-p',
                            action='store_true',
                            default=False,
                            dest='no_polarity_flips')
        parser.add_argument('--no-variables-permutation',
                            '-v',
                            action='store_true',
                            default=False,
                            dest='no_variables_permutation')
        parser.add_argument('--no-clauses-permutation',
                            '-c',
                            action='store_true',
                            default=False,
                            dest='no_clauses_permutation')

    @staticmethod
    def transform_cnf(F, args):
        return Shuffle(
            F,
            polarity_flips='fixed' if args.no_polarity_flips else 'shuffle',
            variables_permutation='fixed'
            if args.no_variables_permutation else 'shuffle',
            clauses_permutation='fixed'
            if args.no_clauses_permutation else 'shuffle')


#
# Command line helpers for these substitutions
#


class NoSubstitutionCmd(TransformationHelper):
    name = 'none'
    description = 'no transformation'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0}".format(parser.prog)

        parser.description =\
"""No transformation is applied.

optional arguments:
  --help, -h          show this help message and exit
"""
        pass

    @staticmethod
    def transform_cnf(F, args):
        return F


class OrSubstitutionCmd(TransformationHelper):
    name = 'or'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
predicate ``X(1) or ... or X(N)'' where variables X(1), ..., X(N)
are new.

positional arguments:
  N                   the arity of the or operator

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return OrSubstitution(F, args.N)


class XorSubstitutionCmd(TransformationHelper):
    name = 'xor'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
predicate ``X(1)+...+X(N) == 1 (mod 2)'' where variables
X(1), ..., X(N) are new.

positional arguments:
  N                   the arity of the sum

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return XorSubstitution(F, args.N)


class AllEqualsSubstitutionCmd(TransformationHelper):
    name = 'eq'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
 predicate claiming that all the new variables X(1),...,X(N) have
 the same value.

positional arguments:
  N                   the arity of the predicate

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return AllEqualSubstitution(F, args.N)


class NeqSubstitutionCmd(TransformationHelper):
    name = 'neq'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
 predicate claiming that the new variables X(1),...,X(N) do not have
 all the same value.

positional arguments:
  N                   the arity of the predicate

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return NotAllEqualSubstitution(F, args.N)


class MajSubstitution(TransformationHelper):
    name = 'maj'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
predicate ``X(1)+...+X(N) >= N/2'' where variables X(1), ..., X(N)
are new.

positional arguments:
  N                   the arity of the sum

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return MajoritySubstitution(F, args.N)


class IfThenElseSubstitutionCmd(TransformationHelper):
    name = 'ite'

    @staticmethod
    def setup_command_line(parser):
        parser.usage="usage:\n {0}".format(parser.prog)
        parser.description=\
"""Substitute a variable X with the predicate
  if C then Y else Z
where C, Y, Z are new variables.

optional arguments:
  --help, -h          show this help message and exit
"""

    @staticmethod
    def transform_cnf(F, args):
        return IfThenElseSubstitution(F)


class ExactlyOneSubstitutionCmd(TransformationHelper):
    name = 'one'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
 predicate X(1)+...+X(N) == 1 where variables X(1), ..., X(N) are new.

positional arguments:
  N                   the arity of the sum

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return ExactlyOneSubstitution(F, args.N)


class AtLeastKSubstitutionCmd(TransformationHelper):
    name = 'atleast'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N k".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
 predicate X(1)+...+X(N) >= k where variables X(1), ..., X(N) are new.

positional arguments:
  N                   the arity of the sum
  k                   the lower threshold

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)
        parser.add_argument('K', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return AtLeastKSubstitution(F, args.N, args.K)


class AtMostKSubstitutionCmd(TransformationHelper):
    name = 'atmost'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N k".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
 predicate X(1)+...+X(N) <= k where variables X(1), ..., X(N) are new.

positional arguments:
  N                   the arity of the sum
  k                   the upper threshold

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)
        parser.add_argument('K', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return AtMostKSubstitution(F, args.N, args.K)


class ExactlyKSubstitutionCmd(TransformationHelper):
    name = 'exact'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N k".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
 predicate X(1)+...+X(N) == k where variables X(1), ..., X(N) are new.

positional arguments:
  N                   the arity of the sum
  k                   the desired value

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)
        parser.add_argument('K', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return ExactlyKSubstitution(F, args.N, args.K)


class AnythingButKSubstitutionCmd(TransformationHelper):
    name = 'anybut'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} N k".format(parser.prog)

        parser.description =\
"""The value of each original variable X substituted with the
 predicate X(1)+...+X(N) !=k where variables X(1), ..., X(N) are new.

positional arguments:
  N                   the arity of the sum
  k                   the forbidded value

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('N', type=positive_int)
        parser.add_argument('K', type=positive_int)

    @staticmethod
    def transform_cnf(F, args):
        return AnythingButKSubstitution(F, args.N, args.K)


# Technically lifting is not a substitution, therefore it should be in
# another file. Unfortunately there is a lot of dependency from
# this one.


class FormulaLiftingCmd(TransformationHelper):
    """Lifting
    """
    name = 'lift'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0} k".format(parser.prog)

        parser.description =\
"""One dimensional lifting of the formula. The value of the original
variable X is taken from one among new variables X(1), ..., X(k).
Which one is decided by the new selector variables Y(1), ..., Y(k), for
which the condition Y(1)+...+Y(k) = 1 is enforced.

positional arguments:
  k                   the rank of the lifting

optional arguments:
  --help, -h          show this help message and exit
"""
        parser.add_argument('k', type=positive_int, action='store')

    @staticmethod
    def transform_cnf(F, args):
        return FormulaLifting(F, args.k)


class FlipCmd(TransformationHelper):
    name = 'flip'

    @staticmethod
    def setup_command_line(parser):
        parser.usage = "usage:\n {0}\n".format(parser.prog)
        parser.description ="Inverts the polarity of all literals in the formula."

    @staticmethod
    def transform_cnf(F, args):

        return FlipPolarity(F)


class XorCompressionCmd(TransformationHelper):
    name = 'xorcomp'

    @staticmethod
    def setup_command_line(parser):

        parser.usage = """usage:
 {0} N
 {0} N d
 {0} <bipartite>""".format(parser.prog)

        parser.description =\
"""Variable compression: each variable in the original formula is
substituted with the XOR of d members of a set of N new variables.
Alternatively you can use

 {0} <mapping>

to give an explicit mapping between each original variable and the
corresponding set of new variables. In this case <mapping> is
a bipartite graph (see 'cnfgen --help-bipartite').

positional arguments:
  N           number of new variables
  d           arity of majority (default: 3)
  <mapping>   a bipartite graph (see 'cnfgen --help-bipartite')

optional arguments:
  --help, -h          show this help message and exit
""".format(parser.prog)

        firstparser = CLIParser()
        firstparser.add_argument('N', type=positive_int, action='store')
        firstparser.add_argument('d',
                                 nargs='?',
                                 type=positive_int,
                                 action='store',
                                 default=3)
        secondparser = CLIParser()
        secondparser.add_argument('B', action=ObtainBipartiteGraph)

        action = compose_two_parsers(firstparser, secondparser)

        parser.add_argument('args',
                            metavar='<graph_description>',
                            action=action,
                            nargs='*',
                            help=argparse.SUPPRESS)

    @staticmethod
    def transform_cnf(F, args):
        if hasattr(args, 'N'):
            N = args.N
            d = args.d
            V = len(list(F.variables()))
            B = make_graph_from_spec('bipartite', ['glrd', V, N, d])
        elif hasattr(args, 'B'):
            B = args.B

        return VariableCompression(F, B, function='xor')


class MajCompressionCmd(TransformationHelper):
    name = 'majcomp'

    @staticmethod
    def setup_command_line(parser):

        parser.usage = """usage:
 {0} N
 {0} N d
 {0} <bipartite>""".format(parser.prog)

        parser.description =\
"""Variable compression: each variable in the original formula is
substituted with the majority of d members of a set of N new
variables. Alternatively you can use

 {0} <mapping>

to give an explicit mapping between each original variable and the
corresponding set of new variables. In this case <mapping> is
a bipartite graph (see 'cnfgen --help-bipartite').

positional arguments:
  N           number of new variables
  d           arity of majority (default: 3)
  <mapping>   a bipartite graph (see 'cnfgen --help-bipartite')

optional arguments:
  --help, -h          show this help message and exit
""".format(parser.prog)

        firstparser = CLIParser()
        firstparser.add_argument('N', type=positive_int, action='store')
        firstparser.add_argument('d',
                                 nargs='?',
                                 type=positive_int,
                                 action='store',
                                 default=3)
        secondparser = CLIParser()
        secondparser.add_argument('B', action=ObtainBipartiteGraph)

        action = compose_two_parsers(firstparser, secondparser)

        parser.add_argument('args',
                            metavar='<graph_description>',
                            action=action,
                            nargs='*',
                            help=argparse.SUPPRESS)

    @staticmethod
    def transform_cnf(F, args):
        if hasattr(args, 'N'):
            N = args.N
            d = args.d
            V = len(list(F.variables()))
            B = make_graph_from_spec('bipartite', ['glrd', V, N, d])
        elif hasattr(args, 'B'):
            B = args.B

        return VariableCompression(F, B, function='maj')
