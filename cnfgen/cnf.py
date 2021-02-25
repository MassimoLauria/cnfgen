#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Build and manipulate CNF formulas

The module `contains facilities to generate cnf formulas, in
order to be printed in DIMACS or LaTeX formats. Such formulas are
ready to be fed to sat solvers.

The module implements the `CNF` object, which is the main entry point
to the `cnfgen` library.

Copyright (C) 2012-2021  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from functools import reduce
from operator import mul
from itertools import product, islice
from itertools import combinations
from math import ceil, log

from cnfgen.basecnf import BaseCNF
from cnfgen.variables import VariablesManager
from cnfgen.utils.parsedimacs import to_dimacs_string, to_dimacs_file


class CNF(VariablesManager, BaseCNF):
    """Propositional formulas in conjunctive normal form.

    A CNF  formula is a  sequence of  clauses, which are  sequences of
    literals. Each literal is either a variable or its negation.

    Use ``add_clause`` to add new clauses to CNF. Clauses will be added
    multiple times in case of multiple insertion of the same clauses.

    For documentation purpose it is possible use have an additional
    comment header at the top of the formula, which will be
    *optionally* exported to LaTeX or dimacs.

    Implementation:  for efficiency reason clauses and variable can
    only be added, and not deleted. Furthermore order matters in
    the representation.

    Examples
    --------
    >>> c=CNF([[1, 2, -3], [-2, 4]])
    >>> print( c.to_dimacs(export_header=False),end='')
    p cnf 4 2
    1 2 -3 0
    -2 4 0
    >>> c.add_clause([-3, 4, -5])
    >>> print( c.to_dimacs(export_header=False),end='')
    p cnf 5 3
    1 2 -3 0
    -2 4 0
    -3 4 -5 0
    >>> print(c[1])
    [-2, 4]
    """

    def __init__(self, clauses=None, description=None):
        """Propositional formulas in conjunctive normal form.

        Parameters
        ----------
        clauses : ordered list of clauses
            a clause with k literals list containing k pairs, each
            representing a literal (see `add_clause`). First element
            is the polarity and the second is the variable, which must
            be an hashable object.

            E.g. (not x3) or x4 or (not x2) is encoded as [(False,"x3"),(True,"x4"),False,"x2")]

        description: string, optional
            a description of the formula
        """
        VariablesManager.__init__(
            self, clauses=clauses, description=description)

    def to_dimacs(self, export_header=True, export_varnames=False):
        """Produce the dimacs encoding of the formula

        The formula is rendered in the DIMACS format for CNF formulas,
        which is a particularly popular input format for SAT solvers [1]_.

        .. note:: By default the DIMACS output is *ascii* encoded,
                  with non-ascii characters replaced.

        Parameters
        ----------
        export_header : bool
            determines whether the formula header should be inserted as
            a comment in the DIMACS output.

        extra_text : str, optional
            Additional text attached to the header

        export_varnames : bool, optional
            determines whether a map from variable indices to variable
            names should be appended to the header.

        Returns
        -------
        string
            the string contains the Dimacs code


        Examples
        --------
        >>> c=CNF([[-1, 2, -3], [-2,-4], [2, 3, -4]])
        >>> print(c.to_dimacs(export_header=False),end='')
        p cnf 4 3
        -1 2 -3 0
        -2 -4 0
        2 3 -4 0

        >>> c=CNF()
        >>> print(c.to_dimacs(export_header=False),end='')
        p cnf 0 0

        References
        ----------
        .. [1] http://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/satformat.ps
        """
        return to_dimacs_string(self,
                                export_header=export_header,
                                export_varnames=export_varnames)

    def latex(self, export_header=True, extra_text=None, full_document=False):
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

        Parameters
        ----------
        export_header : bool, optional
            determines whether the formula header should be inserted as
            a LaTeX comment in the output. By default is True.

        extra_text : str, optional
            Additional text attached to the abstract.

        full_document : bool, optional
            rather than just output the formula, output a document
            that contains it. False by default.

        Returns
        -------
        string
            the string contains the LaTeX code

        Examples
        --------
        >>> c=CNF([[-1, 2, -3], [-2, -4], [2, 3, -4]])
        >>> print(c.latex(export_header=False))
        \\begin{align}
        &       \\left( {\\overline{x}_1} \\lor            {x_2} \\lor {\\overline{x}_3} \\right) \\\\
        & \\land \\left( {\\overline{x}_2} \\lor {\\overline{x}_4} \\right) \\\\
        & \\land \\left(            {x_2} \\lor            {x_3} \\lor {\\overline{x}_4} \\right)
        \\end{align}
        >>> c=CNF()
        >>> print(c.latex(export_header=False))
        \\begin{align}
           \\top
        \\end{align}

        References
        ----------
        .. [1] http://www.latex-project.org/
        """
        clauses_per_page = 40

        latex_preamble = r"""%
\documentclass[10pt,a4paper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{listings}
\usepackage[utf8]{inputenc}
"""

        from io import StringIO
        output = StringIO()

        # formula header as a LaTeX comment
        if export_header:
            for field in self.header:
                tmp = "% {}: {}\n".format(field, self.header[field])
                tmp = tmp.encode('ascii', errors='replace').decode('ascii')
                output.write(tmp)
            output.write("%\n")

        # document opening
        if full_document:
            output.write(latex_preamble)
            output.write("\\begin{document}\n")
            title = self.header['description']
            title = title.replace("_", "\\_")
            output.write("\\title{{{}}}\n".format(title))
            output.write("\\author{CNFgen formula generator}\n")
            output.write("\\maketitle\n")
            output.write("\\noindent\\textbf{Formula header:}\n")
            output.write("\\begin{lstlisting}[breaklines]\n")
            for field in self.header:
                tmp = "{}: {}\n".format(field, self.header[field])
                tmp = tmp.encode('ascii', errors='replace').decode('ascii')
                output.write(tmp)
            output.write("\\end{lstlisting}\n")
            output.write("\\bigskip\n")

        if extra_text is not None and full_document:
            output.write(extra_text)

        # Literal translation
        littext = {}
        for varid, name in enumerate(
                self.all_variable_labels(default_label_format='x_{}'),
                start=1):
            littext[varid] = "           {" + name + "}"
            split_points = [name.find("_"), name.find("^")]
            split_point = min([x for x in split_points if x > 0])
            if split_point < 1:
                littext[-varid] = "  \\overline{" + name + "}"
            else:
                littext[-varid] = "{\\overline{" + \
                    name[:split_point] + "}" + name[split_point:] + "}"

        def write_clause(cls, first, full_document):
            """Write the clause in LaTeX."""
            output.write("\n&" if first else " \\\\\n&")
            output.write("       " if full_document or first else " \\land ")

            # build the latex clause
            if len(cls) == 0:
                output.write("\\square")
            elif full_document:
                output.write(" \\lor ".join(littext[lit] for lit in cls))
            else:
                output.write("\\left( " +
                             " \\lor ".join(littext[lit] for lit in cls) +
                             " \\right)")

        # Output the clauses
        if full_document:
            output.write("\\noindent\\textbf{{CNF with {} variables and and {} clauses:}}\n".
                         format(self._numvar, len(self)))

        output.write("\\begin{align}")

        if len(self) == 0:
            output.write("\n   \\top")
        else:
            for i, clause in enumerate(self._clauses):
                if i % clauses_per_page == 0 and i != 0 and full_document:
                    output.write("\n\\end{align}\\pagebreak")
                    output.write("\n\\begin{align}")
                    write_clause(clause, True, full_document)
                else:
                    write_clause(clause, i == 0, full_document)

        output.write("\n\\end{align}")

        # document closing
        if full_document:
            output.write("\n\\end{document}")

        return output.getvalue()

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
        from .utils import solver
        return solver.is_satisfiable(self,
                                     cmd=cmd,
                                     sameas=sameas,
                                     verbose=verbose)

    ###
    # Various utility function for CNFs
    ###
    def add_parity(self, lits, constant):
        """Adds the CNF encoding of a parity constraint

        E.g. X1 + X2 + X3 = 1 (mod 2) is encoded as

        ( X1 v  X2 v  X3)
        (~X1 v ~X2 v  X3)
        (~X1 v  X2 v ~X3)
        ( X1 v ~X2 v ~X3)

        Parameters
        ----------
        variables : array-like
            literals
        constant : {0,1}
            the constant of the linear equation

        Returns
        -------
        None

        Examples
        --------
        >>> C=CNF()
        >>> C.add_parity([-1,2],1)
        >>> list(C)
        [[-1, 2], [1, -2]]
        >>> C=CNF()
        >>> C.add_parity([-1,2],0)
        >>> list(C)
        [[-1, -2], [1, 2]]
        """
        desired_sign = 1 if constant == 1 else -1
        for signs in product([1, -1], repeat=len(lits)):
            # Save only the clauses with the right polarity
            parity = reduce(mul, signs)
            if parity == desired_sign:
                self.add_clause([lit*sign for lit, sign in zip(lits, signs)])

    def add_linear(self, lits, op, constant):
        """Add a linear constraint to the formula

        Encodes an equality or an inequality constraint on literals (no
        coeffcients) as clauses.

        Parameters
        ----------
        lits : array-like
            literals
        op: str
            one among '<=', ">=", '<', '>', '==', '!='
        constant : integer
            the constant of the linear equation

        Returns
        -------
        None

        Examples
        --------
        >>> c = CNF()
        >>> c.add_linear([-1,2,-3],'>=',1)
        >>> list(c)
        [[-1, 2, -3]]
        >>> c = CNF()
        >>> c.add_linear([-1,2,-3],'>=',3)
        >>> list(c)
        [[-1], [2], [-3]]
        >>> c = CNF()
        >>> c.add_linear([-1,2,-3],'<',2)
        >>> list(c)
        [[1, -2], [1, 3], [-2, 3]]
        >>> c = CNF()
        >>> c.add_linear([1,2,3],'<=',-1)
        >>> list(c)
        [[]]
        >>> c = CNF()
        >>> c.add_linear([1,2,3],'<=',10)
        >>> list(c)
        []
        """
        operators = ['<=', ">=", '<', '>', '==', '!=']
        if op not in operators:
            raise ValueError('Invalid operator, only {} allowed'.
                             format(", ".join(operators)))

        # We reduce to the case of >=
        if op == "==":
            self.add_linear(lits, '<=', constant)
            self.add_linear(lits, '>=', constant)
            return
        elif op == "!=":
            self.add_linear(lits, '<=', constant-1)
            self.add_linear(lits, '>=', constant+1)
            return
        elif op == "<":
            self.add_linear(lits, '<=', constant-1)
            return
        elif op == ">":
            self.add_linear(lits, '>=', constant+1)
            return
        elif op == "<=":
            self.add_linear([-lit for lit in lits], '>=', len(lits) - constant)
            return

        # Tautologies and invalid inequalities
        if constant <= 0:
            return

        if constant > len(lits):
            self.add_clause([])
            return

        k = len(lits) - constant + 1
        for clause in combinations(lits, k):
            self.add_clause(clause)

    def add_loose_majority(self, lits):
        """Clauses encoding a \"at least half\" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = ((len(lits) + 1) // 2)
        return self.add_linear(lits, '>=', threshold)

    def add_loose_minority(self, lits):
        """Clauses encoding a \"at most half\" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = len(lits) // 2
        return self.add_linear(lits, '<=', threshold)

    def add_strict_majority(self, lits):
        """Clauses encoding a "strict majority" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = len(lits)//2 + 1
        return self.add_linear(lits, '>=', threshold)

    def add_strict_minority(self, lits):
        """Clauses encoding a \"at most half\" constraint

        Parameters
        ----------
        lists : iterable(int)
           literals in the constraint
        """
        threshold = (len(lits) - 1) // 2
        return self.add_linear(lits, '<=', threshold)

    def new_mapping(self, *args, labelfmt="f({})={}"):
        """Build the CNF representation of a mapping between two sets.

        Parameters
        ----------

        """

        def __init__(self, startid, B, **kwargs):
            r"""Generator for the clauses of a mapping between to sets

            This generates of the constraints on variables :math:`v(i,j)`
            where :math:`i \in D` and :math:`j in R`, so that they
            represent a mapping (or a relation) between the two sets,
            expressed in unary (i.e. :math:`v(i,j)` expresses whether
            :math:`i` is mapped to :math:`j` or not).

            Parameters
            ----------
            B : BaseBipartiteGraph
                the domain of the mapping

            R : int
                the range of the mapping

            sparsity_pattern : bipartite_graph, optional
                each element of the domain is allowed to be mapped
                only into certain range elements. The graph represents
                which range elements are compatible with a specific
                domain element.

            var_name: function, optional
                given :math:`i` and :math`j` the function must produce the
                name of variable :math`v(i,j)`

            complete: bool, optional
                every element of :math:`D` must have an image (default: true)

            functional: bool, optional
                every element of :math:`D` must have at most one image (default: false)

            surjective: bool, optional
                every element of :math:`R` must have a pre-image (default: false)

            injective: bool, optional
                every element of :math:`R` must have at most one pre-image (default: false)

            nondecreasing: bool, optional
                the mapping is going to be non decresing, with respect to
                the order of domain and range (default: false)

            """
            self.B = B

            # optional parameters of the mapping
            self.Complete = kwargs.pop('complete', True)
            self.Functional = kwargs.pop('functional', False)
            self.Surjective = kwargs.pop('surjective', False)
            self.Injective = kwargs.pop('injective', False)

            self.NonDecreasing = kwargs.pop('nondecreasing', False)

            # variable name scheme
            self.VG = BipartiteEdgesVariables(startid, B)

        def variables(self):
            return self.VG

        def clauses(self):

            U, V = self.B.parts()

            m = self.VG

            # Completeness axioms
            if self.Complete:
                for u in U:
                    yield list(m(u, None))

            # Surjectivity axioms
            if self.Surjective:
                for v in V:
                    yield list(m(None, v))

            # Injectivity axioms
            if self.Injective:
                for v in V:
                    L = self.B.left_neighbors(v)
                    for u1, u2 in combinations(L, 2):
                        yield [-m(u1, v), -m(u2, v)]

            # Functionality axioms
            if self.Functional:
                for u in U:
                    R = self.B.right_neighbors(u)
                    for v1, v2 in combinations(R, 2):
                        yield [-m(u, v1), -m(u, v2)]

            # Mapping is monotone non-decreasing
            if self.NonDecreasing:
                for (u1, u2) in combinations(U, 2):
                    for (v1, v2) in product(self.B.right_neighbors(u1), self.B.right_neighbors(u2)):
                        if v1 > v2:
                            yield [-m(u1, v1), -m(u1, v2)]

    class binary_mapping(object):
        """Binary CNF representation of a mapping between two sets."""

        Domain = None
        Range = None
        Bits = None

        Injective = False
        NonDecreasing = False

        @staticmethod
        def var_name(i, b):
            return "Y_{{{0},{1}}}".format(i, b)

        def variables(self):
            for v, b in product(self.Domain, range(0, self.Bits)):
                yield self.var_name(v, b)

        def __init__(self, D, R, **kwargs):
            r"""Generator for the clauses of a binary mapping between D and :math:`R`

            This generates of the constraints on variables
            :math:`v(i,0)...v(i,k-1)` where :math:`i \in D` and
            :math:`v(i,0)...v(i,k-1)` is a binary of :math:`k` bits, so
            that the first :math:`|R|` string in :math:`{0,1}^k` (in
            lexicographic order) encode the elements of :math:`R`.

            Parameters
            ----------
            D : iterable
                the domain of the mapping

            R : iterable
                the length of the bit strings

            var_name: function, optional
                given :math:`i` and :math`b` the function must produce the
                name of variable :math`v(i,b)`

            injective: bool, optional
                every bitstring must have at most one pre-image (default: false)

            nondecreasing: bool, optional
                the mapping must be non decreasing (default: false)

            """
            self.Domain = list(D)
            self.Range = list(R)
            self.Bits = int(ceil(log(len(R), 2)))

            # optional parameters of the mapping
            self.Injective = kwargs.pop('injective', False)
            self.NonDecreasing = kwargs.pop('nondecreasing', False)
            # variable name scheme
            self.var_name = kwargs.pop('var_name', self.var_name)

            if kwargs:
                raise TypeError('Unexpected **kwargs: %r' % kwargs)

            self.ImageToBits = {}
            self.BitsToImage = {}

            for i, bs in islice(enumerate(product([0, 1], repeat=self.Bits)),
                                len(self.Range)):

                self.ImageToBits[self.Range[i]] = bs
                self.BitsToImage[bs] = self.Range[i]

        def image_to_bitstring(self, im):
            return self.ImageToBits[im]

        def bitstring_to_image(self, bs):
            return self.BitsToImage[bs]

        def forbid_bitstring(self, i, bs):
            """Generates a clause that exclude 'i -> bs' mapping """
            return [(bs[b] == 0, self.var_name(i, self.Bits - 1 - b))
                    for b in range(self.Bits)]

        def forbid_image(self, i, j):
            """Generates a clause that exclude 'i -> j' mapping """
            return self.forbid_bitstring(i, self.ImageToBits[j])

        def clauses(self):

            # Avoid strings that do not correspond to elements from the range
            for i, bs in product(
                    self.Domain,
                    islice(product([0, 1], repeat=self.Bits), len(self.Range),
                           None)):
                yield self.forbid_bitstring(i, bs)

            # Injectivity
            if self.Injective:
                for j in self.Range:
                    for i1, i2 in combinations(self.Domain, 2):
                        yield self.forbid_image(i1, j) + self.forbid_image(
                            i2, j)

            # Enforce Non Decreasing Mapping
            if self.NonDecreasing:
                pairs_of_maps = product(combinations(self.Domain, 2),
                                        combinations(self.Range, 2))

                for (i1, i2), (j1, j2) in pairs_of_maps:
                    yield self.forbid_image(i1, j2) + self.forbid_image(i2, j1)
