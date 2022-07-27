#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Write OPB format

OPB format is the industry standard for the encoding of pseudo boolean
constraints.[1]_.

References
----------
.. [1] https://www.cril.univ-artois.fr/PB12/format.pdf

"""

import sys

def to_opb_file(formula, fileorname=None,
                export_header=True,
                export_varnames=False):
    """Save the OPB encoding of a CNF formula to a file

    Parameters
    ----------
    formula:
        a cnf formula
    fileorname: file object or string (or stdout if None)
        destination file given either as object or as filename
    export_header : bool
        determines whether the formula header should be inserted as
        a comment in the OPB output.
    export_varnames : bool, optional
        determines whether a map from variable indices to variable
        names should be appended to the header.
    """
    # fileorname is an actual file name
    if fileorname is None:
        output = sys.stdout
    elif isinstance(fileorname, str):
        with open(fileorname, 'w', encoding='utf-8') as filehandle:
            to_opb_file(formula, filehandle,
                        export_header=export_header,
                        export_varnames=export_varnames)
            return
    else:
        output = fileorname

    # Count the number of variables and clauses
    n = formula.number_of_variables()
    m = formula.number_of_clauses()

    # Formula specs on top
    output.write("* #variable= {n} #constraint= {m}\n".format(n=n,m=m))

    # Produce header in ascii compatible format
    if export_header:
        # remove non ascii text
        for field in formula.header:
            tmp = "* {}: {}\n".format(field, formula.header[field])
            tmp = tmp.encode('ascii', errors='replace').decode('ascii')
            output.write(tmp)
        output.write("*\n")

    if export_varnames:
        for varid, label in enumerate(formula.all_variable_labels(), start=1):
            output.write("* varname {0} {1}\n".format(varid, label))
        output.write("*\n")

    # Clauses
    for cls in formula:
        for lit in cls:
            if lit>=0:
                output.write("1  x{} ".format(lit) )
            else:
                output.write("1 ~x{} ".format(-lit))
        output.write(">= 1\n")
