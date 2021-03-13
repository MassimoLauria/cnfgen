#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""The implementaton of the basic CNF object
"""

from collections import OrderedDict
from cnfgen.info import info

class BaseCNF:
    """Basic propositional formulas in conjunctive normal form.

    A CNF  formula is a  sequence of  clauses, which are  sequences of
    literals. Each literal is either a variable or its negation.

    Use ``add_clause`` to add new clauses to CNF. Clauses will be added
    multiple times in case of multiple insertion of the same clauses.

    For documentation purpose it is possible use have an additional
    comment header at the top of the formula, which will be
    *optionally* exported to LaTeX or dimacs.

    Implementation:  for efficiency reason clauses and variable can
    only be added, and not deleted. Furthermore order matters in
    the representation.

    Examples
    --------
    >>> c=BaseCNF([[1, 2, -3], [-2, 4]])
    >>> list(c)
    [[1, 2, -3], [-2, 4]]
    >>> c.add_clause([-3, 4, -5])
    >>> list(c)
    [[1, 2, -3], [-2, 4], [-3, 4, -5]]
    >>> print(c[1])
    [-2, 4]
    """

    def __init__(self, clauses=None, description=None):
        """Propositional formulas in conjunctive normal form.

        Parameters
        ----------
        clauses : ordered list of clauses
            a clause with k literals list containing k pairs, each
            representing a literal (see `add_clause`). First element
            is the polarity and the second is the variable, which must
            be an hashable object.

            E.g. (not x3) or x4 or (not x2) is encoded as [(False,"x3"),(True,"x4"),False,"x2")]

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

        # Problem representation via encoders and variable groups.
        self._encoders = []

        # Initial empty formula
        self._numvar = 0
        self._clauses = []
        for c in clauses or []:
            self.add_clause(c)

    def __str__(self):
        """String representation of the formula
        """
        n = self._numvar
        m = len(self._clauses)
        text = "CNF with {} vars and {} clauses".format(n, m)
        if 'description' in self.header:
            text += " -- " + self.header['description']
        return text

    def __len__(self):
        """Number of clauses in the formula
        """
        return len(self._clauses)

    def __iter__(self):
        """Number of clauses in the formula
        """
        return iter(self._clauses)

    def __getitem__(self,idx):
        """Number of clauses in the formula
        """
        return self._clauses[idx][:]

    def number_of_variables(self):
        return self._numvar

    def number_of_clauses(self):
        return len(self)


    def all_variable_labels(self,default_label_format='x{}'):
        """Produces the labels of all the variables"""

        for i in range(1,self._numvar+1):
            yield default_label_format.format(i)

    def update_variable_number(self, new_value):
        """Raises the number of variable in the formula to `new_value`

If the formula has already at least `new_value` variables, this does
not have any effect."""
        self._numvar = max(self._numvar, new_value)

    def debug(self, allow_opposite=False, allow_repetition=False):
        """Check if the formula representation is correct

        Params
        ------
        allow_repetition: bool, optional
            Allow literal repetition.

            Useful for sanity check. If the flag is `False` and the
            clause contain two copies of the same literal, then
            `ValueError` is raised. (default: False)

        allow_opposite: bool, optional
            True if and only if the clause can have opposite literal.

            Useful for sanity check. If the flag is `False` and the
            clause contain two opposite literals, then `ValueError`
            is raised. (default: False)

        Certain manipulation methods are not safe if used incorrectly,
        so the CNF may be corrupted. This method tests if that was not
        the case.

        Examples
        --------
        >>> c=BaseCNF()
        >>> c.add_clauses_from([[-1,2],[1,0,-2],[1,3]])
        >>> c.debug()
        False
        >>> c=BaseCNF()
        >>> c.add_clauses_from([[-1,2],[1,-2],[1,3]])
        >>> c.debug()
        True
        >>> c.add_clause([-1,2,2])
        >>> c.debug(allow_repetition=False)
        False
        >>> c.add_clause([3,2,-3])
        >>> c.debug(allow_opposite=False)
        False
        """
        # number of variables and clauses
        N = self._numvar

        # Count clauses and check literal representation
        for clause in self._clauses:
            for literal in clause:
                if not 0 < abs(literal) <= N:
                    return False

        for clause in self._clauses:
            sclause = sorted(clause, key=abs)
            n = len(sclause)
            for i in range(n-1):
                if not allow_repetition and sclause[i] == sclause[i+1]:
                    return False
                if not allow_opposite and sclause[i] == -sclause[i+1]:
                    return False

        # formula passed all tests
        return True

    def add_clause(self, clause):
        """Add a clause to the CNF.

        E.g. (not x3) or x4 or (not x2) is encoded as [-1, 4, -2]

        All variable mentioned in the clause will be added to the list
        of variables  of the CNF,  in the  order of appearance  in the
        clauses.

        No check is done on the clauses.

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
        """
        data = list(clause)
        if len(data) == 0:
            self._clauses.append([])
            return

        try:
            maxid = max([abs(literal) for literal in data])
        except TypeError:
            raise ValueError("'clause' must be a sequence of non-zero integers")
        self._numvar = max(maxid, self._numvar)
        self._clauses.append(data)

    def add_clauses_from(self, clauses):
        """Add a sequence of clauses to the CNF"""
        for c in clauses:
            self.add_clause(c)

    def variables(self):
        """Return the list of variables"""
        return range(1, self.number_of_variables()+1)

    def clauses(self):
        """Return the list of clauses
        """
        return self.__iter__()
