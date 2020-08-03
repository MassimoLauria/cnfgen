#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for the Pitfall formula

Copyright (C) 2012-2020 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfformula.families.pitfall import PitfallFormula

from .formula_helpers import FormulaHelper
from .cmdline import positive_int, nonnegative_int

usage_string = """Pitfall Formula

The Pitfall formula has been designed by Marc Vinyals (AAAI 2020) to
be specifically easy for Resolution and hard for common CDCL
heuristics. The formula is unsatisfiable and is the union of an easy
to refute and several copies of unsatisfiable Tseitin formulas on
random regular graphs. For more details on this formula I suggest to
read the corresponding paper.
"""
# positional arguments:
#  {0} v,d,ny,nz,k

#  where:
#  v    --- number of graph vertices for the Tseitin part
#  d    --- graph degree for the Tseitin part
#  ny   --- ??
#  nz   --- ??
#  k    --- number of copies of the Tseitin formula
#  """


class PitfallCmdHelper(FormulaHelper):
    name = 'pitfall'
    description = 'Pitfall formula'

    @staticmethod
    def setup_command_line(parser):

        parser.usage = usage_string.format(parser.prog)

        parser.add_argument('v',
                            type=positive_int,
                            help='vertices in each graph')
        parser.add_argument('d',
                            type=positive_int,
                            help='degree in each graph')
        parser.add_argument('ny', type=positive_int)
        parser.add_argument('nz', type=positive_int)
        parser.add_argument('k', type=positive_int)

    @staticmethod
    def build_cnf(args):

        return PitfallFormula(args.v, args.d, args.ny, args.nz, args.k)
