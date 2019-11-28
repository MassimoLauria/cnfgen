#!/usr/bin/env python

import sys
import cnfformula

import cnfformula.families as families
from cnfformula.cmdline import is_family_helper
from cnfformula.cmdline import find_methods_in_package

from .test_commandline_helper import TestCommandline

class TestCnfgen(TestCommandline):
    def test_empty(self):
        self.checkCrash(sys.stdin,["cnfgen"])

    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            cnfformula.cnfgen(["cnfgen","-h"])
        self.assertEqual(cm.exception.code, 0)

    def test_find_formula_families(self):
        subcommands = find_methods_in_package(families, is_family_helper)
        self.assertNotEqual(subcommands[:],[])
        
    def test_subformulas_help(self):
        subcommands = find_methods_in_package(families, is_family_helper)
        for sc in subcommands:
            with self.assertRaises(SystemExit) as cm:
                cnfformula.cnfgen(["cnfgen", sc.name, "-h"])
            self.assertEqual(cm.exception.code, 0)

    def test_nonformula_empty(self):
        self.checkCrash(sys.stdin,["cnfgen","spam"])

    def test_nonformula_help(self):
        self.checkCrash(sys.stdin,["cnfgen","spam", "-h"])
