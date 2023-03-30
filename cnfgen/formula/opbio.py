#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF formula with read/write capabilities"""

import os
from io import StringIO

from cnfgen.formula.cnfio import guess_output_format

from cnfgen.utils.latexoutput import to_latex_string, to_latex_document
from cnfgen.utils.opb    import to_opb_file
from cnfgen.formula.baseopb import BaseOPB

class OPBio(BaseOPB):
    """OPB class with I/O capabilities

    - read and write DIMACS
    - write to OPB format
    - write to LaTeX format

    Examples
    --------
    >>> c=OPBio()
    >>> c.cardinality_geq([1,2,4,-3],3)
    >>> print( c.to_opb(),end='')
    * #variable= 4 #constraint= 1
    +1 x1 +1 x2 +1 x4 +1 ~x3 >= 3
    """
    def __init__(self, constraints=None, description=None):
        BaseOPB.__init__(self, constraints=constraints, description=description)

    def to_opb(self):
        """Produce the OPB encoding of the formula

        .. note:: the OPB output is *ascii* encoded,
                  with non-ascii characters replaced.

        Returns
        -------
        string
            the string contains the OPB code

        Examples
        --------
        >>> c=OPBio()
        >>> c.cardinality_leq([1,4,2],2)
        >>> c.cardinality_eq([3,-4],1)
        >>> print(c.to_opb(),end='')
        * #variable= 4 #constraint= 2
        +1 ~x1 +1 ~x4 +1 ~x2 >= 1
        +1 x3 +1 ~x4 = 1

        >>> c=OPBio()
        >>> print(c.to_opb(),end='')
        * #variable= 0 #constraint= 0

        References
        ----------
        .. [1] https://www.cril.univ-artois.fr/PB12/format.pdf
        """
        output = StringIO()
        to_opb_file(self, output, export_header=False, export_varnames=False)
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
        >>> c=OPBio()
        >>> c.cardinality_geq([1,3,-2,4],3)
        >>> c.cardinality_eq([1,3,-2,4],3)
        >>> c.add_constraint([(2,3),(2,-1),(1,-2),">=",2])
        >>> print(c.to_latex())
        \\begin{align}
        & {x_1} + {x_3} + {\\overline{x}_2} + {x_4} \\geq 3 \\\\
        & {x_1} + {x_3} + {\\overline{x}_2} + {x_4} = 3 \\\\
        & 2{x_3} + 2{\\overline{x}_1} + {\\overline{x}_2} \\geq 2
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

        The formula is saved on file, in either as a OPB file, or
        as a LaTeX document.

        If `fileformat` is either `opb` or `tex` then the output is
        saved in the corresponding format.

        If `fileformat` is `None`, then OPB format is the default
        output format unless the file name ends with '.tex'.

        Parameters
        ----------
        fileorname: file name or file object
            where to print the file (default: <stdout>)

        fileformat: 'tex', 'opb' or None
            format of the output file

        export_header: bool
            print some additional information on the output file (default: True)

        export_varnames: bool
            add the variable ID --> name information in the dimacs (default: True)

        extra_text: str
            additional text to be included in the LaTeX output document
        """
        fileformat = guess_output_format(fileorname,fileformat)

        if fileformat == 'latex':
            to_latex_document(self,
                              fileorname,
                              export_header=export_header,
                              extra_text=extra_text)
        else:
            to_opb_file(self,
                        fileorname,
                        export_header=export_header,
                        export_varnames=export_varnames)
