#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Build and manipulate pseudo boolean formulas

The module `contains facilities to generate pseudo boolean formulas,
in order to be printed in OPB or LaTeX formats. Such formulas are
ready to be fed to sat solvers.

The module implements the `OPB` object, which is the main entry point
to the `cnfgen` library.

Copyright (C) 2012-2022  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from cnfgen.formula.opbio import OPBio
from cnfgen.formula.baseopb import BaseOPB
from cnfgen.formula.variables import VariablesManager


class OPB(VariablesManager, OPBio):
    """Pseudo boolean formula

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
    >>> c=OPB()
    >>> c.add_clause([1, 2, -3])
    >>> c.add_clause([-2, 4])
    >>> c.add_clause([-3, 4, -5])
    >>> print(c[1])
    [(1, -2), (1, 4), '>=', 1]
    >>> c.add_constraint([(1,2),(4,-3), '>=', 2])
    >>> print(c[-1])
    [(1, 2), (4, -3), '>=', 2]

    >>> c = OPB()
    >>> f = c.new_mapping(5,4)
    >>> c.force_complete_mapping(f)
    >>> c.force_injective_mapping(f)
    >>> print( c.to_opb(), end='')
    * #variable= 20 #constraint= 9
    +1 x1 +1 x2 +1 x3 +1 x4 >= 1
    +1 x5 +1 x6 +1 x7 +1 x8 >= 1
    +1 x9 +1 x10 +1 x11 +1 x12 >= 1
    +1 x13 +1 x14 +1 x15 +1 x16 >= 1
    +1 x17 +1 x18 +1 x19 +1 x20 >= 1
    +1 ~x1 +1 ~x5 +1 ~x9 +1 ~x13 +1 ~x17 >= 4
    +1 ~x2 +1 ~x6 +1 ~x10 +1 ~x14 +1 ~x18 >= 4
    +1 ~x3 +1 ~x7 +1 ~x11 +1 ~x15 +1 ~x19 >= 4
    +1 ~x4 +1 ~x8 +1 ~x12 +1 ~x16 +1 ~x20 >= 4
    """

    def __init__(self, constraints=None, description=None):
        OPBio.__init__(self,
                           constraints=constraints,
                           description=description)
        VariablesManager.__init__(self,self)
