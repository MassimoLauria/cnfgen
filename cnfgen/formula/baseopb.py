#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""The implementaton of the basic CNF object
"""

from functools import reduce
from operator import mul
from itertools import product
from inspect import isgenerator

from collections import OrderedDict
from cnfgen.info import info

from cnfgen.localtypes import non_negative_int

class ConstraintsView:
    """Object that represents a list of constraints

Useful to provide some read only operations to the list of causes of
a formula"""
    def __init__(self,F):
        """Create a view of the constraints of ``F``"""
        self.F = F
        self.data = F._constraints

    def __len__(self):
        """Number of clauses in the formula
        """
        return len(self.data)

    def __iter__(self):
        """Number of clauses in the formula
        """
        return iter(self.data)

    def __eq__(self,other):
        if isinstance(other, BaseOPB):
            return self.data == other._constraints
        elif isinstance(other, ConstraintsView):
            return self.data == other.data
        else:
            return self.data == other

    def __getitem__(self, idx):
        """Number of clauses in the formula
        """
        if isinstance(idx, slice):
            return self.data[idx]
        elif isinstance(idx, int):
            return self.data[idx][:]
        else:
            raise TypeError("Invalid type for an index")

    def __str__(self):
        return 'ConstraintsView({})'.format(self.data)

    def __repr__(self):
        return 'ConstraintsView({})'.format(self.data)



def normalize_opb(constraint):
    """Normalization of opb constraints

    A normalized opb has only
    - positive coefficients
    - >= or = operator

    >>> x = normalize_opb([(1,3),(-2,2),(1,4),'>',3])
    >>> print(x)
    [(1, 3), (2, -2), (1, 4), '>=', 6]

    >>> x = normalize_opb([(1,3),(2,1),(3,-2),'>=',3])
    >>> print(x)
    [(1, 3), (2, 1), (3, -2), '>=', 3]

    >>> x = normalize_opb([(1,3),(2,1),(-3,-2),'==',3])
    >>> print(x)
    [(1, 3), (2, 1), (3, 2), '==', 6]

    >>> x = normalize_opb([(2,-3), '<',1])
    >>> print(x)
    [(2, 3), '>=', 2]
    """
    value = constraint[-1]
    op    = constraint[-2]
    combinations = constraint[:-2]

    # reduce strict inequalities to loose inequalities
    if op == '<':
        value = value - 1
        op = '<='
    elif op == '>':
        value = value + 1
        op = '>='

    # Invert the sign
    if op == '<=':
        combinations = [(-c,l) for (c,l) in combinations]
        value = -value
        op = '>='

    # Normalize coefficients
    for i in range(len(combinations)):
        c,l = combinations[i]
        if c < 0:
            c = abs(c)
            l = -l
            value = value + c
            combinations[i] = (c,l)
    return combinations+[op,value]



class BaseOPB:
    """Basic propositional formulas in conjunctive normal form.

    A OPB formula is a sequence of pseudo boolean constraints, which
    are positive integer linear combinations of boolean literals,
    either >= or == some integer number.

    Use ``add_constraint`` to add new constraint to the formula, but
    in this case there is no restriction of negative of positive
    coefficients, and the operator can be '>=', '<=', '==', '>', '<'.

    Use ``add_clause`` to add just disjunction of literals.

    Constraints will be added multiple times in case of multiple insertion.

    For documentation purpose it is possible use have an additional
    comment header at the top of the formula, which will be
    *optionally* exported to LaTeX or dimacs.

    Implementation:  for efficiency reason constraints and variables
    can only be added, and not deleted. Furthermore order matters in
    the representation.

    Examples
    --------
    >>> c=BaseOPB()
    >>> c.add_clause([1, 2, -3])
    >>> c.add_clause([-2, 4])
    >>> c.add_clause([-3, 4, -5])
    >>> print(c[1])
    [(1, -2), (1, 4), '>=', 1]
    """

    def __init__(self, constraints=None, description=None):
        """Propositional formulas in conjunctive normal form.

        Parameters
        ----------
        constraints : ordered list of opb constraints
            a clause with k literals list containing k pairs, each
            representing a literal (see `add_clause`). First element
            is the polarity and the second is the variable, which must
            be an hashable object.

            E.g. (not x3) or x4 or (not x2) is encoded as [-3,4,-2]

        description: string, optional
            a description of the formula
        """
        default_description = 'Formula in CNF'
        self.header = OrderedDict()
        if description is not None:
            self.header['description'] = description
        else:
            self.header['description'] = default_description

        self.header['generator'] = "{} ({})".format(info['project'],
                                                    info['version'])
        self.header['copyright'] = info['copyright']
        self.header['url'] = info['url']

        # Initial empty formula
        self._numvar = 0
        self._constraints = []
        for c in constraints or []:
            self.add_constraint(c, check=True)

    def __str__(self):
        """String representation of the formula
        """
        n = self._numvar
        m = len(self._clauses)
        text = "pseudo-boolean formula with {} vars and {} constraints".format(n, m)
        if 'description' in self.header:
            text += " -- " + self.header['description']
        return text

    def __len__(self):
        """Number of constraints in the formula
        """
        return len(self._constraints)

    def __iter__(self):
        """Iterator for clauses in the formula
        """
        return iter(self._constraints)

    def __getitem__(self,idx):
        """Get a clause in the formula
        """
        return self._constraints[idx][:]

    def number_of_variables(self):
        return self._numvar

    def number_of_constraints(self):
        return len(self)


    def all_variable_labels(self,default_label_format='x{}'):
        """Produces the labels of all the variables"""

        for i in range(1, self._numvar+1):
            yield default_label_format.format(i)

    def _check_and_update(self, data):
        if len(data) == 0:
            return
        try:
            maxv = self._numvar
            for c,l in data[:-2]:
                if l==0:
                    raise ValueError("0 is not a valid literal")
                if c<0:
                    raise ValueError("coefficients should be positive")
                maxv = max(abs(l),maxv)
            self._numvar = maxv
            if data[-2] not in ['>=','==']:
                raise ValueError("only >= and == operators allowed")
        except (TypeError, ValueError) as te:
            msg = "constraint is not well formatted"
            raise ValueError(msg) from te


    def update_variable_number(self, new_value):
        """Raises the number of variable in the formula to `new_value`

If the formula has already at least `new_value` variables, this does
not have any effect."""
        non_negative_int(new_value, 'new_value')
        self._numvar = max(self._numvar, new_value)

    def debug(self, allow_opposite=False, allow_repetition=False):
        """Check if the formula representation is correct

        Params
        ------
        allow_repetition: bool, optional
            Allow literal repetition.

            Useful for sanity check. If the flag is `False` and the
            constraints contain two copies of the same literal, then
            `ValueError` is raised. (default: False)

        allow_opposite: bool, optional
            True if and only if the constraints can have opposite literal.

            Useful for sanity check. If the flag is `False` and the
            constraint contain two opposite literals, then
            `ValueError` is raised. (default: False)

        Examples
        --------
        >>> c=BaseOPB()
        >>> c.add_clauses_from([[-1,2],[1,0,-2],[1,3]], check=False)
        >>> c.debug()
        False
        >>> c=BaseOPB()
        >>> c.add_constraint([(1,3),(-2,2),(1,4),'>',3])
        >>> c.debug()
        True
        >>> c.add_constraint([(2,-3), '<',1])
        >>> c.debug()
        True
        >>> c.add_constraint([(1,3),(-2,2),(1,-2),'>',3])
        >>> c.debug()
        False
        >>> c.debug(allow_repetition=True)
        True
        >>> c=BaseOPB()
        >>> c.add_constraint([(1,3),(-2,2),(1,2),'>',3])
        >>> c.debug()
        False
        >>> c.debug(allow_opposite=True)
        True
        """
        # number of variables and clauses
        N = self._numvar

        for constraint in self._constraints:
            for coeff,literal in constraint[:-2]:
                if not 0 < abs(literal) <= N:
                    return False
                if coeff <= 0:
                    return False

        for constraint in self._constraints:
            lits = sorted([l for (c,l) in constraint[:-2] ], key=abs)
            n = len(lits)
            for i in range(n-1):
                if not allow_repetition and lits[i] == lits[i+1]:
                    return False
                if not allow_opposite and lits[i] == -lits[i+1]:
                    return False

        # formula passed all tests
        return True

    def add_clause(self, clause, check=True):
        """Add a clause to the CNF.

        E.g. (not x3) or x4 or (not x2) is encoded as [-1, 4, -2]

        All variable mentioned in the clause will be added to the list
        of variables  of the OPB,  in the  order of appearance  in the
        clauses.

        By default no check is done on the clauses.

        Parameters
        ----------
        clause: list of (bool,str)
            the clause to be added in the CNF

            A clause with k literals is a list with k pairs.
            First coords are the polarities, second coords are utf8
            encoded strings with variable names.

            Clause may contain repeated or opposite literal, but this
            behavior can be modified by the optional flags.

            Clauses are added with repetition, i.e. if the same clause
            is added twice then it will occur twice in the
            formula too.

        check : bool
            check that all literals as integer and update the number of variables, based
            on the literal present in the clause. (default: True)
        """
        data = [(1,l) for l in clause] + ['>=', 1]

        self._constraints.append(data)

        if check:
            self._check_and_update(data)

    def add_clauses_from(self, clauses, check=True):
        """Add a sequence of clauses to the CNF

        Parameters
        ----------
        clause: list of clauses
            the clauses to be added in the CNF

        check : bool
            check that all literals as integer and update the number of variables, based
            on the literal present in the clause. (default: False)
        """
        for c in clauses:
            self.add_clause(c, check=check)

    def add_constraint(self, constraint, check=True):
        """Add a constraint to the formula.

        All variable mentioned in the clause will be added to the list
        of variables of the OPB, in the order of appearance in
        the clauses.

        By default no check is done on the clauses.

        Parameters
        ----------
        constraint: list of (coeff,literal) + op + value
            the constraint to be added

            A constraint is a list containing pairs
            (coefficient,literal) concluded by

            an operator: >=, <=, >, <, ==

            an integer value

            Coefficients must be integers.


        check : bool
            check that all literals as integer and update the
            number of variables, based on the literal present in the
            clause. (default: True)
        """
        constraint = normalize_opb(constraint)
        self._constraints.append(constraint)

        if check:
            self._check_and_update(constraint)

    def add_constraints_from(self, constraints, check=True):
        """Add a sequence of constraints to the formula

        Parameters
        ----------
        constraint: list of constraints
            the constraints to be added

        check : bool
            check that all literals as integer and update the number
            of variables, based on the literal present in the clause.
            (default: False)

        """
        for c in constraints:
            self.add_constraint(c, check=check)

    def variables(self):
        """Return the list of variables"""
        return range(1, self.number_of_variables()+1)

    def constraints(self):
        """Return the list of clauses
        """
        return ConstraintsView(self)

    def at_least(self, lits, value,check=True):
        """Encoding of \"at least\" constraint

        >>> c = BaseOPB()
        >>> c.at_least([1,4,2,-3,6],3)
        >>> print(c[0])
        [(1, 1), (1, 4), (1, 2), (1, -3), (1, 6), '>=', 3]
        """
        lits = [(1,l) for l in lits]
        self.add_constraint(lits + ['>=', value], check=check)

    def at_most(self, lits, value,check=True):
        """Encoding of \"at most\" constraint

        >>> c = BaseOPB()
        >>> c.at_most([1,4,2,-3,6],4)
        >>> print(c[0])
        [(1, -1), (1, -4), (1, -2), (1, 3), (1, -6), '>=', 1]
        """
        lits = [(1,l) for l in lits]
        self.add_constraint(lits + ['<=', value], check=check)

    def cardinality_eq(self, lits, value,check=True):
        """Encoding of \"at most\" constraint

        >>> c = BaseOPB()
        >>> c.cardinality_eq([1,4,2,-3,6],3)
        >>> print(c[0])
        [(1, 1), (1, 4), (1, 2), (1, -3), (1, 6), '==', 3]
        """
        lits = [(1,l) for l in lits]
        self.add_constraint(lits + ['==', value], check=check)

    def add_loose_majority(self, lits, check=True):
        """Encoding of \"at least half\" constraint

        >>> c = BaseOPB()
        >>> c.add_loose_majority([1,4,2,-3,6])
        >>> print(c[0])
        [(1, 1), (1, 4), (1, 2), (1, -3), (1, 6), '>=', 3]
        """
        lits = [(1,l) for l in lits]
        threshold = ((len(lits) + 1) // 2)
        self.add_constraint(lits + ['>=', threshold], check=check)

    def add_loose_minority(self, lits, check=True):
        """Encoding of \"at most half\" constraint

        >>> c = BaseOPB()
        >>> c.add_loose_minority([1,4,2,-3,6,-5])
        >>> print(c[0])
        [(1, -1), (1, -4), (1, -2), (1, 3), (1, -6), (1, 5), '>=', 3]
        """
        lits = [(1,l) for l in lits]
        threshold = len(lits)//2
        self.add_constraint(lits + ['<=', threshold], check=check)

    def add_strict_majority(self, lits, check=True):
        """Encoding of "strict majority" constraint

        >>> c = BaseOPB()
        >>> c.add_strict_majority([1,4,2,-3,6])
        >>> print(c[0])
        [(1, 1), (1, 4), (1, 2), (1, -3), (1, 6), '>=', 3]
        """
        lits = [(1,l) for l in lits]
        threshold = len(lits)//2
        self.add_constraint(lits + ['>', threshold], check=check)

    def add_strict_minority(self, lits, check=True):
        """Encoding \"at most half\" constraint

        >>> c = BaseOPB()
        >>> c.add_strict_minority([1,4,2,-3,6])
        >>> print(c[0])
        [(1, -1), (1, -4), (1, -2), (1, 3), (1, -6), '>=', 3]
        """
        lits = [(1,l) for l in lits]
        threshold = ((len(lits) + 1) // 2)
        self.add_constraint(lits + ['<', threshold], check=check)

    def add_parity(self, lits, constant, check=True):
        """Adds the CNF encoding of a parity constraint

        E.g. X1 + X2 + X3 = 1 (mod 2) is encoded as

        ( X1 v  X2 v  X3)
        (~X1 v ~X2 v  X3)
        (~X1 v  X2 v ~X3)
        ( X1 v ~X2 v ~X3)

        Parameters
        ----------
        variables : array-like
            literals
        constant : {0,1}
            the constant of the linear equation
        check : bool
            check that the literals are valid and update the variable count

        Returns
        -------
        None

        Examples
        --------
        >>> C=BaseOPB()
        >>> C.add_parity([-1,2],1)
        >>> print(list(C))
        [[(1, -1), (1, 2), '>=', 1], [(1, 1), (1, -2), '>=', 1]]
        >>> C=BaseOPB()
        >>> C.add_parity([-1,2],0)
        >>> print(list(C))
        [[(1, -1), (1, -2), '>=', 1], [(1, 1), (1, 2), '>=', 1]]
        """
        if isgenerator(lits):
            lits = list(lits)
        if check:
            # dummy constraint, just to check the literals once
            self._check_and_update([(1,l) for l in lits]+ ['==',0])

        desired_sign = 1 if constant == 1 else -1
        for signs in product([1, -1], repeat=len(lits)):
            # Save only the clauses with the right polarity
            parity = reduce(mul, signs, 1)
            if parity == desired_sign:
                self.add_clause([lit*sign for lit, sign in zip(lits, signs)],
                                check=False)
