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
    """Apply Xor substitution or rank ``k``

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


def OrSubstitution(F, k):
    """Apply Or substitution or rank ``k``

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


class IfThenElseSubstitution(BaseSubstitution):
    """Transformed formula: substitutes variable with a three variables
    if-then-else
    """
    def __init__(self, cnf):
        """Build a new CNF obtained by substituting an if-then-else to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        """
        super(IfThenElseSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "If-Then-Else substitution formula")

    def transform_a_literal(self, polarity, varname):
        """Substitute a positive literal with an if then else statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: variable to be substituted

        Returns: a list of clauses
        """
        X = "{{{}}}^0".format(varname)
        Y = "{{{}}}^1".format(varname)
        Z = "{{{}}}^2".format(varname)

        return [[(False, X), (polarity, Y)], [(True, X), (polarity, Z)]]


class MajoritySubstitution(BaseSubstitution):
    """Transformed formula: substitutes variable with a Majority
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a Majority to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        super(MajoritySubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with Majority of {}".format(self._rank))

    def transform_a_literal(self, polarity, varname):
        """Substitute a positive literal with Loose Majority,
        and negative literals with Strict Minority.

        Parameters
        ----------
        polarity : bool
            polarity of the literal
        varname  : string
            variable to be substituted

        Returns: a list of clauses
        """

        variables = ["{{{}}}^{}".format(varname, i) for i in range(self._rank)]

        threshold = (self._rank + 1) // 2  # loose majority
        if polarity:
            return list(self.greater_or_equal_constraint(variables, threshold))
        else:
            return list(self.less_than_constraint(variables, threshold))




class AllEqualSubstitution(BaseSubstitution):
    """Transformed formula: substitutes variable with 'all equals'
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting 'all equals' to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        super(AllEqualSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with Equality of {}".format(self._rank))

    def transform_a_literal(self, polarity, varname):
        """Substitute a positive literal with an 'all equal' statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = ["{{{}}}^{}".format(varname, i) for i in range(self._rank)]
        pairs = permutations(names, 2)
        if polarity:
            return [[(False, a), (True, b)] for a, b in pairs
                    ]  # a true variable implies all the others to true.

        else:
            return [[(False, a) for a in names],
                    [(True, a)
                     for a in names]]  # at least a true and a false variable.


class NotAllEqualSubstitution(BaseSubstitution):
    """Transformed formula: substitutes variable with 'not all equals'
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting 'not all equals' to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        super(NotAllEqualSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with NonEquality of {}".format(self._rank))

    def transform_a_literal(self, polarity, varname):
        """Substitute a positive literal with an 'not all equal' statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        return AllEqualSubstitution.transform_a_literal(
            self, not polarity, varname)



class FormulaLifting(BaseSubstitution):
    """Formula lifting: Y variable select X values
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by lifting procedures

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        positive_int(rank, 'rank')
        BaseSubstitution.__init__(self, cnf)
        self._rank = rank
        for name in cnf.all_variable_labels():
            self.new_block(rank, label='X_{{'+name+'}}^{}')
            self.new_block(rank, label='Y_{{'+name+'}}^{}')

        self.add_transformation_description(
            "Lifting with selectors over {} values".format(self._rank))
        self._apply()

    def transform_variable_preamble(self, variable):
        """Additional clauses for each lifted variable

        Arguments:
        - `name`:     variable to be substituted

        Returns: a list of clauses
        """
        Yoff = (variable-1)*2*self._rank + self._rank
        temp = CNF()
        temp.add_linear([Yoff+i for i in range(1,self._rank+1)], '==', 1)
        return list(temp)

    def transform_a_literal(self, lit):
        """Lift a literal

        Parameters
        ----------
        lit : literal to substitute

        Returns
        -------
        a list of clauses
        """
        sign = lit//abs(lit)
        oldvar = abs(lit)
        Xoff = (oldvar-1)*2*self._rank
        Yoff = (oldvar-1)*2*self._rank + self._rank
        return [[-(Yoff + i), sign*(Xoff + i)] for i in range(1, self._rank+1)]


class ExactlyOneSubstitution(BaseSubstitution):
    """Transformed formula: exactly one variable is true
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained substituting all variables with
        'exactly one' function.

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each substitution
        """
        self._rank = rank

        super(ExactlyOneSubstitution, self).__init__(cnf)

        self.add_transformation_description(
            "Substitution with Exactly one of {}".format(self._rank))

    def transform_a_literal(self, polarity, varname):
        """Substitute a literal with an \"Exactly One\"

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        clauses = []
        varnames = [
            "X_{{{}}}^{}".format(varname, i) for i in range(self._rank)
        ]

        if polarity:
            # at least one variable is true
            clauses.append([(True, name) for name in varnames])
            # no two variables are true
            for (n1, n2) in combinations(varnames, 2):
                clauses.append([(False, n1), (False, n2)])
        else:
            # if all variables but one are false, the other must be false
            for name in varnames:
                clauses.append([(False, name)] +
                               [(True, other)
                                for other in varnames if other != name])
        return clauses


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



    # def __init__(self, cnf):
    #     """Build a new CNF obtained by flipping the polarity of the variables

    #     Parameters
    #     ----------
    #     cnf : a CNF object
    #     """
    #     BaseSubstitution.__init__(self, cnf)
    #     self.add_transformation_description("All polarities have been flipped")
    #     self._apply()

    # def transform_a_literal(self, lit):
    #     """Substitute a positive literal with an OR,
    #     and negative literals with its negation.

    #     Arguments:
    #     - `polarity`: polarity of the literal
    #     - `varname`: fariable to be substituted

    #     Returns: a list of clauses
    #     """
    #     return [[-lit]]


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
