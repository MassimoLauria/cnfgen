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
from cnfgen.formula.basecnf import BaseCNF
from cnfgen.formula.baseopb import BaseOPB


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
    m = len(formula)

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
            output.write("* varname x{0} {1}\n".format(varid, label))
        output.write("*\n")

    # Objective
    if isinstance(formula,BaseOPB):
        if formula.objective():
            output.write("min: ")
            for (c,l) in formula.objective():
                output.write("{:+} x{} ".format(c,l) )
            output.write(" ;\n")

    # Clauses
    if isinstance(formula,BaseCNF):
        for cls in formula:
            for lit in cls:
                if lit>=0:
                    output.write("+1 x{} ".format(lit) )
                else:
                    output.write("+1 ~x{} ".format(-lit))
            output.write(">= 1 ;\n")
    elif isinstance(formula,BaseOPB):
        for lin in formula:
            op = ">=" if lin[-2]==">=" else "="
            value = lin[-1]
            for (c,l) in lin[:-2]:
                if l>=0:
                    output.write("{:+} x{} ".format(c,l) )
                else:
                    output.write("{:+} ~x{} ".format(c,-l) )
            output.write("{} {} ;\n".format(op,value))
