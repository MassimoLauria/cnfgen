#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Random CNF Formulas

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""


from cnfformula import CNF
from cnfformula.cmdline import is_formula_cmdhelper    



def RandomKCNF(k, n, m, seed=None):
    """Build a random k-CNF

    Sample :math:`m` clauses over :math:`n` variables, each of width
    :math:`k`, uniformly at random. The sampling is done without
    repetition, meaning that whenever a randomly picked clause is
    already in the CNF, it is sampled again.

    If the sampling takes too long (i.e. the space of possible clauses
    is too small) then a ``RuntimeError`` is raised.

    Parameters
    ----------
    k : int
       width of each clause
    
    n : int
       number of variables to choose from. The resulting CNF object 
       will contain n variables even if some are not mentioned in the clauses.
    
    m : int
       number of clauses to generate
    
    seed : hashable object
       seed of the random generator

    Returns
    -------
    a CNF object

    Raises
    ------
    ValueError 
        when some paramenter is negative, or when k>n.
    RuntimeError
        the formula is too dense for the simple sampling process.

    """
    import random
    if seed:
        random.seed(seed)


    if k>n or n<0 or m<0 or k<0:
        raise ValueError("Parameters must be non-negatives.")
        
    F = CNF()
    F.header = "Random {}-CNF over {} variables and {} clauses\n".format(k,n,m) + F.header
    
    for variable in xrange(1,n+1):
        F.add_variable(variable)

    clauses = set()
    t = 0
    while len(clauses)<m and t < 10*m:
        t += 1
        clauses.add(tuple((random.choice([True,False]),x+1)
                      for x in sorted(random.sample(xrange(n),k))))
    if len(clauses)<m:
        raise RuntimeError("Sampling is taking too long. Maybe the requested formula is too dense.")
    for clause in clauses:
        F.add_clause(list(clause))

    return F
 


class RandCmdHelper(object):
    """Command line helper for random formulas
    """
    name='randkcnf'
    description='random k-CNF'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,help="clause width")
        parser.add_argument('n',metavar='<n>',type=int,help="number of variables")
        parser.add_argument('m',metavar='<m>',type=int,help="number of clauses")

    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        return RandomKCNF(args.k,args.n,args.m)


assert is_formula_cmdhelper(RandCmdHelper)
