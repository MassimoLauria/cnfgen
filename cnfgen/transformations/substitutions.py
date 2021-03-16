#!/usr/bin/env python
# -*- coding:utf-8 -*-

from itertools import combinations, product, permutations
from copy import copy

from cnfgen.localtypes import positive_int
from cnfgen.formula.cnf import CNF

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




class BaseSubstitution(CNF):
    """Apply a substitution to a formula
    """
    def __init__(self, cnf, new_variables=None):
        """Build a new CNF substituting variables

        Arguments:
        - `cnf`: the original cnf
        """
        self._orig_cnf = cnf
        CNF.__init__(self)
        self.header = copy(cnf.header)


    def _apply(self):
        """Apply the substitutions

        This should be called after setting up the lifted variables
        """
        # Load original variable names
        #
        # For n variables we get
        #
        # substitution  = [None, F1, F2,..., Fn, -Fn, -F(n-1), ..., -F2, -F1]
        #
        cnf = self._orig_cnf
        N = cnf.number_of_variables()
        substitutions = [None] * (2 * N + 1)

        # Add the clauses additional clauses per variable
        for var in range(1, N+1):
            self.add_clauses_from(self.transform_variable_preamble(var))

        # Transform all possible literals
        for i in range(1, N+1):
            substitutions[i] = self.transform_a_literal(i)
            substitutions[-i] = self.transform_a_literal(-i)

        # build and add new clauses
        for orig_cls in cnf:

            # a substituted clause is the OR of the CNF for the literals
            domains = [substitutions[lit] for lit in orig_cls]
            domains = tuple(domains)
            # apply distribution
            block = (
                tuple([lit for clause in clause_tuple for lit in clause])
                for clause_tuple in product(*domains)
            )

            self.add_clauses_from(block)


    def add_transformation_description(self, description):
        i = 1
        while 'transformation {}'.format(i) in self.header:
            i += 1
        self.header['transformation {}'.format(i)] = description

    def transform_variable_preamble(self, var):
        """Additional clauses for each variable

        Arguments:
        - `name`:     variable to add clauses for

        Returns: a list of clauses
        """
        return []

    def transform_a_literal(self, lit):
        """Substitute a literal with the transformation function

        Arguments:
        - `lit`:     literal to be substituted

        Returns: a list of clauses
        """
        return [[lit]]






class AtLeastKSubstitution(BaseSubstitution):
    """Transformed formula: at least k variables are true
    """
    def __init__(self, cnf, N, K):
        """Build a new CNF obtained substituting all variables with
        'at least k' function.

        Arguments:
        - `cnf`: the original cnf
        - `N`: how many variables in each substitution
        - `K`: at least how many variables must be true
        """
        self._cnf = cnf
        self._N = N
        self._K = K

        if N < 0:
            raise ValueError("N must be a non-negative integer")
        if not isinstance(K, int):
            raise ValueError("K must be an integer value")

        super(AtLeastKSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with At Least {} of {}".format(self._K, self._N))

    def transform_a_literal(self, polarity, varname):
        """Substitute a literal with an \"At Least K of N\"

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        K = self._K
        clauses = []
        varnames = ["X_{{{}}}^{}".format(varname, i) for i in range(self._N)]

        if polarity:
            # at least k variables are true
            for clause in self._cnf.greater_or_equal_constraint(varnames, K):
                clauses.append(clause)
        else:
            # at most k-1 variables are true
            for clause in self._cnf.less_or_equal_constraint(varnames, K - 1):
                clauses.append(clause)
        return clauses


class AtMostKSubstitution(BaseSubstitution):
    """Transformed formula: at most k variables are true
    """
    def __init__(self, cnf, N, K):
        """Build a new CNF obtained substituting all variables with
        'at most k' function.

        Arguments:
        - `cnf`: the original cnf
        - `N`: how many variables in each substitution
        - `K`: at most how many variables must be true
        """
        self._cnf = cnf
        self._N = N
        self._K = K

        if N < 0:
            raise ValueError("N must be a non-negative integer")
        if not isinstance(K, int):
            raise ValueError("K must be an integer value")

        super(AtMostKSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with At Most {} of {}".format(self._K, self._N))

    def transform_a_literal(self, polarity, varname):
        """Substitute a literal with an \"At Least K of N\"

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        K = self._K
        clauses = []
        varnames = ["X_{{{}}}^{}".format(varname, i) for i in range(self._N)]

        if polarity:
            # at most k variables are true
            for clause in self._cnf.less_or_equal_constraint(varnames, K):
                clauses.append(clause)
        else:
            # at least k+1 variables are true
            for clause in self._cnf.greater_or_equal_constraint(
                    varnames, K + 1):
                clauses.append(clause)
        return clauses


class ExactlyKSubstitution(BaseSubstitution):
    """Transformed formula: exactly k variables are true
    """
    def __init__(self, cnf, N, K):
        """Build a new CNF obtained substituting all variables with
        'exactly K' function.

        Arguments:
        - `cnf`: the original cnf
        - `N`: how many variables in each substitution
        - `K`: exactly how many variables must be true
        """
        self._cnf = cnf
        self._N = N
        self._K = K

        if N < 0:
            raise ValueError("N must be a non-negative integer")
        if not isinstance(K, int):
            raise ValueError("K must be an integer value")

        super(ExactlyKSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with Exactly {} of {}".format(self._K, self._N))

    def transform_a_literal(self, polarity, varname):
        """Substitute a literal with an \"Exactly K of N\"

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        K = self._K
        clauses = []
        varnames = ["X_{{{}}}^{}".format(varname, i) for i in range(self._N)]

        if polarity:
            # exactly k variables are true
            for clause in self._cnf.equal_to_constraint(varnames, K):
                clauses.append(clause)
        else:
            # any number different from k of true variables
            for clause in self._cnf.not_equal_to_constraint(varnames, K):
                clauses.append(clause)
        return clauses


class AnythingButKSubstitution(BaseSubstitution):
    """Transformed formula: anything but k variables are true
    """
    def __init__(self, cnf, N, K):
        """Build a new CNF obtained substituting all variables with
        'anything but k' function.

        Arguments:
        - `cnf`: the original cnf
        - `N`: how many variables in each substitution
        - `K`: how many variables will cause falsity
        """
        self._cnf = cnf
        self._N = N
        self._K = K

        if N < 0:
            raise ValueError("N must be a non-negative integer")
        if not isinstance(K, int):
            raise ValueError("K must be an integer value")

        super(AnythingButKSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with anything but {} of {}".format(self._K, self._N))

    def transform_a_literal(self, polarity, varname):
        """Substitute a literal with an \"Anything but K of N\"

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        K = self._K
        clauses = []
        varnames = ["X_{{{}}}^{}".format(varname, i) for i in range(self._N)]

        if polarity:
            # any number different from k of true variables
            for clause in self._cnf.not_equal_to_constraint(varnames, K):
                clauses.append(clause)
        else:
            # anything but k variables are true
            for clause in self._cnf.equal_to_constraint(varnames, K):
                clauses.append(clause)
        return clauses





class VariableCompression(BaseSubstitution):
    """Vabiable compression transformation

    The original variable are substituted with the XOR (or MAJ) of
    a subset of a new set of variables (usually smaller).
    """

    _name_vertex_dict = {}
    _pattern = None
    _function = None

    def __init__(self, cnf, B, function='xor'):
        """Build a new CNF obtained by substituting a XOR to the
        variables of the original CNF.

        Parameters
        ----------
        cnf : CNF
            the original cnf formula
        B : cnfgen.graphs.BipartiteGraph
            a bipartite graph. The left side must have the number of
            vertices equal to the number of original variables

        function: string
            Select which faction is used for the compression. It must
            be one among 'xor' or 'maj'.

        """
        if function not in ['xor', 'maj']:
            raise ValueError(
                "Function specification for variable compression must be either 'xor' or 'maj'."
            )

        Left, Right = B.parts()

        if len(Left) != len(list(cnf.variables())):
            raise ValueError(
                "Left side of the graph must match the variable numbers of the CNF."
            )

        self._pattern = B
        self._function = function
        for n, v in zip(cnf.variables(), Left):
            self._name_vertex_dict[n] = v

        super(VariableCompression, self).__init__(
            cnf, new_variables=["Y_{{{0}}}".format(i) for i in Right])

        self.add_transformation_description(
            "Variable {}-compression from {} to {} variables".format(
                function, len(Left), len(Right)))

    def transform_a_literal(self, polarity, varname):
        """Substitute a literal with a (negated) XOR

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: variable to be substituted

        Returns: a list of clauses
        """
        varname = self._name_vertex_dict[varname]
        local_vars = self._pattern.right_neighbors(varname)
        local_names = ["Y_{{{0}}}".format(i) for i in local_vars]

        if self._function == 'xor':

            return list(self.parity_constraint(local_names, polarity))

        elif self._function == 'maj':

            threshold = (len(local_names) + 1) // 2  # loose majority

            if polarity:
                return list(
                    self.greater_or_equal_constraint(local_names, threshold))
            else:
                return list(self.less_than_constraint(local_names, threshold))

        else:
            raise RuntimeError(
                "Error: variable compression with invalid function")
