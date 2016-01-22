#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of XORification with recycling
"""

from cnfformula.cnf import CNF
from cnfformula.cmdline import BipartiteGraphHelper

import cnfformula.cmdline
import cnfformula.families

from itertools import combinations,product

import random

@cnfformula.families.register_cnf_generator
def XORificationWithRecycling(formula, m, M):
    """XORification with recycling 

    Arguments:
    - `formula`: original formula
    - `m`: #vars in new formula
    - `M`: list of lists of new variables per variable

    References
    ----------
    .. [1] The ultimate tradeoff paper?

    """
    dmin = min(map(len,M))
    dmax = max(map(len,M))
    s_cnt = "{0}".format(dmin) if dmin==dmax else "between {0} and {1}".format(dmin,dmax)
    new_formula=CNF()
    new_formula.header="{0} XORified with {1} new variables per variable\n".format(formula.header,s_cnt)

    for i in xrange(m): new_formula.add_variable(i)

    def dfs(C, idx, curclause):
        if idx == len(C):
            curclause_sorted = list(curclause)
            curclause_sorted.sort(key=lambda (pol,x) : x)
            curclause_reduced = []
            for pol,x in curclause_sorted:
                if len(curclause_reduced) > 0 and (pol,x) == curclause_reduced[-1]: continue
                elif len(curclause_reduced) > 0 and (not pol,x) == curclause_reduced[-1]: return # always satisfied
                else: curclause_reduced.append((pol,x))
            new_formula.add_clause(curclause_reduced)
        else:
            replacement = M[abs(C[idx])-1]
            for msk in range(2 ** len(replacement)):
                bitcount = 0
                for i in range(len(replacement)):
                    if msk & (1<<i): bitcount += 1
                # rule out assignment `msk`
                if (bitcount % 2 == 0) == (C[idx] > 0):
                    for i in range(len(replacement)):
                        curclause.append((not bool(msk & (1<<i)), replacement[i]))
                    dfs(C, idx+1, curclause)
                    for i in range(len(replacement)):
                        curclause.pop()

    for cls in formula._clauses: dfs(cls, 0, [])

    return new_formula
