#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Random CNF Formulas
"""

import itertools
import random

from cnfformula.cnf import CNF

import cnfformula.cmdline
import cnfformula.families



def clause_satisfied(cls,assignments):
    """Test whether a clause is satisfied by all assignments

Test if clauses `cls` is satisfied by all assigment in the
list assignments.
"""
    for assignment in assignments:

        if  any( assignment.has_key(var) and polarity == assignment[var]
                 for (polarity, var) in cls):
            continue

        else:
            return False

    return True

def sample_clauses(k, indices, m, planted_assignments):
    clauses = set()
    t = 0
    while len(clauses)<m and t < 10*m:
        t += 1

        cls = tuple((random.choice([True,False]),'x_{0}'.format(i))
                    for i in sorted(random.sample(indices,k)))

        if clause_satisfied(cls,planted_assignments):
            clauses.add(cls)
        
    if len(clauses)<m:
        return sample_clauses_dense(k, indices, m, planted_assignments)
    return clauses

def all_clauses(k, indices, planted_assignments):
    for domain in itertools.combinations(indices, k):
        for polarity in itertools.product([True,False], repeat=k):

            cls =  zip(polarity,('x_{0}'.format(i) for i in domain))
            if clause_satisfied(cls, planted_assignments):
                yield cls

                
def sample_clauses_dense(k, indices, m, planted_assignments):
    return random.sample(list(all_clauses(k, indices, planted_assignments)), m)

@cnfformula.families.register_cnf_generator
def RandomKCNF(k, n, m, seed=None, planted_assignments=[]):
    """Build a random k-CNF

    Sample :math:`m` clauses over :math:`n` variables, each of width
    :math:`k`, uniformly at random. The sampling is done without
    repetition, meaning that whenever a randomly picked clause is
    already in the CNF, it is sampled again.

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

    planted_assignments : iterable(dict), optional 
       a set of total/partial assigments such that all clauses in the formula 
       will be satisfied by all of them.

    Returns
    -------
    a CNF object

    Raises
    ------
    ValueError
        when some paramenter is negative, or when k>n.

    """
    if seed:
        random.seed(seed)


    if n<0 or m<0 or k<0:
        raise ValueError("Parameters must be non-negatives.")

    if k>n:
        raise ValueError("Clauses cannot have more {} literals.".format(n))

    F = CNF()
    F.header = "Random {}-CNF over {} variables and {} clauses\n".format(k,n,m) + F.header

    indices = xrange(1,n+1)
    for i in indices:
        F.add_variable('x_{0}'.format(i))
    try:
        for clause in sample_clauses(k, indices, m, planted_assignments):
            F.add_clause(list(clause), strict=True)
    except ValueError:
        raise ValueError("There are fewer clauses available than the number requested")

    return F


@cnfformula.cmdline.register_cnfgen_subcommand
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
        return RandomKCNF(args.k, args.n, args.m)
