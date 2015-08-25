#!/usr/bin/env python

import unittest
import cnfformula.cnfgen as cnfgen

class TestCnfgen(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(SystemExit) as cm:
            cnfgen.command_line_utility(["cnfgen"])
        self.assertNotEqual(cm.exception.code, 0)

    def test_help(self):
        with self.assertRaises(SystemExit) as cm:
            cnfgen.command_line_utility(["cnfgen","-h"])
        self.assertEqual(cm.exception.code, 0)

    def test_find_formula_families(self):
        subcommands = cnfgen.find_formula_subcommands()
        self.assertNotEqual(subcommands[:],[])
        
    def test_subformulas_help(self):
        subcommands = cnfgen.find_formula_subcommands()
        for sc in subcommands:
            with self.assertRaises(SystemExit) as cm:
                cnfgen.command_line_utility(["cnfgen", sc.name, "-h"])
            self.assertEqual(cm.exception.code, 0)

    def test_nonformula_empty(self):
        with self.assertRaises(SystemExit) as cm:
            cnfgen.command_line_utility(["cnfgen", "spam"])
        self.assertNotEqual(cm.exception.code, 0)

    def test_nonformula_help(self):
        with self.assertRaises(SystemExit) as cm:
            cnfgen.command_line_utility(["cnfgen", "spam", "-h"])
        self.assertNotEqual(cm.exception.code, 0)
