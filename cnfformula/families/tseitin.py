#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Tseitin formulas

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""

import cnfformula
from cnfformula import CNF
from cnfformula.cmdline import SimpleGraphHelper

from cnfformula.cnf import parity_constraint

import random

def TseitinFormula(graph,charges=None):
    """Build a Tseitin formula based on the input graph.

    Odd charge is put on the first vertex by default, unless other
    vertices are is specified in input.

    Arguments:
    - `graph`: input graph
    - `charges': odd or even charge for each vertex
    """
    V=sorted(graph.nodes())

    if charges==None:
        charges=[1]+[0]*(len(V)-1)             # odd charge on first vertex
    else:
        charges = [bool(c) for c in charges]   # map to boolean

    if len(charges)<len(V):
        charges=charges+[0]*(len(V)-len(charges))  # pad with even charges

    # init formula
    tse=CNF()
    for e in graph.edges():
        tse.add_variable("E_{{{0},{1}}}".format(*sorted(e)))

    # add constraints
    for v,c in zip(V,charges):
        
        # produce all clauses and save half of them
        names = [ "E_{{{0},{1}}}".format(*sorted(e)) for e in graph.edges_iter(v) ]
        for cls in parity_constraint(names,c):
            tse.add_clause(list(cls))

    return tse


@cnfformula.cmdline.register_cnfgen_subcommand
class TseitinCmdHelper(object):
    """Command line helper for Tseitin  formulas
    """
    name='tseitin'
    description='tseitin formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Tseitin formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--charge',metavar='<charge>',default='first',
                            choices=['first','random','randomodd','randomeven'],
                            help="""charge on the vertices.
                                    `first'  puts odd charge on first vertex;
                                    `random' puts a random charge on vertices;
                                    `randomodd' puts random odd  charge on vertices;
                                    `randomeven' puts random even charge on vertices.
                                     """)
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)

        if G.order()<1:
            charge=None

        elif args.charge=='first':

            charge=[1]+[0]*(G.order()-1)

        else: # random vector
            charge=[random.randint(0,1) for _ in xrange(G.order()-1)]

            parity=sum(charge) % 2

            if args.charge=='random':
                charge.append(random.randint(0,1))
            elif args.charge=='randomodd':
                charge.append(1-parity)
            elif args.charge=='randomeven':
                charge.append(parity)
            else:
                raise ValueError('Illegal charge specification on command line')

        return TseitinFormula(G,charge)
