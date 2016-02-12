#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Collection of XORified pyramid formulas.
"""

from cnfformula.cnfgen import command_line_utility as cmd
from cnfformula.batches import register_cnf_batch

@register_cnf_batch
class PyramidXO2(object):

    name='pyrxor2-100'
    description='XOR-ified pebble formula on pyramids of height 10,20,..,100 '

    random_seed = 734841396579
    
    @classmethod
    def run(cls):

        print("""Generating pebbling formula over pyramid graphs. 

In each formula we substitute variables with XOR of two distinct
corresponding variables. """)

        for h in xrange(10,101,10):
            fname = "pyrxor2h{}.cnf".format(h)
            print("-- "+ fname)
            cmd(["cnfgen","-o",fname,"-T","xor","-Ta","2","peb","--pyramid",str(h)])
