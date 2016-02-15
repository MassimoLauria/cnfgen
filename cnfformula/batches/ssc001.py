#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""First collection of subset cardinality formulas.
"""

from cnfformula.cnfgen import command_line_utility as cmd
from cnfformula.batches import register_cnf_batch
from cnfformula.graphs import writeGraph,bipartite_random_regular,sample_missing_edges

import random

@register_cnf_batch
class SSC001(object):

    name='ssc001'
    description='Subset cardinality formulas (4 entries per row/col +1 entry) on NxN N=50,100,..,1000'

    random_seed = 734841396579L
    
    @classmethod
    def run(cls):

        print("""Subset cardinality formulas

Each formula is on an NxN matrix with 4 non empty entries per row and per column.
Matrix are saved along with the DIMACS files.
""")

        for s in xrange(50,1001,50):

            fname = "ssc001size{}.cnf".format(s)
            gname = "ssc001size{}.matrix".format(s)

            print("-- {} and {}".format(gname,fname))

            G = bipartite_random_regular(s,s,4)
            G.add_edges_from(sample_missing_edges(G,1))
            writeGraph(G,gname,graph_type="bipartite")
            cmd(["cnfgen","-o",fname,"subsetcard","-i",gname])
