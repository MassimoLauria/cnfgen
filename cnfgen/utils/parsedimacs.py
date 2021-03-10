#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Read and write DIMACS format

DIMACS format is the industry standard for the encoding of CNF
formulas. It is the most popular input format for SAT solvers [1]_.

References
----------
.. [1] http://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/satformat.ps

"""

import sys
from io import StringIO


def to_dimacs_file(formula, fileorname=None, export_header=True, export_varnames=False):
    """Save the DIMACS encoding of a formula to a file

    Parameters
    ----------
    formula:
        a cnf formula
    fileorname: file object or string (or stdout if None)
        destination file given either as object or as filename
    export_header : bool
        determines whether the formula header should be inserted as
        a comment in the DIMACS output.
    export_varnames : bool, optional
        determines whether a map from variable indices to variable
        names should be appended to the header.
    """
    # fileorname is an actual file name
    if fileorname is None:
        output = sys.stdout
    elif isinstance(fileorname, str):
        with open(fileorname, 'w', encoding='utf-8') as filehandle:
            to_dimacs_file(formula, filehandle,
                           export_header=export_header,
                           export_varnames=export_varnames)
            return
    else:
        output = fileorname

    # Count the number of variables and clauses
    n = formula.number_of_variables()
    m = formula.number_of_clauses()

    # Produce header in ascii compatible format
    if export_header:
        # remove non ascii text
        for field in formula.header:
            tmp = "c {}: {}\n".format(field, formula.header[field])
            tmp = tmp.encode('ascii', errors='replace').decode('ascii')
            output.write(tmp)
        output.write("c\n")

    if export_varnames:
        for varid, label in enumerate(formula.all_variable_labels(), start=1):
            output.write("c varname {0} {1}\n".format(varid, label))
        output.write("c\n")

    # Formula specification
    output.write("p cnf {0} {1}\n".format(n, m))
    # Clauses
    for cls in formula:
        print(*cls, 0, file=output)


def parse_dimacs(infile):
    """
    Parse a dimacs cnf file into a list of
    compressed clauses.

    return: (n,c) where

    n is the number of variables
    c is the list of compressed clauses.
    """
    n = None  # negative signal that spec line has not been read
    m = None
    clauses_count = 0

    line_counter = 0
    literal_buffer = []

    for line in infile.readlines():

        line_counter += 1
        line = line.strip()

        # Empty line
        if len(line) == 0 or line[0] == 'c':
            continue

        # parse spec line
        if line[0] == 'p':
            if n is not None:
                raise ValueError(
                    "There is a another spec at line {}".format(line_counter))
            try:
                _, _, nstr, mstr = line.split()
                n = int(nstr)
                m = int(mstr)
            except ValueError:
                raise ValueError("Spec at line {} should have "
                                 "format 'p cnf <n> <m>'".format(line_counter))
            yield n
            continue

        if n is None:
            raise ValueError(
                "Non comment line {} before p cnf <n> <m>".format(line_counter))

        # parse literals
        try:
            for lv in [int(lit) for lit in line.split()]:
                if lv == 0:
                    clauses_count += 1
                    yield tuple(literal_buffer)
                    literal_buffer = []
                elif 1 <= abs(lv) <= n:
                    literal_buffer.append(lv)
                else:
                    raise ValueError
        except ValueError:
            raise ValueError("Invalid literal at line {}".format(line_counter))

    # Checks at the end of parsing
    if len(literal_buffer) > 0:
        raise ValueError("Last clause was incomplete")

    if n is None:
        raise ValueError("Missing spec line 'p cnf <n> <m>")

    if m != clauses_count:
        raise ValueError("Formula contains {} clauses "
                         "but {} were expected.".format(clauses_count, m))


def from_dimacs_file(cnfclass, fileorname=None):
    """Read DIMACS into a CNF object

    Parameters
    ----------
    cnfclass: subclass of cnfgen.basecnf.BaseCNF
        the type of CNF object to produce
    fileorname: file object or string (or stdin if None)
        destination file given either as object or as filename"""
    if fileorname is None:
        inputfile = sys.stdin
        name = '<stdin>'
    elif isinstance(fileorname, str):
        with open(fileorname, 'r', encoding='utf-8') as filehandle:
            from_dimacs_file(cnfclass, filehandle)
            return
    else:
        inputfile = fileorname
        try:
            name = fileorname.name
        except AttributeError:
            name = '<unknown>'

    description = 'Formula from DIMACS file {}'.format(name)
    F = cnfclass(description=description)
    dimacs = parse_dimacs(inputfile)
    n = next(dimacs)
    F.update_variable_number(n)
    for c in dimacs:
        F.add_clause(c)
    return F
