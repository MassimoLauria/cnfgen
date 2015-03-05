#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""SAT solver integrated with CNFgen.

Of course it does not implement an actual sat solver, but tries to use
solvers installed on the machine. So far it only works with lingeling
and minisat.

Copyright (C) 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import subprocess
import tempfile
import os


def is_lingeling_available(progname='lingeling'):
    """Test is `lingeling` is available"""

    try:
        subprocess.Popen(args=[progname, '--help'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    except OSError:
        return False
    else:
        return True


def is_minisat_available(progname='minisat'):
    """Test is `minisat` is available"""

    try:
        subprocess.Popen(args=[progname, '--help'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    except OSError:
        return False
    else:
        return True


def is_satisfiable_minisat(F, cmd='minisat'):
    """Test CNF satisfiability using a minisat-style solver.

    This also works fine using `glucose` instead of `minisat`, and any
    other solver which is a drop-in replacement of `minisat`.

    Arguments:
    ----------
    `F`: a CNF formula
    `cmd`: the command line used to invoke the SAT solver.

    Example:
    --------
    is_satisfiable_minisat(F,cmd='minisat -no-pre')
    is_satisfiable_minisat(F,cmd='glucose -pre')

    The first call tests F using `minisat` without formula
    preprocessing. The second does it using `glucose` with
    preprocessing.

    Returns:
    --------
    A pair (answer,witness) where answer is either True when F is
    satisfiable, or False otherwise. If F is satisfiable the witness
    is a satisfiable assignment in form of a dictionary, otherwise it
    is None.

    """

    # Minisat does not operate on stdin/stdout so we need temporary
    # files
    cnf = tempfile.NamedTemporaryFile(delete=False)
    sat = tempfile.NamedTemporaryFile(delete=False)
    cnf.write(F.dimacs())
    cnf.close()
    sat.close()

    output = []

    # Run the command, store its output and remove the temporary files.
    try:
        subprocess.Popen(args=cmd.split()+[cnf.name, sat.name],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE).wait()
        sat = open(sat.name, "r")
        output = sat.read().split()
        sat.close()
    except OSError:
        pass
    finally:
        os.unlink(cnf.name)
        os.unlink(sat.name)

    # At this point `output` is either the list ["UNSAT"] or a list of
    # the form ["SAT","v1","v2",...,"vn"] where each "vi" is either
    # "-i" or "i", to indicate that the i-th variables is assigned to
    # false and true, respectively.
    #
    result = None
    witness = None

    if len(output) == 0:

        raise RuntimeError("Error during SAT solver call.\n")

    elif output[0] == 'SAT':

        result = True

        witness = [int(v) for v in output[1:] if v != '0']

        witness = {F._index2name[abs(v)]: v > 0 for v in witness}

    elif output[0] == 'UNSAT':

        result = False

    else:

        raise RuntimeError("Error during SAT solver call.\n")

    return (result, result and witness or None)


def is_satisfiable_lingeling(F, cmd='lingeling'):
    """Test CNF satisfiability using a lingeling-style solver.

    This also works fine using any other solver which is a drop-in
    replacement of `lingeling`.

    Arguments:
    ----------
    `F`: a CNF formula
    `cmd`: the command line used to invoke the SAT solver.

    Example:
    --------
    is_satisfiable_lingeling(F,cmd='minisat -no-pre')
    is_satisfiable_lingeling(F,cmd='glucose -pre')

    The first call tests F using `minisat` without formula
    preprocessing. The second does it using `glucose` with
    preprocessing.


    Returns:
    --------
    A pair (answer,witness) where answer is either True when F is
    satisfiable, or False otherwise. If F is satisfiable the witness
    is a satisfiable assignment in form of a dictionary, otherwise it
    is None.

    """

    # call solver
    p = subprocess.Popen(args=cmd.split(),
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    (output, err) = p.communicate(F.dimacs())

    # parse the solver output, for example
    #
    # s SATISFIABLE
    # v -1 -2 -3 4 5 6 0
    # v -7 8 9 -10 0
    #
    # is parsed as (True,[-1,-2,-3,4,5,6,-7,8,9,-10])

    witness = []
    result = None

    for line in output.splitlines():

        if line[0] == 's':
            if line.split()[1] == 'SATISFIABLE':
                result = True
            elif line.split()[1] == 'UNSATISFIABLE':
                result = False
            else:
                result = None
        if line[0] == 'v':
            witness += [int(el)
                           for el in line.split() if el != "v" and el != "0"]

    if result is None:
        raise RuntimeError("Error during SAT solver call.\n")

    # Now witness is a list [v1,v2,...,vn] where vi is either -i or
    # +i, to represent the assignment. We translate this to our
    # desired output.
    witness = {F._index2name[abs(v)]: v > 0
               for v in witness}

    return (result, result and witness or None)




def is_satisfiable(F, cmd=None):
    """Determines whether a CNF is satisfiable or not.

    The satisfiability is determined using an external sat solver.  If
    no command line is specified, the known solvers are tried in
    succession until one is found.

    Arguments:
    ----------
    `F`: a CNF formula
    `cmd`: command line used for the solver

    Example:
    --------
    is_satisfiable(F,cmd='minisat -no-pre')
    is_satisfiable(F,cmd='glucose -pre')
    is_satisfiable(F,cmd='lingeling --plain')

    Returns:
    --------
    A pair (answer,witness) where answer is either True when F is
    satisfiable, or False otherwise. If F is satisfiable the witness
    is a satisfiable assignment in form of a dictionary, otherwise it
    is None.

    Supported solvers:
    ------------------
    We support `lingeling`, `plingeling`, `minisat` and `glucose` solvers,
    tried in this order.

    Drop-in solver replacements:
    ----------------------------
    It is possible to use any drop-in replacement for these solvers,
    but in this case more information is needed on how to communicate
    with the solver. In particular `lingeling` and `minisat` have very
    different interfaces. `glucose` is a drop-in replacement of
    `minisat`, as `plingeling` is for `lingeling`.

    For the supported solver we pick the right interface, but for
    other solvers it is impossible to guess. We suggest to use one of

    is_satisfiable_minisat(F,cmd='dropin-replacement')
    is_satisfiable_lingeling(F,cmd='dropin-replacement')
    """
    dropin = {
        'lingeling': 'lingeling',
        'plingeling': 'lingeling',
        'minisat': 'minisat',
        'glucose': 'minisat'
    }

    solver_functions = {
        'minisat': (is_minisat_available, is_satisfiable_minisat),
        'lingeling': (is_lingeling_available, is_satisfiable_lingeling)
    }

    cmd='lingeling'
    if (cmd is None) or len(cmd.split())==0:

        solver_names = dropin.keys()  # try all supported solvers

    else:

        solver_names = cmd.split()[0:1]  # use the requested solver
        if solver_names[0] not in dropin:
            raise RuntimeError("Unsupported solver: see the documentation.")

    # tries the choses solvers until one works
    for solver in solver_names:
        assert(dropin[solver] in solver_functions)
        s_test, s_func = solver_functions[dropin[solver]]

        if not s_test(progname=solver):
            continue
        else:
            return s_func(F, cmd)

    # no solver was available.
    raise RuntimeError("No usable solver was found.")
    
