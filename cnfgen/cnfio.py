#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF formula with read/write capabilities"""

import os
from io import StringIO

from cnfgen.basecnf import BaseCNF

from cnfgen.utils.parsedimacs import to_dimacs_file
from cnfgen.utils.latexoutput import to_latex_string, to_latex_document
from cnfgen.utils.solver import is_satisfiable


class CNFio(BaseCNF):
    """CNF class with I/O capabilities

    - read and write DIMACS
    - write to LaTeX format
    - communicate with SAT solver

    Examples
    --------
    >>> c=CNFio([[1, 2, -3], [-2, 4]])
    >>> print( c.to_dimacs(),end='')
    p cnf 4 2
    1 2 -3 0
    -2 4 0
    """
    def __init__(self, clauses=None, description=None):
        BaseCNF.__init__(self, clauses=clauses, description=description)

    def to_dimacs(self):
        """Produce the dimacs encoding of the formula

        The formula is rendered in the DIMACS format for CNF formulas,
        which is a particularly popular input format for SAT solvers [1]_.

        .. note:: By default the DIMACS output is *ascii* encoded,
                  with non-ascii characters replaced.

        Returns
        -------
        string
            the string contains the Dimacs code

        Examples
        --------
        >>> c=CNFio([[-1, 2, -3], [-2,-4], [2, 3, -4]])
        >>> print(c.to_dimacs(),end='')
        p cnf 4 3
        -1 2 -3 0
        -2 -4 0
        2 3 -4 0

        >>> c=CNFio()
        >>> print(c.to_dimacs(),end='')
        p cnf 0 0

        References
        ----------
        .. [1] http://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/satformat.ps
        """
        output = StringIO()
        to_dimacs_file(self, output, export_header=False, export_varnames=False)
        return output.getvalue()

    def to_latex(self):
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

        Returns
        -------
        string
            the string contains the LaTeX code

        Examples
        --------
        >>> c=CNFio([[-1, 2, -3], [-2, -4], [2, 3, -4]])
        >>> print(c.to_latex())
        \\begin{align}
        &       \\left( {\\overline{x}_1} \\lor            {x_2} \\lor {\\overline{x}_3} \\right) \\\\
        & \\land \\left( {\\overline{x}_2} \\lor {\\overline{x}_4} \\right) \\\\
        & \\land \\left(            {x_2} \\lor            {x_3} \\lor {\\overline{x}_4} \\right)
        \\end{align}
        >>> c=CNFio()
        >>> print(c.to_latex())
        \\begin{align}
           \\top
        \\end{align}

        References
        ----------
        .. [1] http://www.latex-project.org/
        """
        return to_latex_string(self)


    def to_file(self,
                fileorname=None,
                fileformat=None,
                export_header=True,
                export_varnames=False,
                extra_text=""):
        """Save the formula to a file

        The formula is saved on file, in either as a DIMACS file, or
        as a LaTeX document.

        If `fileformat` is either `dimacs` or `tex` then the output is
        saved in the corresponding format.

        If `fileformat` is `None`, then DIMACS format is the default
        output format unless the file name ends with '.tex'.

        Parameters
        ----------
        fileorname: file name or file object
            where to print the file (default: <stdout>)

        fileformat: 'tex', 'dimacs' or None
            format of the output file

        export_header: bool
            print some additional information on the output file (default: True)

        export_varnames: bool
            add the variable ID --> name information in the dimacs (default: True)

        extra_text: str
            additional text to be included in the LaTeX output document
        """
        if fileformat is None:
            # try to discover the appropriate fileformat
            try:
                if isinstance(fileorname, str):
                    name = fileorname
                else:
                    name = fileorname.name
                ext = os.path.splitext(name)[-1][1:]
                fileformat = ext
            except (AttributeError, ValueError, IndexError):
                fileformat = 'dimacs'

        if fileformat == 'tex':
            to_latex_document(self,
                              fileorname,
                              export_header=export_header,
                              extra_text=extra_text)
        else:
            to_dimacs_file(self,
                           fileformat,
                           export_header=export_header,
                           export_varnames=export_varnames)


    def is_satisfiable(self, cmd=None, sameas=None, verbose=0):
        """Determines whether a CNF is satisfiable or not.

        The formula is passed to a SAT solver, according to the
        optional command line ``cmd``. If no command line is
        specified, the known solvers are tried in succession until one
        is found.

        It is possible to use any drop-in replacement for these
        solvers, but in this case more information is needed on how to
        communicate with the solver. In particular ``minisat`` does not
        respect the standard DIMACS I/O conventions, and that holds
        also for ``glucose`` which is a drop-in replacement of
        ``minisat``.

        For the supported solver we can pick the right interface, but
        for other solvers it is impossible to guess. Nevertheless it
        is possible to indicate which interface to use, or more
        specifically which known solver interface to mimic.

        >>> F.is_satisfiable(cmd='minisat-style-solver',sameas='minisat')  # doctest: +SKIP
        >>> F.is_satisfiable(cmd='dimacs-style-solver',sameas='lingeling') # doctest: +SKIP

        Parameters
        ----------
        cmd : string,optional
            the actual command line used to invoke the SAT solver

        sameas : string, optional
            use the interface of one of the supported solvers. Useful
            when the solver used in the command line is not supported.

        verbose: int
            0 or less means no output. 1 shows the command line actually
            run. 2 outputs the solver output. (default: 0)


        Examples
        --------
        >>> F.is_satisfiable()                                              # doctest: +SKIP
        >>> F.is_satisfiable(cmd='minisat -no-pre')                         # doctest: +SKIP
        >>> F.is_satisfiable(cmd='glucose -pre')                            # doctest: +SKIP
        >>> F.is_satisfiable(cmd='lingeling --plain')                       # doctest: +SKIP
        >>> F.is_satisfiable(cmd='sat4j')                                   # doctest: +SKIP
        >>> F.is_satisfiable(cmd='my-hacked-minisat -pre',sameas='minisat') # doctest: +SKIP
        >>> F.is_satisfiable(cmd='patched-lingeling',sameas='lingeling')    # doctest: +SKIP

        Returns
        -------
        (boolean,assignment or None)
            A pair (answer,witness) where answer is either True when
            F is satisfiable, or False otherwise. If F is satisfiable
            the witness is a satisfiable assignment in form of
            a dictionary, otherwise it is None.

        Raises
        ------
        RuntimeError
           if it is not possible to correctly invoke the solver needed.

        ValueError
           if `sameas` is set and is not the name of a supported solver.

        TypeError
           if F is not a CNF object.

        See Also
        --------
        cnfgen.utils.solver.is_satisfiable : implementation independent of CNF object.
        cnfgen.utils.solver.supported_satsolvers : the SAT solver recognized by `cnfgen`.

        """
        return is_satisfiable(self,
                              cmd=cmd,
                              sameas=sameas,
                              verbose=verbose)
