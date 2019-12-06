#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of some Ordering principle helpers

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019 Massimo Lauria <massimo.lauria@uniroma1.it>
https://massimolauria.net/cnfgen/
"""

from cnfformula import OrderingPrinciple
from cnfformula import GraphOrderingPrinciple

from .graph_cmdline import SimpleGraphHelper
from .formula_helpers import FormulaHelper


class OPCmdHelper(FormulaHelper):
    """Command line helper for Ordering principle formulas
    """
    name='op'
    description='ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return OrderingPrinciple(args.N,args.total,args.smart,args.plant,args.knuth)


class GOPCmdHelper(FormulaHelper):
    """Command line helper for Graph Ordering principle formulas
    """
    name='gop'
    description='graph ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Graph ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return GraphOrderingPrinciple(G,args.total,args.smart,args.plant,args.knuth)


