#!/usr/bin/env python
# -*- coding:utf-8 -*-


import random


from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

from ..cnf import CNF, disj, xor, less, greater, geq, leq

@register_cnf_transformation
def Shuffle(F,**kwargs):
    """Reshuffle the given cnf. 

    Returns a formula logically equivalent to the input, a CNF with
    :math:`n` variables and :math:`m` clauses, with the following
    transformations applied in order:

    Parameters
    ----------
    F : CNF 
        formula to be shuffled
    
    variables_permutation: list(string) or 'random', optional 
        the sequence of variables, in their new order. If `'random'`
        then the order is picked at random. If `None` or the parameter
        is not set, then there is no permutation. (default: None)

    polarity_flips: list(-1,1) or 'random', optional 
        This is a :math:`\{-1,1\}^n` vector. If the :math:`i`-th
        entry is -1, all the literals with the :math:`i`-th variable
        change its sign. If `'random'` then theflips are picked at
        random. If `None` or the parameter is not set, then the
        literals are not flipped. (default:  None)
    
    clauses_permutation: list(int) or 'random', optional 
        it is a permutation of [0..m-1]. The resulting clauses are
        reordered according to the permutation. If `'random'` then the
        permutation is picked at random. If `None` or the parameter is
        not set, then the clauses are shuffled. (default:  None)

    """
    variables_permutation = kwargs.pop('variables_permutation',  None)
    polarity_flips        = kwargs.pop('polarity_flips',         None)
    clauses_permutation   = kwargs.pop('clauses_permutation',    None)
    
    # empty cnf
    out=CNF(header='')

    out.header="Reshuffling of:\n\n"+F.header

    # Permute variables
    variables=list(F.variables())
    N=len(variables)

    if variables_permutation == 'random':
        random.shuffle(variables)
    elif variables_permutation is not None:
        assert set(variables_permutation)==set(variables)
        variables = variables_permutation

    for v in variables:
        out.add_variable(v)
    
        
    # polarity flip
    if polarity_flips is None:
        polarity_flips=[1]*N
    elif polarity_flips == 'random':
        polarity_flips=[random.choice([-1,1]) for _ in xrange(N)]
    else:
        assert len(polarity_flips)==N

    #
    # substitution of variables
    #
    substitution=[None]*(2*N+1)
    reverse_idx=dict([(v,i) for (i,v) in enumerate(out.variables(),1)])
    polarity_flips = [None]+polarity_flips

    for i,v in enumerate(F.variables(),1):
        substitution[i]=  polarity_flips[i]*reverse_idx[v]
        substitution[-i]= -substitution[i]

    
    # permutation of clauses
    #
    M=len(F)
    compressed_clauses = None
    if clauses_permutation==None:

        clauses_permutation = range(M)

    elif clauses_permutation == 'random':

        clauses_permutation=range(M)
        random.shuffle(clauses_permutation)

    else:
        assert len(clauses_permutation)==M
        
    # load clauses
    out._constraints = [None]*M
    out._length  = M
    for (old,clause) in enumerate(F._compressed_clauses()):
        out._constraints[clauses_permutation[old]]= disj(*(substitution[l] for l in clause))

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
                            dest='no_variables_permutation',
                            help="No permutation of variables")
        parser.add_argument('--no-clauses-permutation','-c',
                            action='store_true',
                            dest='no_clauses_permutation',
                            help="No permutation of constraints")
    
    @staticmethod
    def transform_cnf(F,args):
        return Shuffle(F,
                       variables_permutation  = None if args.no_variables_permutation else 'random',
                       clauses_permutation    = None if args.no_clauses_permutation   else 'random',
                       polarity_flips         = None if args.no_polarity_flips        else 'random')
