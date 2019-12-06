#!/usr/bin/env python

import sys

from cnfgen import cnfgen
from cnfgen.cmdline import get_transformation_helpers

from .test_commandline_helper import TestCommandline

class TestCnfgen(TestCommandline):
    def test_empty(self):
        self.checkCrash(sys.stdin, ["cnfgen"])

    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            cnfgen(["cnfgen", "-h"])
        self.assertEqual(cm.exception.code, 0)

    def test_find_formula_transformations(self):
        subcommands = get_transformation_helpers()
        self.assertNotEqual(subcommands[:], [])
        
    def test_transformations_help(self):
        subcommands = get_transformation_helpers()
        for sc in subcommands:
            with self.assertRaises(SystemExit) as cm:
                cnfgen(["cnfgen", "and", "0", "0", "-T", sc.name, "-h"])
            self.assertEqual(cm.exception.code, 0)

    def test_nonformula_empty(self):
        self.checkCrash(sys.stdin,["cnfgen", "peb", "--tree", 2, "-T", "spam"])

    def test_nonformula_help(self):
        self.checkCrash(sys.stdin,["cnfgen", "peb", "--tree", 2, "-T", "spam", "-h"])
