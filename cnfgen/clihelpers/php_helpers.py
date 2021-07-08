#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for pigeonhole principle formulas

Copyright (C) 2012-2021 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfgen.families.cliquecoloring import CliqueColoring
from cnfgen.families.ramsey import RamseyNumber
from cnfgen.families.ramsey import PythagoreanTriples
from cnfgen.families.ramsey import VanDerWaerden

from cnfgen.families.pigeonhole import PigeonholePrinciple
from cnfgen.families.pigeonhole import GraphPigeonholePrinciple
from cnfgen.families.pigeonhole import BinaryPigeonholePrinciple

from cnfgen.families.pigeonhole import RelativizedPigeonholePrinciple

from cnfgen.graphs import bipartite_random_left_regular

from cnfgen.clitools import ObtainBipartiteGraph
from cnfgen.clitools import CLIParser, CLIHelpFormatter
from cnfgen.clitools import positive_int, nonnegative_int
from cnfgen.clitools import make_graph_doc

from .formula_helpers import FormulaHelper
import argparse

help_usage = """usage:
 {0} N               --- N+1 pigeons fly to N holes
 {0} M N             --- M pigeons fly to N holes
 {0} M N D           --- M pigeons fly to N holes, pigeon left degree D
 {0} <bipartite>     --- pigeons can fly to certain holes with <bipartite>
 {1}                     (see 'cnfgen --help-bipartite')
"""

help_description = """Pigeonhole principle claims that P pigeons can fly to H holes with
no two pigeons in the same hole. This is unsatisfiable when P > H.
Instead of just the number of pigeon and holes, it is possible to
specify a bipartite graph <bipartite> that specifies which pigeons can
fly to which holes. Left vertices of <bipartite> are pigeons, right
vertices are holes.

examples:
 {0} 100             --- 101 pigeons and 100 holes (unsat)
 {0} 14 10           --- 14 pigeons and 10 holes (unsat)
 {0} 9  10           --- 9  pigeons and 10 holes (sat)
 {0} 12 10 3         --- 12 pigeons and 10 holes,
 {1}                     pigeon can go to 3 random holes (unsat)
 {0} graph.gml       --- pigeons and holes specificed by the graph
 {1}                     in file 'graph.gml'
 {0} regular 12 8 4  --- 12 pigeons and 8 holes, each pigeon has
 {1}                     and exactly 4 outgoing edges, each hole has
 {1}                     exactly 6 incoming edges (unsat)

optional arguments:
    --functional         each pigeon sits in at most one hole
    --onto               every hole has a sitting pigeon
    --help, -h           show this help message and exit
"""


def is_some_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


class PHPArgs(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        # now we setup the main parser for the formula generation command
        innerparser = CLIParser(prog=parser.prog,
                                formatter_class=CLIHelpFormatter)
        innerparser.add_argument('B', action=ObtainBipartiteGraph)

        if len(values) == 0:
            parser.error('php formula needs <pigeons> <holes> specification')

        # Use graph spec instead of numeric parameters
        # when first argument is not a number
        if not is_some_number(values[0]):
            innerparser.parse_args(values, namespace=args)
            return

        if len(values) > 3:
            parser.error('too many arguments for php formula')

        try:
            intvalues = [int(x) for x in values]
            if not all([x >= 0 for x in intvalues]):
                raise ValueError
        except ValueError:
            parser.error('php arguments must be positive integers')

        if len(intvalues) == 1:
            setattr(args, "pigeons", intvalues[0] + 1)
            setattr(args, "holes", intvalues[0])
            setattr(args, "degree", intvalues[0])
        elif len(intvalues) == 2:
            setattr(args, "pigeons", intvalues[0])
            setattr(args, "holes", intvalues[1])
            setattr(args, "degree", intvalues[1])
        else:
            setattr(args, "pigeons", intvalues[0])
            setattr(args, "holes", intvalues[1])
            setattr(args, "degree", intvalues[2])

            if intvalues[1] < intvalues[2]:
                parser.error("degree must be at most the number of holes")


class PHPCmdHelper(FormulaHelper):
    """Command line helper for the Pigeonhole principle CNF"""

    name = 'php'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = help_usage.format(parser.prog,
                                         " " * len(parser.prog))
        parser.description = help_description.format(parser.prog,
                                                     " " * len(parser.prog))

        # parser.epilog = "Parameters <bipartite>:" + make_graph_doc(
        #     'bipartite', parser.prog)

        parser.add_argument('pigeonholes',
                            action=PHPArgs,
                            nargs='*',
                            help=argparse.SUPPRESS)
        parser.add_argument('--functional',
                            action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',
                            action='store_true',
                            help="every hole has a sitting pigeon")

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        if hasattr(args, 'B') and args.B is not None:
            return GraphPigeonholePrinciple(args.B,
                                            functional=args.functional,
                                            onto=args.onto)

        elif args.holes == args.degree:
            return PigeonholePrinciple(args.pigeons,
                                       args.holes,
                                       functional=args.functional,
                                       onto=args.onto)
        else:
            G = bipartite_random_left_regular(args.pigeons, args.holes,
                                              args.degree)
            return GraphPigeonholePrinciple(G,
                                            functional=args.functional,
                                            onto=args.onto)


class BPHPCmdHelper(FormulaHelper):
    """Command line helper for the Pigeonhole principle CNF"""

    name = 'bphp'
    description = 'binary pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:
 {0} M N             M pigeons fly to N holes""".format(parser.prog)

        parser.description = """Binary Pigeonhole principle claims that M pigeons can fly to
N holes with no two pigeons in the same hole. This is unsatisfiable
when M > N. The difference with the standad pigeonhole principle is
that here the target hole of a pigeon is represented in binary by
a log(N) variables. If N is not a power of two, invalid targets
are forbidden.

examples:
 {0} 100             --- 101 pigeons and 100 holes (unsat)
 {0} 14 10           --- 14 pigeons and 10 holes (unsat)
 {0} 9  10           --- 9  pigeons and 10 holes (sat)

positional arguments:
  M                    number of pigeons
  N                    number of holes

optional arguments:
  --help, -h           show this help message and exit
""".format(parser.prog)
        parser.add_argument('M', type=positive_int)
        parser.add_argument('N', type=positive_int)

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return BinaryPigeonholePrinciple(args.M, args.N)


class CliqueColoringCmdHelper(FormulaHelper):
    """Command line helper for the Clique-coclique CNF"""

    name = 'cliquecoloring'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for clique-coloring formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:
 {0} n k c""".format(parser.prog)

        parser.description = """Clique-Coloring principle claims that there there is a graph with
n vertices that contains a k-clique and is simultaneously c-colorable.
This is clearly satisfiabile if and only if k<=c and n>=k.

examples:
 {0} 10 4 3          --- there is a 10-verices graph which
 {1}                     is 3-colorable and has a 4-clique (unsat)
 {0} 14 5 5          --- there is a 14-verices graph which
 {1}                     is 5-colorable and has a 5-clique (sat)

positional arguments:
  n                    number of vertices
  k                    number of clique size
  c                    coloring size

optional arguments:
  --help, -h           show this help message and exit
""".format(parser.prog, " "*len(parser.prog))
        parser.add_argument('n', type=nonnegative_int)
        parser.add_argument('k', type=positive_int)
        parser.add_argument('c', type=positive_int)

    @staticmethod
    def build_cnf(args):
        """Build a Clique-coclique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CliqueColoring(args.n, args.k, args.c)


class RamseyCmdHelper(FormulaHelper):
    """Command line helper for RamseyNumber formulas
    """
    name = 'ram'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:
 {0} s k N""".format(parser.prog)

        parser.description = """This formula, given s, k, and N, claims that there is some graph
with N vertices which has neither independent sets of size s nor
cliques of size k. It turns out that there is a number r(s,k), called
Ramsey number, so that every graph with at least r(s,k) vertices must
contain either one or the other. Hence the generated formula is
satisfiable if and only if r(s,k) > N

examples:
 {0} 3 3 6       --- claims r(3,3) > 6   (unsat)
 {0} 4 6 34      --- claims r(4,6) > 34  (sat)
 {0} 4 6 41      --- claims r(4,6) > 41  (unsat)
 {0} 4 6 37      --- claims r(4,6) > 37  (???)
 {0} 5 5 49      --- claims r(5,5) > 49  (unsat)

positional arguments:
  s                    forbidden independent set size
  k                    forbidden clique size
  N                    number of vertices

optional arguments:
  --help, -h           show this help message and exit
""".format(parser.prog)

        parser.add_argument('s', type=positive_int)
        parser.add_argument('k', type=positive_int)
        parser.add_argument('N', type=nonnegative_int)

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RamseyNumber(args.s, args.k, args.N)


vdw_help_usage = """usage:
 {0} N k1 k2             --- claims vdw(k1,k2) > N
 {0} N k1 k2 k3 ... kt   --- claims vdw(k1,k2,...,kt) > N
"""

vdw_help_description = """A van der Waerden formula claims that N is smaller
than the van der Waerden number vdw(k1,k2,...,kt), which is the smallest prefix
of the integers that cannot be t-colored without some arithmetic progression of
(1) color i, (2) length ki.

Formula is satisfiable iff there is a t-coloring of 1...N with no such
arithmetic progressions.

positional arguments:
  N           interval 1...N to be colored
  k1 k2 ...   lengths of the forbidden arith. progressions

optional arguments:
  --help, -h         show this help message and exit
"""


class VDWCmdHelper(FormulaHelper):
    """Command line helper for RamseyNumber formulas
    """
    name = 'vdw'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = vdw_help_usage.format(parser.prog)
        parser.description = vdw_help_description

        parser.add_argument('N', type=nonnegative_int, help=argparse.SUPPRESS)

        parser.add_argument('k1', type=positive_int, help=argparse.SUPPRESS)
        parser.add_argument('k2', type=positive_int, help=argparse.SUPPRESS)

        parser.add_argument('ks',
                            nargs='*',
                            type=positive_int,
                            help=argparse.SUPPRESS)

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return VanDerWaerden(args.N, args.k1, args.k2, *args.ks)


class PTNCmdHelper(FormulaHelper):
    """Command line helper for PTN formulas
    """
    name = 'ptn'
    description = 'Bicoloring of N with no monochromatic Pythagorean Triples'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for PTN formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:
 {0} N""".format(parser.prog)

        parser.description = """

The formula claims that it is possible to bicolor the numbers from 1
to N so that there is no monochromatic triplet (x,y,z) so that

    x^2+y^2 = z^2.

For every positive N there is a number PTN that is the smallest
number for which this bicoloring is impossible. Hence the generated
formula is satisfiable if and only if PTN > N.

examples:
 {0} 6         --- claims PTN > 6     (sat)
 {0} 7824      --- claims PTN > 7824  (sat)
 {0} 7825      --- claims PTN > 7825  (unsat)
 {0} 10000     --- claims PTN > 10000 (unsat)

positional arguments:
  N                    consider the domain [1,...,N]

optional arguments:
  --help, -h           show this help message and exit
""".format(parser.prog)

        parser.add_argument('N', type=nonnegative_int)

    @staticmethod
    def build_cnf(args):
        """Build a PTN formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PythagoreanTriples(args.N)


class RPHPCmdHelper(FormulaHelper):
    """Command line helper for the Relativized Pigeonhole principle CNF"""

    name = 'rphp'
    description = 'relativized pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for relativized pigeonhole principle formula
        Arguments:
        - `parser`: parser to load with options.
        """
        parser.usage = """usage:
 {0} P R H""".format(parser.prog)

        parser.description = """This formula is a variant of the pigeonhole principle. We consider
P pigeons, R resting places, H holes. The formula claims that pigeons
can fly into holes with no conflicts (i.e. two pigeons in the same
home), with the additional caveat that before landing in a hole, each
pigeon stops in some resting place. No two pigeons can rest in the
same place.

examples:
 {0} 10 20 12      --- 10 pigeons, 20 resting places and 12 holes (sat)
 {0} 10  8 12      --- 10 pigeons,  8 resting places and 12 holes (unsat)
 {0} 13 15 11      --- 12 pigeons, 15 resting places and 11 holes (unsat)

positional arguments:
  P                    number of pigeons
  R                    number of resting places
  H                    number of holes

optional arguments:
  --help, -h           show this help message and exit
""".format(parser.prog)

        parser.add_argument('pigeons',        type=nonnegative_int)
        parser.add_argument('resting_places', type=nonnegative_int)
        parser.add_argument('holes',          type=nonnegative_int)

    @staticmethod
    def build_cnf(args):
        """Build a RPHP formula according to the arguments
        Arguments:
        - `args`: command line options
        """
        return RelativizedPigeonholePrinciple(args.pigeons,
                                              args.resting_places, args.holes)
