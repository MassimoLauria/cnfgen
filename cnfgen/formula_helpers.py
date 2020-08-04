#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula Helper interface

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""


class FormulaHelper:
    """Command line helper for a formula family"""

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line parser for this formula subcommand"""
        raise NotImplementedError("Formula family helper must be subclassed")

    @staticmethod
    def build_cnf(args):
        """Buil the CNF according to the parameters on the command line"""
        raise NotImplementedError("Formula family helper must be subclassed")


