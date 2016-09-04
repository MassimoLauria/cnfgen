#!/usr/bin/env python
# -*- coding:utf-8 -*-


import random


from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

from ..cnf import CNF


@register_cnf_transformation
def Shuffle(cnf,
               variable_permutation=None,
               clause_permutation=None,
               polarity_flip=None):
    """ Reshuffle the given cnf. Returns a formula logically
    equivalent to the input with the following transformations
    applied in order:

    1. Polarity flips. polarity_flip is a {-1,1}^n vector. If the i-th
    entry is -1, all the literals with the i-th variable change its
    sign.

    2. Variable permutations. variable_permutation is a permutation of
    [vars(cnf)]. All the literals with the old i-th variable are
    replaced with the new i-th variable.

    3. Clause permutations. clause_permutation is a permutation of
    [0..m-1]. The resulting clauses are reordered according to the
    permutation.
"""
    
    # empty cnf
    out=CNF(header='')

    out.header="Reshuffling of:\n\n"+cnf.header


    variables=list(cnf.variables())
    N=len(variables)
    M=len(cnf)

    # variable permutation
    if variable_permutation==None:
        variable_permutation=variables
        random.shuffle(variable_permutation)
    else:
        assert len(variable_permutation)==N

    # polarity flip
    if polarity_flip==None:
        polarity_flip=[random.choice([-1,1]) for x in xrange(N)]
    else:
        assert len(polarity_flip)==N

    #
    # substitution of variables
    #
    for v in variable_permutation:
        out.add_variable(v)

    substitution=[None]*(2*N+1)
    reverse_idx=dict([(v,i) for (i,v) in enumerate(out.variables(),1)])
    polarity_flip = [None]+polarity_flip

    for i,v in enumerate(cnf.variables(),1):
        substitution[i]=  polarity_flip[i]*reverse_idx[v]
        substitution[-i]= -substitution[i]

    #
    # permutation of clauses
    #
    if clause_permutation==None:
        clause_permutation=range(M)
        random.shuffle(clause_permutation)

    # load clauses
    out._clauses = [None]*M
    for (old,new) in enumerate(clause_permutation):
        out._clauses[new]=tuple( substitution[l] for l in cnf._clauses[old])

    # return the formula
    assert out._check_coherence(force=True)
    return out


@register_cnf_transformation_subcommand
class ShuffleCmd:
    """Shuffle 
    """
    name='shuffle'
    description='Permute variables, clauses and polarity of literals at random'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('--no-polarity-flips','-p',action='store_true',dest='no_polarity_flips',help="No polarity flips")
        parser.add_argument('--no-variables-permutation','-v',action='store_true',dest='no_variable_permutations',help="No permutation of variables")
        parser.add_argument('--no-clauses-permutation','-c',action='store_true',dest='no_clause_permutations',help="No permutation of clauses")
    
    @staticmethod
    def transform_cnf(F,args):
        return Shuffle(F,
                       variable_permutation=None if not args.no_variable_permutations else list(F.variables()),
                       clause_permutation=None if not args.no_clause_permutations else range(len(F)),
                       polarity_flip=None if not args.no_polarity_flips else [1]*len(list(F.variables())))
