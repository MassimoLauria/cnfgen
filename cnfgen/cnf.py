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
from collections import OrderedDict
from math import ceil, log

from cnfgen.info import info
from cnfgen.variables import BipartiteEdgesVariables


class CNF:
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
    >>> print( c.dimacs(export_header=False),end='')
    p cnf 4 2
    1 2 -3 0
    -2 4 0
    >>> c.add_clause([-3, 4, -5])
    >>> print( c.dimacs(export_header=False),end='')
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
        default_description = 'Formula in CNF'
        self.header = OrderedDict()
        if description is not None:
            self.header['description'] = description
        else:
            self.header['description'] = default_description

        self.header['generator'] = "{} ({})".format(info['project'],
                                                    info['version'])
        self.header['copyright'] = info['copyright']
        self.header['url'] = info['url']

        # Problem representation via encoders and variable groups.
        self._variable_groups = []
        self._encoders = []

        # Initial empty formula
        self._numvar = 0
        self._clauses = []
        for c in clauses or []:
            self.add_clause(c)

    def __str__(self):
        """String representation of the formula
        """
        n = self._numvar
        m = len(self._clauses)
        text = "CNF with {} vars and {} clauses".format(n, m)
        if 'description' in self.header:
            text += " -- " + self.header['description']
        return text

    def __len__(self):
        """Number of clauses in the formula
        """
        return len(self._clauses)

    def __iter__(self):
        """Number of clauses in the formula
        """
        return iter(self._clauses)

    def __getitem__(self,idx):
        """Number of clauses in the formula
        """
        return self._clauses[idx][:]

    def variables_number(self):
        return self._numvar

    def all_variable_labels(self,default_label_format='x{}'):
        """Produces the labels of all the variables.

Variable belonging to special variable groups are translated
accordingly. The others get a standard variable name as defined by the
argument `default_label_format` (e.g. 'x{}')."""
        # We cycle through all variables,
        #
        ranges = [(g.ranges()[0], g.ranges()[1], g)
                  for g in self._variable_groups]
        ranges.sort()

        varid = 1
        for vg in self._variable_groups:
            begin = vg.firstID()
            while varid < begin:
                yield default_label_format.format(varid)
                varid += 1
            yield from vg.labels()
            varid += len(vg)
        while varid <= self._numvar:
            yield default_label_format.format(varid)
            varid += 1
        assert varid == self._numvar+1

    def update_variable_number(self, new_value):
        """Raises the number of variable in the formula to `new_value`

If the formula has already at least `new_value` variables, this does
not have any effect."""
        self._numvar = max(self._numvar, new_value)

    #
    # Internal implementation methods, use at your own risk!
    #

    # def _uncompress_clause(self, clause):
    #     """(INTERNAL USE) Uncompress a clause from the numeric representation.

    #     Arguments:
    #     - `clause`: clause to be uncompressed

    #     >>> c=CNF()
    #     >>> c.add_clause([(True,"x"),(False,"y")])
    #     >>> print(c._uncompress_clause([-1,-2]))
    #     [(False, 'x'), (False, 'y')]
    #     """
    #     return [(l > 0, self._index2name[abs(l)]) for l in clause]

    # def _compress_clause(self, clause):
    #     """Convert a clause to its numeric representation.

    #     For reason of efficiency, clauses are memorized as tuples of
    #     integers. Each integer correspond to a variable, with sign +1
    #     or -1 depending whether it represents a positive or negative
    #     literal. The correspondence between the numbers and the
    #     variables names depends on the formula itself

    #     Parameters
    #     ----------
    #     clause: list of pairs
    #         a clause, in the form of a list of literals, which are
    #         pairs (bool,string).

    #     Returns
    #     -------
    #     a tuple of int

    #     Examples
    #     --------
    #     >>> c=CNF()
    #     >>> c.add_clause([(True,"x"),(False,"y")])
    #     >>> print(c._compress_clause([(False, 'x'), (False, 'y')]))
    #     (-1, -2)

    #     """
    #     try:
    #         return tuple(
    #             (1 if p else -1) * self._name2index[n] for p, n in clause)
    #     except TypeError:
    #         raise TypeError("{} is not a well formatted clause".format(clause))

    # def _add_compressed_clauses(self, clauses):
    #     """(INTERNAL USE) Add to the CNF a list of compressed clauses.

    #     This method uses the internal compressed clause representation
    #     to add a large batch of data  into the CNF.  It does not check
    #     for internal  coherence conditions,  and it  does not  need to
    #     convert between  internal and external  clause representation,
    #     so it  is very fast.   When assertions  are tested, a  call to
    #     this method will  disable the standard API, since  the CNF can
    #     be in an inconsistent state.

    #     Whenever the high level API is used with an inconsisten state
    #     the code will fail some assertion.

    #     In particular it does not check if the indexes correspond to a
    #     variable in the formula.

    #     To test consistency and re-enable the API, please use method
    #     `CNF.debug()`.

    #     Arguments:
    #     - `clauses`: a sequence of compressed clauses.

    #     >>> c=CNF()

    #     We add the variables in advance, so that the internal status
    #     stays coherent.

    #     >>> c.add_variable("x")
    #     >>> c.add_variable("y")
    #     >>> c.add_variable("z")

    #     When we add some compressed clauses, we need to test the
    #     internal status of the object. If the test is positive, then
    #     the high level API is available again.

    #     >>> c._add_compressed_clauses([[-1,2,3],[-2,1],[1,-3]])
    #     >>> c.debug()
    #     True
    #     >>> print(c.dimacs(export_header=False))
    #     p cnf 3 3
    #     -1 2 3 0
    #     -2 1 0
    #     1 -3 0

    #     If we call the internal API several times, we need to test the
    #     object only once.

    #     >>> c._add_compressed_clauses([[-2,-3]])
    #     >>> c._add_compressed_clauses([[-1, 2]])
    #     >>> c.debug()
    #     True
    #     >>> print(c.dimacs(export_header=False))
    #     p cnf 3 5
    #     -1 2 3 0
    #     -2 1 0
    #     1 -3 0
    #     -2 -3 0
    #     -1 2 0
    #     """
    #     self._clauses.extend(tuple(c) for c in clauses)

    def debug(self, allow_opposite=False, allow_repetition=False):
        """Check if the formula representation is correct

        Params
        ------
        allow_repetition: bool, optional
            Allow literal repetition.

            Useful for sanity check. If the flag is `False` and the
            clause contain two copies of the same literal, then
            `ValueError` is raised. (default: False)

        allow_opposite: bool, optional
            True if and only if the clause can have opposite literal.

            Useful for sanity check. If the flag is `False` and the
            clause contain two opposite literals, then `ValueError`
            is raised. (default: False)

        Certain manipulation methods are not safe if used incorrectly,
        so the CNF may be corrupted. This method tests if that was not
        the case.

        Examples
        --------
        >>> c=CNF()
        >>> c.add_clauses_from([[-1,2],[1,0,-2],[1,3]])
        >>> c.debug()
        False

        """
        # number of variables and clauses
        N = self._numvar

        # Count clauses and check literal representation
        for clause in self._clauses:
            for literal in clause:
                if not 0 < abs(literal) <= N:
                    return False

        for clause in self._clauses:
            sclause = sorted(clause, key=abs)
            n = len(sclause)
            for i in range(n-1):
                if not allow_repetition and sclause[i] == sclause[i+1]:
                    return False
                if not allow_opposite and sclause[i] == -sclause[i+1]:
                    return False

        # formula passed all tests
        return True

    def add_clause(self, clause):
        """Add a clause to the CNF.

        E.g. (not x3) or x4 or (not x2) is encoded as [-1, 4, -2]

        All variable mentioned in the clause will be added to the list
        of variables  of the CNF,  in the  order of appearance  in the
        clauses.

        No check is done on the clauses.

        Parameters
        ----------
        clause: list of (bool,str)
            the clause to be added in the CNF

            A clause with k literals is a list with k pairs.
            First coords are the polarities, second coords are utf8
            encoded strings with variable names.

            Clause may contain repeated or opposite literal, but this
            behavior can be modified by the optional flags.

            Clauses are added with repetition, i.e. if the same clause
            is added twice then it will occur twice in the
            formula too.
        """
        if len(clause) == 0:
            self._clauses.append([])
            return
        maxid = max([abs(literal) for literal in clause])
        self._numvar = max(maxid, self._numvar)
        self._clauses.append(list(clause))

    def add_clauses_from(self, clauses):
        """Add a sequence of clauses to the CNF"""
        for c in clauses:
            self.add_clause(c)


    def clauses(self):
        """Return the list of clauses
        """
        return self.__iter__()


    def dimacs(self, export_header=True, export_varnames=False):
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
        >>> print(c.dimacs(export_header=False),end='')
        p cnf 4 3
        -1 2 -3 0
        -2 -4 0
        2 3 -4 0

        >>> c=CNF()
        >>> print(c.dimacs(export_header=False),end='')
        p cnf 0 0

        References
        ----------
        .. [1] http://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/satformat.ps

        """
        from io import StringIO
        output = StringIO()

        # Count the number of variables and clauses
        n = self._numvar
        m = len(self)

        # Produce header in ascii compatible format
        if export_header:
            # remove non ascii text
            for field in self.header:
                tmp = "c {}: {}\n".format(field, self.header[field])
                tmp = tmp.encode('ascii', errors='replace').decode('ascii')
                output.write(tmp)
            output.write("c\n")

        if export_varnames:
            for varid, label in enumerate(self.all_variable_labels(), start=1):
                output.write("c varname {0} {1}\n".format(varid, label))
            output.write("c\n")

        # Formula specification
        output.write("p cnf {0} {1}\n".format(n, m))
        # Clauses
        for cls in self._clauses:
            print(*cls, 0, file=output)
        return output.getvalue()

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
                littext[-varid] = "{\\overline{" + name[:split_point] + "}" + name[split_point:] + "}"

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

    class unary_mapping(object):
        """Unary CNF representation of a mapping between two sets."""

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
                    for (v1, v2) in product(self.B.right_neighbors(u1),self.B.right_neighbors(u2)):
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
