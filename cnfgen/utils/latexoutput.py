#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""Output a LaTeX version of the CNF formula

The CNF formula is translated into the LaTeX markup language
[1]_, using the names of the variable literally. The formula
is rendered in the ``align`` environment, with one clause per
row. Negated literals are rendered using the
``\\neg`` command.

The output string is ready to be included in a document, but
it does not include neither a preamble nor is nested inside
``\\begin{document}`` ... ``\\end{document}``.

.. note::  By default the LaTeX document in output is *UTF-8* encoded.

Examples
--------
>>> from cnfgen.formula.cnf import CNF
>>> F=CNF([[-1, 2, -3], [-2, -4], [2, 3, -4]])
>>> print(to_latex_string(F))
\\begin{align}
&       \\left( {\\overline{x}_1} \\lor            {x_2} \\lor {\\overline{x}_3} \\right) \\\\
& \\land \\left( {\\overline{x}_2} \\lor {\\overline{x}_4} \\right) \\\\
& \\land \\left(            {x_2} \\lor            {x_3} \\lor {\\overline{x}_4} \\right)
\\end{align}
>>> F=CNF()
>>> print(to_latex_string(F))
\\begin{align}
   \\top
\\end{align}


References
----------
.. [1] http://www.latex-project.org/

"""

import sys
from io import StringIO

def to_latex_string(F):
    """LaTeX string of the CNF formula

    Parameters
    ----------
    F : cnfgen.formula.cnf.CNF
        cnf formula

    Returns
    -------
    string
        the string contains the LaTeX code
    """
    outputfile = StringIO()
    _print_latex(F, outputfile)
    return outputfile.getvalue()

def _print_latex(F, outputfile, split_every=-1, compact=True):
    """Print the LaTeX code corresponding to formula F, to `outputfile`

    Put a pagebreak every 'split_every' clauses.
    """

    # Literal translation
    littext = {}
    for varid, name in enumerate(
            F.all_variable_labels(default_label_format='x_{}'),
            start=1):
        littext[varid] = "           {" + name + "}"
        split_points = [name.find("_"), name.find("^")]
        split_points = [x for x in split_points if x > 0]
        if len(split_points)==0:
            littext[-varid] = "  \\overline{" + name + "}"
        else:
            split_point = min(split_points)
            littext[-varid] = "{\\overline{" + \
                name[:split_point] + "}" + name[split_point:] + "}"

    def write_clause(cls, first, compact):
        """Write the clause in LaTeX."""
        outputfile.write("\n&" if first else " \\\\\n&")
        outputfile.write("       " if not compact or first else " \\land ")

        # build the latex clause
        if len(cls) == 0:
            outputfile.write("\\square")
        elif compact:
            outputfile.write("\\left( " +
                             " \\lor ".join(littext[lit] for lit in cls) +
                             " \\right)")
        else:
            outputfile.write(" \\lor ".join(littext[lit] for lit in cls))

    outputfile.write("\\begin{align}")

    if len(F) == 0:
        outputfile.write("\n   \\top")
    else:
        for i in range(len(F)):
            if split_every > 0 and i % split_every == 0 and i != 0:
                outputfile.write("\n\\end{align}\\pagebreak")
                outputfile.write("\n\\begin{align}")
                write_clause(F[i], True, compact)
            else:
                write_clause(F[i], i == 0, compact)

    outputfile.write("\n\\end{align}")

def to_latex_document(F, fileorname, export_header=True, extra_text=""):
    """Output a LaTeX document describing the CNF formula

    Parameters
    ----------
    F : cnfgen.formula.cnf.CNF
        cnf formula

    fileorname: file object or string (or stdout if None)
        destination file given either as object or as filename

    export_header : bool, optional
        determines whether the formula header should be inserted as
        a LaTeX comment in the output. By default is True.

    extra_text : str, optional
        Additional text attached to the abstract."""

    # fileorname is an actual file name
    if fileorname is None:
        output = sys.stdout
    elif isinstance(fileorname, str):
        with open(fileorname, 'w', encoding='utf-8') as filehandle:
            to_latex_document(F, filehandle,
                              export_header=export_header,
                              extra_text=extra_text)
            return
    else:
        output = fileorname

    clauses_per_page = 35

    latex_preamble = r"""%
\documentclass[10pt,a4paper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{listings}
\usepackage[utf8]{inputenc}
"""

    # document opening
    output.write(latex_preamble)
    output.write("\\begin{document}\n")
    title = F.header['description']
    title = title.replace("_", "\\_")
    output.write("\\title{{{}}}\n".format(title))
    output.write("\\author{CNFgen formula generator}\n")
    output.write("\\maketitle\n")
    if export_header:
        output.write("\\noindent\\textbf{Formula header:}\n")
        output.write("\\begin{lstlisting}[breaklines]\n")
        for field in F.header:
            tmp = "{}: {}\n".format(field, F.header[field])
            tmp = tmp.encode('ascii', errors='replace').decode('ascii')
            output.write(tmp)
        output.write("\\end{lstlisting}\n")
        output.write("\\bigskip\n")

    # Extra text
    output.write(extra_text)

    # Output the clauses
    output.write("\\noindent\\textbf{{CNF with {} variables and and {} clauses:}}\n".
                 format(F.number_of_variables(), F.number_of_clauses()))

    _print_latex(F,output,split_every=clauses_per_page,compact=False)

    # document closing
    output.write("\n\\end{document}")
