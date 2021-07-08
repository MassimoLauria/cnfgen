#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helpers for the Pitfall formula

Copyright (C) 2012-2021 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfgen.families.pitfall import PitfallFormula

from .formula_helpers import FormulaHelper
from cnfgen.clitools import positive_int, positive_even_int

usage = """usage:
 {0} <v> <d> <ny> <nz> <k>"""


description = """The Pitfall formula was designed to be specifically easy for
Resolution and hard for common CDCL heuristics. The formula is
unsatisfiable and consists of three parts: an easy formula, a hard
formula, and a pitfall misleading the solver into working with the
hard part. For more details, see the corresponding paper by Marc
Vinyals (AAAI 2020).

example:
 {0} 45 4 30 5 8      --- parameters used in the paper

positional arguments:
  <v>               number of vertices of the Tseitin graph
  <d>               degree of the Tseitin graph
  <ny>              number of pitfall variables
  <nz>              number of safety variables
  <k>               number of copies of the hard and pitfall parts; controls how
                    easy the easy part is

optional arguments:
  --help, -h        show this help message and exit
"""


class PitfallCmdHelper(FormulaHelper):
    name = 'pitfall'

    @staticmethod
    def setup_command_line(parser):

        parser.usage = usage.format(parser.prog)
        parser.description = description.format(parser.prog)

        parser.add_argument('v',  type=positive_int)
        parser.add_argument('d',  type=positive_int)
        parser.add_argument('ny', type=positive_int)
        parser.add_argument('nz', type=positive_int)
        parser.add_argument('k',  type=positive_even_int)

    @staticmethod
    def build_cnf(args):
        return PitfallFormula(args.v, args.d, args.ny, args.nz, args.k)
