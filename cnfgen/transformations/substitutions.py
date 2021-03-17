#!/usr/bin/env python
# -*- coding:utf-8 -*-

from itertools import combinations, product, permutations
from copy import copy

from cnfgen.localtypes import positive_int, any_int, one_of_values
from cnfgen.formula.cnf import CNF
from cnfgen.graphs import BipartiteGraph

#
# Utilities
#

def add_description(F, text):
    """Add the description of a transformation

    Parameters
    ----------
    F : cnfgen.CNF
        formula that gets the new description
    text : str
        text of the description"""
    i = 1
    while 'transformation {}'.format(i) in F.header:
        i += 1
    F.header['transformation {}'.format(i)] = text


def apply_substitution(formula, subst):
    """Apply the substitution ``f`` to a formula

    Applies a substitution to a formula and produces a sequence
    of clauses.

    Parameters
    ----------
    formula : cnfgen.CNF
        formula that gets the new description
    subst : function
        a function that maps literals to sequences of clauses
    """
    # Load original variable names
    #
    # For n variables we get
    #
    # substitution  = [None, F1, F2,..., Fn, -Fn, -F(n-1), ..., -F2, -F1]
    #
    N = formula.number_of_variables()
    substitutions = [None] * (2 * N + 1)

    # Transform all possible literals
    for i in range(1, N+1):
        substitutions[i] = subst(i)
        substitutions[-i] = subst(-i)

    # build and add new clauses
    for clause in formula:

        # a substituted clause is the OR of the CNF for the literals
        domains = [substitutions[lit] for lit in clause]
        domains = tuple(domains)
        # apply distribution
        block = (
            tuple([lit for clause in clause_tuple for lit in clause])
            for clause_tuple in product(*domains)
        )
        yield from block


#
# Substitutions
#
def FlipPolarity(F):
    """Flip the polarity of variables

    F : cnfgen.CNF
        formula
    """
    newF = CNF()
    newF.header = copy(F.header)
    add_description(newF,"All polarities have been flipped")

    def subst(lit):
        return [[-lit]]
    newF.add_clauses_from(apply_substitution(F, subst))
    return newF


def XorSubstitution(F, k):
    """Apply Xor substitution of rank ``k``

    F : cnfgen.CNF
        formula
    k : int
        arity of the xor substitution
    """
    positive_int(k, 'k')
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='{{'+name+'}}^{}')
    add_description(newF, "Substitution with XOR of arity {}".format(k))

    def xorify(lit):
        polarity = 1 if lit > 0 else 0
        nvars = [(abs(lit)-1)*k + i for i in range(1, k+1)]
        temp = CNF()
        temp.add_parity(nvars, polarity)
        return list(temp)

    newF.add_clauses_from(
        apply_substitution(F, xorify))

    return newF

def ExactlyOneSubstitution(F, k):
    """Apply exactly-oine substitution of rank ``k``

    F : cnfgen.CNF
        formula
    k : int
        arity of the xor substitution
    """
    positive_int(k, 'k')
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='{{'+name+'}}^{}')
    add_description(newF, "Substitution with exaclty-one, of arity {}".format(k))

    def oneify(lit):
        nvars = [(abs(lit)-1)*k + i for i in range(1, k+1)]
        temp = CNF()
        if lit > 0:
            temp.add_linear(nvars, '==', 1)
        else:
            for i in range(len(nvars)):
                nvars[i] *= -1
                temp.add_clause(nvars)
                nvars[i] *= -1
        return list(temp)

    newF.add_clauses_from(
        apply_substitution(F, oneify))

    return newF


def LinearSubstitution(F, k, op, C):
    """Linear substitution of rank ``k``

    Substitute each variable x(i) with a linear form

    x(i,1) + x(i,2) + ... x(i,k)  op  constant

    F : cnfgen.CNF
        formula
    k : int
        arity of the linear substitution
    op : str
        an operator among
    C : int
        constant
    """
    opchoices = ['==', '<', '>', '<=', '>=', '!=']
    positive_int(k, 'k')
    one_of_values(op, 'op', opchoices)
    any_int(C, 'C')

    i = opchoices.index(op)
    negop = opchoices[-i-1]
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='{{'+name+'}}^{}')
    desc = "Substitution x --> x1 + x2 + ... x{} {} {}".format(k, op, C)
    add_description(newF, desc)

    def linear(lit):
        nvars = [(abs(lit)-1)*k + i for i in range(1, k+1)]
        temp = CNF()
        if lit > 0:
            temp.add_linear(nvars, op, C)
        else:
            temp.add_linear(nvars, negop, C)
        return list(temp)

    newF.add_clauses_from(
        apply_substitution(F, linear))

    return newF


def MajoritySubstitution(F, k):
    """Apply Majority substitution of rank ``k``

    F : cnfgen.CNF
        formula
    k : int
        arity of the majority substitution
    """
    positive_int(k, 'k')
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='{{'+name+'}}^{}')
    add_description(newF, "Substitution with majority of arity {}".format(k))

    def majorify(lit):
        nvars = [(abs(lit)-1)*k + i for i in range(1, k+1)]
        temp = CNF()
        if lit > 0:
            temp.add_loose_majority(nvars)
        else:
            temp.add_strict_minority(nvars)
        return list(temp)

    newF.add_clauses_from(
        apply_substitution(F, majorify))

    return newF


def AllEqualSubstitution(F, k, invert=False):
    """Apply all-equals substitution of rank ``k``

    F : cnfgen.CNF
        formula
    k : int
        arity of the all-equals substitution
    invert : bool
        apply the not-all-equal substitution
    """
    positive_int(k, 'k')
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='{{'+name+'}}^{}')
    if invert:
        add_description(newF, "Substitution with not-all-equals of arity {}".format(k))
    else:
        add_description(newF, "Substitution with not-all-equals of arity {}".format(k))

    def aesubst(lit):
        nvars = [(abs(lit)-1)*k + i for i in range(1, k+1)]
        clauses = []
        if invert:
            lit *= -1
        if lit > 0:
            # one true implies all true
            clauses = []
            clauses.append([nvars[0],-nvars[-1]])
            clauses.extend([[-nvars[i-1], nvars[i]] for i in range(1,len(nvars))])
        else:
            # at least one true
            clauses = [nvars, [-v for v in nvars]]
        return clauses

    newF.add_clauses_from(
        apply_substitution(F, aesubst))

    return newF

def NotAllEqualSubstitution(F, k):
    """Apply not-all-equals substitution of rank ``k``

    F : cnfgen.CNF
        formula
    k : int
        arity of the not-all-equals substitution
    """
    positive_int(k, 'k')
    return AllEqualSubstitution(F, k, invert=True)


def OrSubstitution(F, k):
    """Apply Or substitution of rank ``k``

    F : cnfgen.CNF
        formula
    k : int
        arity of the or substitution
    """
    positive_int(k, 'k')
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='{{'+name+'}}^{}')
    add_description(newF, "Substitution with OR of arity {}".format(k))

    def orify(lit):
        nvars = [(abs(lit)-1)*k + i for i in range(1, k+1)]
        if lit > 0:
            return [nvars]
        else:
            return [[-nvar] for nvar in nvars]

    newF.add_clauses_from(
        apply_substitution(F, orify))

    return newF

def AndSubstitution(F, k):
    """Apply AND substitution of rank ``k``

    F : cnfgen.CNF
        formula
    k : int
        arity of the or substitution
    """
    positive_int(k, 'k')
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='{{'+name+'}}^{}')
    add_description(newF, "Substitution with AND of arity {}".format(k))

    def andify(lit):
        nvars = [(abs(lit)-1)*k + i for i in range(1, k+1)]
        if lit > 0:
            return [[nvar] for nvar in nvars]
        else:
            return [-nvar for nvar in nvars]

    newF.add_clauses_from(
        apply_substitution(F, andify))

    return newF


def IfThenElseSubstitution(F):
    """Apply if-then-else substitution

    Each original variable is substituted with a function on three
    new variables x,y,z which is

    if x then y else z

    F : cnfgen.CNF
        formula
    """
    newF = CNF()
    newF.header = copy(F.header)
    N = F.number_of_variables()
    for name in F.all_variable_labels():
        newF.new_variable('{{'+name+'}}^{i}')
    for name in F.all_variable_labels():
        newF.new_variable('{{'+name+'}}^{t}')
    for name in F.all_variable_labels():
        newF.new_variable('{{'+name+'}}^{e}')
    add_description(newF, "If-Then-Else substitution formula")

    def ite(lit):
        var = abs(lit)
        sign = lit//var
        return [[-var, sign*(N+var)], [var, sign*(2*N+var)]]

    newF.add_clauses_from(
        apply_substitution(F, ite))
    return newF


def FormulaLifting(F, k):
    """Formula lifting: Y variable select X values

    F : cnfgen.CNF
        a formula
    k : int
        arity of the lifting
    """
    positive_int(k, 'k')
    newF = CNF()
    newF.header = copy(F.header)
    for name in F.all_variable_labels():
        newF.new_block(k, label='X_{{'+name+'}}^{}')
        newF.new_block(k, label='Y_{{'+name+'}}^{}')
    add_description(newF, "Lifting with selectors over {} values".format(k))

    N = newF.number_of_variables()
    # cycle on the blocks of Y variables
    for y in range(k+1, N+1, 2*k):
        newF.add_linear([y+i for i in range(k)], '==', 1)

    def lift(lit):
        sign = lit//abs(lit)
        oldvar = abs(lit)
        Xoff = (oldvar-1)*2*k
        Yoff = (oldvar-1)*2*k + k
        return [[-(Yoff + i), sign*(Xoff + i)] for i in range(1, k+1)]

    newF.add_clauses_from(
        apply_substitution(F, lift))

    return newF



def AtLeastKSubstitution(F, N, k):
    """Substitution: at least ``k`` true variables out of ``N`` copies"""
    return LinearSubstitution(F, N, '>=', k)


def AtMostKSubstitution(F, N, k):
    """Substitution: at most ``k`` true variables out of ``N`` copies"""
    return LinearSubstitution(F, N, '<=', k)


def ExactlyKSubstitution(F, N, k):
    """Substitution: exactly ``k`` true variables out of ``N`` copies"""
    return LinearSubstitution(F, N, '==', k)


def AnythingButKSubstitution(F, N, k):
    """Substitution: anything bit ``C`` true variables out of ``N`` copies"""
    return LinearSubstitution(F, N, '!=', k)


def VariableCompression(F, B, function):
    """Vabiable compression transformation

    The original variable are substituted with the XOR (or MAJ) of
    a subset of a new set of variables. The mapping between the
    original variables and the new ones is given by a bipartite graph

    Parameters
    ----------
    F : CNF
        the original cnf formula
    B : cnfgen.graphs.BipartiteGraph
        a bipartite graph. The left side must have the number of
        vertices equal to the number of original variables
    func: string
        Select which faction is used for the compression.
        It must be one among 'xor' or 'maj'
    """
    one_of_values(function, 'function', ['xor', 'maj'])
    B = BipartiteGraph.normalize(B)

    if B.left_order() != F.number_of_variables():
        raise ValueError(
            "Left side of graph B must have size equal to the number of variables in F")

    newF = CNF()
    newF.header = copy(F.header)

    L = B.left_order()
    R = B.right_order()
    newF.update_variable_number(R)
    desc = "Variable {}-compression from {} to {} variables".format(function, L, R)
    add_description(newF, desc)

    def applyxor(lit):
        nvars = B.right_neighbors(abs(lit))
        polarity = 1 if lit > 0 else 0
        temp = CNF()
        temp.add_parity(nvars, polarity)
        return list(temp)

    def applymaj(lit):
        nvars = B.right_neighbors(abs(lit))
        temp = CNF()
        if lit > 0:
            temp.add_loose_majority(nvars)
        else:
            temp.add_strict_minority(nvars)
        return list(temp)

    if function == 'xor':
        newF.add_clauses_from(apply_substitution(F, applyxor))
    elif function == 'maj':
        newF.add_clauses_from(apply_substitution(F, applymaj))
    else:
        raise RuntimeError("Function {} not supported for compression".format(func))

    return newF
