#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Collection of XORified pyramid formulas.
"""

from cnfformula.cnfgen import command_line_utility
from cnfformula.batches import register_cnf_batch

@register_cnf_batch
class PyramidXO2(object):

    name='pyrxor2-100'
    description='XOR-ified pebble formula on pyramids of height 10,20,..,100 '

    random_seed = 734841396579
    
    @classmethod
    def run(cls):

        for h in xrange(2,10):
            command_line_utility(["cnfgen","-o","pyrxor2-{}".format(h),"-T","xor","-Ta","2","peb","--pyramid",h])
