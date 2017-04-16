#!/usr/bin/env python
# -*- coding:utf-8 -*-


import random


from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

from ..cnf import CNF, disj, xor, less, greater, geq, leq


@register_cnf_transformation
def Expand(cnf):
    """Expand constraint into clauses.

    Returns a formula logically equivalent to the input in which all
    internal constraints are memorized as clauses.

    """
    
    # empty cnf
    out=CNF(header=cnf.header)

    for v in cnf.variables():
        out.add_variable(v)

    out.mode_unchecked()

    out._constraints = list(cnf._compressed_clauses())
    out._length  = len(out._constraints)

    out._check_coherence()
    out.mode_default()
    # return the formula
    return out


@register_cnf_transformation_subcommand
class ExpandCmd:
    """Expand 
    """
    name='expand'
    description='Expand constraints into clauses'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def transform_cnf(F,args):
        return Expand(F)
