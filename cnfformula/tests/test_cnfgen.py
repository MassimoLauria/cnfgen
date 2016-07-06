#!/usr/bin/env python

import sys
import cnfformula.cnfgen as cnfgen
import cnfformula.families as families
import cnfformula.cmdline as cmdline

from .test_commandline_helper import TestCommandline, stderr_redirector

class TestCnfgen(TestCommandline):
    def test_empty(self):
        self.checkCrash(sys.stdin,["cnfgen"])

    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            cnfgen.command_line_utility(["cnfgen","-h"])
        self.assertEqual(cm.exception.code, 0)

    def test_find_formula_families(self):
        subcommands = cmdline.find_methods_in_package(families,cmdline.is_cnfgen_subcommand)
        self.assertNotEqual(subcommands[:],[])
        
    def test_subformulas_help(self):
        subcommands = cmdline.find_methods_in_package(families,cmdline.is_cnfgen_subcommand)
        for sc in subcommands:
            with self.assertRaises(SystemExit) as cm:
                cnfgen.command_line_utility(["cnfgen", sc.name, "-h"])
            self.assertEqual(cm.exception.code, 0)

    def test_nonformula_empty(self):
        self.checkCrash(sys.stdin,["cnfgen","spam"])

    def test_nonformula_help(self):
        self.checkCrash(sys.stdin,["cnfgen","spam", "-h"])
