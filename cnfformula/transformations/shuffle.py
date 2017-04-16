#!/usr/bin/env python
# -*- coding:utf-8 -*-


import random


from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

from ..cnf import CNF, disj, xor, less, greater, geq, leq


def _shuffle_literals(constraint,substitution):
    """Shuffle the literals in the low level representation of constraints."""
    literals = (substitution[l] for l in constraint)
    if type(constraint)==disj:
        return disj(*literals)
    elif type(constraint)==xor:
        return xor(*literals,value=constraint.value)
    elif type(constraint) in [less, greater, geq, leq]:
        return type(constraint)(*literals,threshold=constraint.threshold)
    else:
        raise ValueError("The constraint type is unknown: {}".format(type(constraint)))
    

@register_cnf_transformation
def Shuffle(cnf,
               variable_permutation=None,
               constraint_permutation=None,
               polarity_flips=None):
    """Reshuffle the given cnf. 

    Returns a formula logically equivalent to the input with the
    following transformations applied in order:

    1. Polarity flips. polarity_flip is a {-1,1}^n vector. If the i-th
    entry is -1, all the literals with the i-th variable change its
    sign.

    2. Variable permutations. variable_permutation is a permutation of
    [vars(cnf)]. All the literals with the old i-th variable are
    replaced with the new i-th variable.

    3. Constraint permutations. constraint_permutation is
    a permutation of [0..m-1]. The resulting clauses are reordered
    according to the permutation.

    """
    
    # empty cnf
    out=CNF(header='')

    out.header="Reshuffling of:\n\n"+cnf.header


    variables=list(cnf.variables())
    N=len(variables)
    M=len(cnf._constraints)

    # variable permutation
    if variable_permutation==None:
        variable_permutation=variables
        random.shuffle(variable_permutation)
    else:
        assert len(variable_permutation)==N

    # polarity flip
    if polarity_flips==None:
        polarity_flips=[random.choice([-1,1]) for x in xrange(N)]
    else:
        assert len(polarity_flips)==N

    #
    # substitution of variables
    #
    for v in variable_permutation:
        out.add_variable(v)

    substitution=[None]*(2*N+1)
    reverse_idx=dict([(v,i) for (i,v) in enumerate(out.variables(),1)])
    polarity_flips = [None]+polarity_flips

    for i,v in enumerate(cnf.variables(),1):
        substitution[i]=  polarity_flips[i]*reverse_idx[v]
        substitution[-i]= -substitution[i]

    #
    # permutation of clauses
    #
    if constraint_permutation==None:
        constraint_permutation=range(M)
        random.shuffle(constraint_permutation)

    # load clauses
    out._constraints = [None]*M
    out._length  = len(cnf)
    for (old,new) in enumerate(constraint_permutation):
        out._constraints[new]=_shuffle_literals(cnf._constraints[old],substitution)
    

    # return the formula
    return out


@register_cnf_transformation_subcommand
class ShuffleCmd:
    """Shuffle 
    """
    name='shuffle'
    description='Permute variables, clauses and polarity of literals at random'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('--no-polarity-flips','-p',
                            action='store_true',
                            dest='no_polarity_flips',
                            help="No polarity flips")
        parser.add_argument('--no-variables-permutation','-v',
                            action='store_true',
                            dest='no_variable_permutation',
                            help="No permutation of variables")
        parser.add_argument('--no-constraint-permutation','-c',
                            action='store_true',
                            dest='no_constraint_permutation',
                            help="No permutation of constraints")
    
    @staticmethod
    def transform_cnf(F,args):
        return Shuffle(F,
                       variable_permutation=None if not args.no_variable_permutation else list(F.variables()),
                       constraint_permutation=None if not args.no_constraint_permutation else range(len(F._clauses)),
                       polarity_flips=None if not args.no_polarity_flips else [1]*len(list(F.variables())))
