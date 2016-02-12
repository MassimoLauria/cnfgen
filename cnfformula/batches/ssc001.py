#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""First collection of subset cardinality formulas.
"""

from cnfformula.cnfgen import command_line_utility as cmd
from cnfformula.batches import register_cnf_batch
from cnfformula.graphs import writeGraph,bipartite_random_regular

import random

@register_cnf_batch
class SSC001(object):

    name='ssc001'
    description='Subset cardinality formulas (4 entries per row/col +1 entry) on NxN N=5,10,..,50'

    random_seed = 734841396579L
    
    @classmethod
    def run(cls):

        print("""Subset cardinality formulas

Each formula is on an NxN matrix with 4 non empty entries per row and per column.
Matrix are saved along with the DIMACS files.
""")

        for s in xrange(5,51,5):

            fname = "ssc001size{}.cnf".format(s)
            gname = "ssc001size{}.matrix".format(s)

            print("-- {} and {}".format(gname,fname))

            G = bipartite_random_regular(s,s,4)
            
            writeGraph(G,gname,graph_type="bipartite")
            cmd(["cnfgen","-o",fname,"subsetcard","-i",gname])
