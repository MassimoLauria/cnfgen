#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""SAT solver integrated with CNFgen.

Of course it does not implement an actual sat solver, but tries to use
solvers installed on the machine. So far it only works with lingeling.

Copyright (C) 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""

import subprocess

def parse_dimacs_solver_output(text):
    """Parse the output of a SAT solver

    Parses the output of a SAT solver, written in DIMACS and produces
    the (answer,assignment) pair. The boolan value `answer` is true
    iff the solver outputs SATISFIABLE. If the formula is satisfiable
    `assignment` is a list of integer which represent the dimacs
    encoding of the assignment, otherwise its value should be ignored.

    Example:
    --------
    s SATISFIABLE
    v -1 -2 -3 4 5 6 0
    v -7 8 9 -10 0

    is parsed as (True,[-1,-2,-3,4,5,6,-7,8,9,-10])
    """
    assignment = []
    result = None

    for line in text.splitlines():

        if line[0] == 's':
            if line.split()[1] == 'SATISFIABLE':
                result = True
            elif line.split()[1] == 'UNSATISFIABLE':
                result = False
            else:
                result = None
        if line[0] == 'v':
            assignment += [int(el)
                           for el in line.split() if el != "v" and el != "0"]

    return result, assignment


def is_satisfiable(F):
    """Determines whether a CNF is satisfiable or not.

    The satisfiability is determined using an external sat solver.  If
    no command line is specified, the known solvers are tried in
    succession until one is found.

    Arguments:
    ----------
    `F`: a CNF formula
    `solvercommand`: the command line used to invoke the SAT solver.

    Returns:
    --------
    A pair (answer,witness) where answer is either True (if
    satisfiable) or False (if unsatisfiable). If satisfiable the
    witness is a satisfiable assignment in form of a
    dictionary. Otherwise it is none.

    """

    # call solver
    p = subprocess.Popen('lingeling',
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    (output, err) = p.communicate(F.dimacs())

    result, dimacs_assignment = parse_dimacs_solver_output(output)

    if result is None:
        raise subprocess.CalledProcessError("Error during SAT solver call.\n")

    # The DIMACS assignment is a vector containing -v or -v for v the
    # integer dimacs indices of variables.
    witness = {F._index2name[v]: v > 0
               for v in dimacs_assignment}

    return (result, result and witness or None)
