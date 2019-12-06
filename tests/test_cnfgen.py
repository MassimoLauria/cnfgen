#!/usr/bin/env python

import sys

from cnfgen import cnfgen
from cnfgen.cmdline import get_formula_helpers

from .test_commandline_helper import TestCommandline

class TestCnfgen(TestCommandline):
    def test_empty(self):
        self.checkCrash(sys.stdin, ["cnfgen"])

    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            cnfgen(["cnfgen", "-h"])
        self.assertEqual(cm.exception.code, 0)

    def test_find_formula_families(self):
        subcommands = get_formula_helpers()
        self.assertNotEqual(subcommands[:], [])
        
    def test_subformulas_help(self):
        subcommands = get_formula_helpers()
        for sc in subcommands:
            with self.assertRaises(SystemExit) as cm:
                cnfgen(["cnfgen", sc.name, "-h"])
            self.assertEqual(cm.exception.code, 0)

    def test_nonformula_empty(self):
        self.checkCrash(sys.stdin,["cnfgen","spam"])

    def test_nonformula_help(self):
        self.checkCrash(sys.stdin,["cnfgen","spam", "-h"])
