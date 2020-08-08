#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for the Pitfall formula

Copyright (C) 2012-2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfgen.families.pitfall import PitfallFormula

from .formula_helpers import FormulaHelper
from cnfgen.clitools import positive_int, positive_even_int

usage_string = """Pitfall Formula

    The Pitfall formula was designed to be specifically easy for
    Resolution and hard for common CDCL heuristics. The formula is
    unsatisfiable and consists of three parts: an easy formula, a hard
    formula, and a pitfall misleading the solver into working with the
    hard part.

    The hard part are several copies of an unsatisfiable Tseitin
    formula on a random regular graph. The pitfall part is made up of
    a few gadgets over (primarily) two sets of variables: pitfall
    variables, which point the solver towards the hard part after
    being assigned, and safety variables, which prevent the gadget
    from breaking even if a few other variables are assigned.

    For more details, see the corresponding paper (Marc Vinyals, AAAI
    2020).

positional arguments:
 {0} v,d,ny,nz,k

 where:
 v    --- number of vertices of the Tseitin graph
 d    --- degree of the Tseitin graph
 ny   --- number of pitfall variables
 nz   --- number of safety variables
 k    --- number of copies of the hard and pitfall parts; controls how
          easy the easy part is
"""

example_string = """example:
 {0} 45 4 30 5 8      --- parameters used in the paper
 """


class PitfallCmdHelper(FormulaHelper):
    name = 'pitfall'
    description = 'Pitfall formula'

    @staticmethod
    def setup_command_line(parser):

        parser.usage = usage_string.format(parser.prog)

        parser.add_argument('v',
                            type=positive_int,
                            help="number of vertices of the Tseitin graph")
        parser.add_argument('d',
                            type=positive_int,
                            help="degree of the Tseitin graph")
        parser.add_argument('ny',
                            type=positive_int,
                            help="number of pitfall variables")
        parser.add_argument('nz',
                            type=positive_int,
                            help="number of safety variables")
        parser.add_argument(
            'k',
            type=positive_even_int,
            help="number of copies of the hard and pitfall parts")

    @staticmethod
    def build_cnf(args):

        return PitfallFormula(args.v, args.d, args.ny, args.nz, args.k)
