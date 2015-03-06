#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""SAT solver integrated with CNFgen.

Of course it does not implement an actual sat solver, but tries to use
solvers installed on the machine. For the full list of supported
solvers, see::

  cnfformula.utils.solver.supported()

Copyright (C) 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import subprocess
import tempfile
import os

__all__ = ["supported", "is_satisfiable", "is_available"]

_SATSOLVER_IOSTYLE = {
    'lingeling': 'dimacs',
    'plingeling': 'dimacs',
    'precosat': 'dimacs',
    'picosat': 'dimacs',
    'march': 'nostdin',
    'cryptominisat': 'dimacs',
    'minisat': 'minisat',
    'glucose': 'minisat',
    'sat4j': 'nostdin',
}


def supported():
    """List the supported SAT solvers"""
    return _SATSOLVER_IOSTYLE.keys()


def is_available(solvers=None):
    """Test whether we can run SAT solvers.

    Paramenters
    -----------
    `solvername` : string / list of strings, optional
        the names of the solvers to be tested.

    If `solvers` is None then all supported solvers are tested.
    If `solvers` is a list of strings all solvers in the list are tested.
    If `solvers` is a string then only that solver is tested.
    """

    if solvers is None:
        solvers = supported()
    elif type(solvers) == str:
        solvers = [solvers]

    for solvername in solvers:
        try:
            subprocess.Popen(args=[solvername, '--help'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        except OSError:
            pass
        else:
            return True
    return False


def is_satisfiable_iostyle_minisat(F, cmd='minisat'):
    """Test CNF satisfiability using a minisat-style solver.

    This also works fine using `glucose` instead of `minisat`, or any
    other solver which uses the same I/O conventions of `minisat`.

    Arguments:
    ----------
    `F`: a CNF formula
    `cmd`: the command line used to invoke the SAT solver.

    Examples:
    ---------
    is_satisfiable_iostyle_minisat(F,cmd='minisat -no-pre')
    is_satisfiable_iostyle_minisat(F,cmd='glucose -pre')

    The first call tests F using `minisat` without formula
    preprocessing. The second does it using `glucose` with
    preprocessing.

    Returns:
    --------
    A pair (answer,witness) where answer is either True when F is
    satisfiable, or False otherwise. If F is satisfiable the witness
    is a satisfiable assignment in form of a dictionary, otherwise it
    is None.


    Notes:
    ------
    `minisat` writes its output on a file. If the formula is
    unsatisfiable then the output file contains just the line "UNSAT",
    but if it is satisfiable it contains the line "SAT" and on a new
    line the assignment, encoded as literal values, e.g., "-1 2 3 -4 -5 ..."
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


def is_satisfiable_iostyle_dimacs(F, cmd='lingeling'):
    """Test CNF satisfiability using a dimacs I/O compatible solver.

    This works fine using any other solver which respects the dimacs
    conventions for input/output. In particular it works with the
    default solver which is `lingeling`.

    Arguments:
    ----------
    `F`: a CNF formula
    `cmd`: the command line used to invoke the SAT solver.

    Example:
    --------
    is_satisfiable_iostyle_dimacs(F,cmd='lingeling --plain')
    is_satisfiable_iostyle_dimacs(F,cmd='cryptominisat')

    The first call tests F using `lingeling` without formula
    preprocessing. The second does it using `march` with default settings.


    Returns:
    --------
    A pair (answer,witness) where answer is either True when F is
    satisfiable, or False otherwise. If F is satisfiable the witness
    is a satisfiable assignment in form of a dictionary, otherwise it
    is None.

    Notes:
    ------
    A solver adheres to dimacs I/O conventions if every line on the
    standard output is preceded by the 'c' character, except for the
    solution line, preceded by 's', and possibly for the assignment
    lines, each one preceded by 'v'. See example::

      c comment line
      c more comments
      s SATISFIABLE
      c other comments
      v -1 -2 -3 4 5 6
      v -7 8 9 -10 0
      c concluding comments.
    """

    # call solver
    output = ""
    try:
        p = subprocess.Popen(args=cmd.split(),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        (output, err) = p.communicate(F.dimacs())
    except OSError:
        pass

    # parse the solver output, for example
    #
    # s SATISFIABLE
    # v -1 -2 -3 4 5 6
    # v -7 8 9 -10 0
    #
    # is parsed as (True,[-1,-2,-3,4,5,6,-7,8,9,-10])

    witness = []
    result = None

    for line in output.splitlines():

        if len(line) == 0:
            continue

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


def is_satisfiable_iostyle_nostdin(F, cmd='sat4j'):
    """Test CNF satisfiability using solvers that requires input file.

    This works fine using any solver which requires the input formula
    as a file but respects the dimacs conventions for the output. In
    particular it works with the default solver which is `sat4j`.

    Arguments:
    ----------
    `F`: a CNF formula
    `cmd`: the command line used to invoke the SAT solver.

    Example:
    --------
    is_satisfiable_iostyle_dimacs(F,cmd='sat4j')
    is_satisfiable_iostyle_dimacs(F,cmd='march')
 
    Returns:
    --------
    A pair (answer,witness) where answer is either True when F is
    satisfiable, or False otherwise. If F is satisfiable the witness
    is a satisfiable assignment in form of a dictionary, otherwise it
    is None.

    """

    # Input formula must be on file.
    cnf = tempfile.NamedTemporaryFile(delete=False)
    cnf.write(F.dimacs())
    cnf.close()

    output = ""

    try:
        p = subprocess.Popen(args=cmd.split()+[cnf.name],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        (output, err) = p.communicate()
    except OSError:
        pass

    # parse the solver output, for example
    #
    # s SATISFIABLE
    # v -1 -2 -3 4 5 6
    # v -7 8 9 -10 0
    #
    # is parsed as (True,[-1,-2,-3,4,5,6,-7,8,9,-10])

    witness = []
    result = None

    for line in output.splitlines():

        if len(line) == 0:
            continue

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
    is_satisfiable(F,cmd='sat4j')

    Returns:
    --------
    A pair (answer,witness) where answer is either True when F is
    satisfiable, or False otherwise. If F is satisfiable the witness
    is a satisfiable assignment in form of a dictionary, otherwise it
    is None.

    Supported solvers:
    ------------------
    see `cnfformula.utils.solver.supported()`

    Drop-in solver replacements:
    ----------------------------

    It is possible to use any drop-in replacement for these solvers,
    but in this case more information is needed on how to communicate
    with the solver. In particular `minisat` does not respect
    the standard `dimacs` I/O conventions, and that holds also for
    `glucose` which is a drop-in replacement of `minisat`.

    For the supported solver we can pick the right interface, but for
    other solvers it is impossible to guess. We suggest to use one of

    is_satisfiable_iostyle_minisat(F,cmd='minisat-style-solver')
    is_satisfiable_iostyle_dimacs(F,cmd='dimacs-style-solver')
    is_satisfiable_iostyle_nostdin(F,cmd='sat4j')
    """

    dropin = _SATSOLVER_IOSTYLE

    solver_functions = {
        'minisat': is_satisfiable_iostyle_minisat,
        'nostdin': is_satisfiable_iostyle_nostdin,
        'dimacs': is_satisfiable_iostyle_dimacs,
    }

    if (cmd is None) or len(cmd.split()) == 0:

        solver_cmds = dropin.keys()  # try all supported solvers

    else:

        # supported solver?
        if cmd.split()[0] not in dropin:
            raise RuntimeError(
                "Solver '{}' is not supported (see documentation)"
                .format(cmd.split()[0]))
        solver_cmds = [cmd]

    # tries the chosen solvers until one works
    for solver_cmd in solver_cmds:
        solver = solver_cmd.split()[0]
        assert dropin[solver] in solver_functions
        s_func = solver_functions[dropin[solver]]

        if not is_available(solvers=[solver]):
            continue
        else:
            return s_func(F, solver_cmd)

    # no solver was available.
    if len(solver_cmds) == 1:
        raise RuntimeError("Solver '{}' is not installed or is unusable."
                           .format(solver_cmds[0].split()[0]))
    else:
        raise RuntimeError("No usable solver found.")
