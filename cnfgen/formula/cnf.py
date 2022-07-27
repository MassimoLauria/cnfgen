#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Build and manipulate CNF formulas

The module `contains facilities to generate cnf formulas, in order to
be printed in DIMACS, OPB or LaTeX formats. Such formulas are ready to
be fed to sat solvers.

The module implements the `CNF` object, which is the main entry point
to the `cnfgen` library.

Copyright (C) 2012-2022  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from cnfgen.formula.cnfio import CNFio
from cnfgen.formula.linear import CNFLinear
from cnfgen.formula.variables import VariablesManager


class CNF(VariablesManager, CNFio, CNFLinear):
    """Propositional formulas in conjunctive normal form.

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
    >>> c=CNF([[1, 2, -3], [-2, 4]])
    >>> print( c.to_dimacs(),end='')
    p cnf 4 2
    1 2 -3 0
    -2 4 0
    >>> c.add_clause([-3, 4, -5])
    >>> print( c.to_dimacs(),end='')
    p cnf 5 3
    1 2 -3 0
    -2 4 0
    -3 4 -5 0
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
        CNFLinear.__init__(self,
                           clauses=clauses,
                           description=description)
        VariablesManager.__init__(self,self)
