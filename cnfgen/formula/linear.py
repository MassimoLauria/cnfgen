#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF formulas type with support of linear forms

This CNF formula type supports
- linear equations mod 2
- integer  linear inequalities on literals (no coefficients)
  for example 'atmost k'


Copyright (C) 2021 Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git
"""

from functools import reduce
from operator import mul
from itertools import combinations
from itertools import product

from cnfgen.formula.basecnf import BaseCNF


class CNFLinear(BaseCNF):
    """CNF with linear constraints"""
    def __init__(self, clauses=None, description=None):
        BaseCNF.__init__(self, clauses=clauses, description=description)

    ###
    # Various utility function for CNFs
    ###
    def add_parity(self, lits, constant):
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

        Returns
        -------
        None

        Examples
        --------
        >>> C=CNFLinear()
        >>> C.add_parity([-1,2],1)
        >>> list(C)
        [[-1, 2], [1, -2]]
        >>> C=CNFLinear()
        >>> C.add_parity([-1,2],0)
        >>> list(C)
        [[-1, -2], [1, 2]]
        """
        desired_sign = 1 if constant == 1 else -1
        for signs in product([1, -1], repeat=len(lits)):
            # Save only the clauses with the right polarity
            parity = reduce(mul, signs, 1)
            if parity == desired_sign:
                self.add_clause([lit*sign for lit, sign in zip(lits, signs)])

    def add_linear(self, lits, op, constant):
        """Add a linear constraint to the formula

        Encodes an equality or an inequality constraint on literals (no
        coeffcients) as clauses.

        Parameters
        ----------
        lits : array-like
            literals
        op: str
            one among '<=', ">=", '<', '>', '==', '!='
        constant : integer
            the constant of the linear equation

        Returns
        -------
        None

        Examples
        --------
        >>> c = CNFLinear()
        >>> c.add_linear([-1,2,-3],'>=',1)
        >>> list(c)
        [[-1, 2, -3]]
        >>> c = CNFLinear()
        >>> c.add_linear([-1,2,-3],'>=',3)
        >>> list(c)
        [[-1], [2], [-3]]
        >>> c = CNFLinear()
        >>> c.add_linear([-1,2,-3],'<',2)
        >>> list(c)
        [[1, -2], [1, 3], [-2, 3]]
        >>> c = CNFLinear()
        >>> c.add_linear([1,2,3],'<=',-1)
        >>> list(c)
        [[]]
        >>> c = CNFLinear()
        >>> c.add_linear([1,2,3],'<=',10)
        >>> list(c)
        []
        """
        operators = ['<=', ">=", '<', '>', '==', '!=']
        if op not in operators:
            raise ValueError('Invalid operator, only {} allowed'.
                             format(", ".join(operators)))

        # We reduce to the case of >=
        if op == "==":
            self.add_linear(lits, '<=', constant)
            self.add_linear(lits, '>=', constant)
            return
        elif op == "!=":
            self.add_linear(lits, '<=', constant-1)
            self.add_linear(lits, '>=', constant+1)
            return
        elif op == "<":
            self.add_linear(lits, '<=', constant-1)
            return
        elif op == ">":
            self.add_linear(lits, '>=', constant+1)
            return
        elif op == "<=":
            negated = [-lit for lit in lits]
            self.add_linear(negated, '>=', len(negated) - constant)
            return

        # Tautologies and invalid inequalities
        if constant <= 0:
            return

        try:
            w = len(lits)
        except TypeError:
            w = len(list(lits))

        if constant > w:
            self.add_clause([])
            return

        k = w - constant + 1
        for clause in combinations(lits, k):
            self.add_clause(clause)

    def add_loose_majority(self, lits):
        """Clauses encoding a \"at least half\" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = ((len(lits) + 1) // 2)
        return self.add_linear(lits, '>=', threshold)

    def add_loose_minority(self, lits):
        """Clauses encoding a \"at most half\" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = len(lits) // 2
        return self.add_linear(lits, '<=', threshold)

    def add_strict_majority(self, lits):
        """Clauses encoding a "strict majority" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = len(lits)//2 + 1
        return self.add_linear(lits, '>=', threshold)

    def add_strict_minority(self, lits):
        """Clauses encoding a \"at most half\" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = (len(lits) - 1) // 2
        return self.add_linear(lits, '<=', threshold)
