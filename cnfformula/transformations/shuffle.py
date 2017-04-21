#!/usr/bin/env python
# -*- coding:utf-8 -*-


import random

from cnfformula.transformations.expand import Expand

from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

from ..cnf import CNF
from ..cnf import disj, xor
from ..cnf import less, greater, geq, leq, eq
from ..cnf import weighted_eq, weighted_geq


def _shuffle_literals(constraint,substitution):
    """Shuffle the literals in the low level representation of constraints."""
    literals = (substitution[l] for l in constraint)

    if type(constraint)==disj:
        return disj(*literals)

    elif type(constraint) in [xor,eq]:
        return type(constraint)(*literals,value=constraint.value)

    elif type(constraint) in [less, greater, geq, leq]:
        return type(constraint)(*literals,threshold=constraint.threshold)

    elif type(constraint) in [weighted_eq,weighted_geq]:

        offset = sum(-w for (w,v) in constraint if substitution[v]<0)
        terms  = ((w*substitution[v]//abs(substitution[v]),abs(substitution[v])) for (w,v) in constraint)

        if type(constraint) == weighted_eq:
            return weighted_eq(*terms,value=constraint.value+offset)
        elif type(constraint) == weighted_geq:
            return weighted_geq(*terms,threshold=constraint.threshold+offset)
        else:
            ValueError("The constraint type is unknown: {}".format(type(constraint)))
    else:
        raise ValueError("The constraint type is unknown: {}".format(type(constraint)))

@register_cnf_transformation
def Shuffle(F,**kwargs):
    """Reshuffle the given cnf. 

    Returns a formula logically equivalent to the input, a CNF with
    :math:`n` variables and :math:`m` constraints, with the following
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
        change its sign. If `'random'` then the flips are picked at
        random. If `None` or the parameter is not set, then the
        literals are not flipped. (default:  None)
    
    constraints_permutation: list(int) or 'random', optional 
        it is a permutation of [0..m-1]. The resulting constrains are
        reordered according to the permutation. If `'random'` then the
        permutation is picked at random. If `None` or the parameter is
        not set, then the constraints are shuffled. (default:  None)

    """
    variables_permutation   = kwargs.pop('variables_permutation',   None)
    polarity_flips          = kwargs.pop('polarity_flips',          None)
    constraints_permutation = kwargs.pop('constraints_permutation', None)
    
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

    
    # permutation of constraints
    #
    M=len(F._constraints)

    if constraints_permutation is None:

        constraints_permutation = range(M)

    elif constraints_permutation == 'random':

        constraints_permutation=range(M)
        random.shuffle(constraints_permutation)

    else:
        assert len(constraints_permutation)==M
        
    # load clauses
    out._constraints = [None]*M
    out._length  = None
    for (old,cnst) in enumerate(F._constraints):
        out._constraints[constraints_permutation[old]]= _shuffle_literals(cnst,substitution)

    # return the formula
    out.mode_default()
    return out


@register_cnf_transformation_subcommand
class ShuffleCmd:
    """Shuffle 
    """
    name='shuffle'
    description='Permute variables, constraints and polarity of literals at random'

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
        parser.add_argument('--no-constraints-permutation','-c',
                            action='store_true',
                            dest='no_constraints_permutation',
                            help="No permutation of constraints")
    
    @staticmethod
    def transform_cnf(F,args):
        return Shuffle(F,
                       variables_permutation   = None if args.no_variables_permutation   else 'random',
                       constraints_permutation = None if args.no_constraints_permutation else 'random',
                       polarity_flips          = None if args.no_polarity_flips          else 'random')

@register_cnf_transformation_subcommand
class FlipCmd:
    name='flip'
    description='negate all variables in the formula'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def transform_cnf(F, args):

        N=sum(1 for _ in F.variables())
        return Shuffle(F, polarity_flips=[-1]*N)
