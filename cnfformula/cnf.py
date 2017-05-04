#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Build and manipulate CNF formulas

The module `contains facilities to generate cnf formulas, in
order to be printed in DIMACS or LaTeX formats. Such formulas are
ready to be fed to sat solvers.

The module implements the `CNF` object, which is the main entry point
to the `cnfformula` library. 



Copyright (C) 2012, 2013, 2014, 2015, 2016, 2017  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""


from __future__ import print_function
from itertools import product,islice
from itertools import combinations,combinations_with_replacement
from collections import Counter
from collections import namedtuple

import re
from math import ceil,log,factorial

from . import prjdata as pd
from .graphs import bipartite_sets,neighbors

class CNF(object):
    """Propositional formulas in conjunctive normal form.

    A CNF  formula is a  sequence of  clauses, which are  sequences of
    literals. Each literal is either a variable or its negation.

    Use ``add_variable`` method to add a variable to the formula. Two
    variable with the same name are considered the same variable, add
    successive additions do not have any effect.

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
    >>> c=CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], \
              [(False,"x2"),(True,"x4")] ])
    >>> print( c.dimacs(export_header=False) )
    p cnf 4 2
    1 2 -3 0
    -2 4 0
    >>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
    >>> print( c.dimacs(export_header=False))
    p cnf 5 3
    1 2 -3 0
    -2 4 0
    -3 4 -5 0
    """

    def __init__(self, clauses=None, header=None):
        """Propositional formulas in conjunctive normal form.

        Parameters
        ----------
        clauses : ordered list of clauses
            a clause with k literals list containing k pairs, each
            representing a literal (see `add_clause`). First element
            is the polarity and the second is the variable, which must
            be an hashable object.

            E.g. (not x3) or x4 or (not x2) is encoded as [(False,"x3"),(True,"x4"),False,"x2")]

        header: string, optional
            a preamble which documents the formula
        """

        # Internal documentation of the formula
        self._header = header or \
                       "Generated with `cnfgen`\n(C) {}\n{}\n\n".format(
                           pd.__copyright__,
                           pd.__url__)

        # Initial empty formula
        self._length          = 0
        self._constraints     = []

        # Variable indexes <--> Variable names correspondence
        # first variable is indexed with 1.
        self._index2name      = [None]
        self._name2index      = dict()
        self._name2descr      = dict()


        # How strict is the addition of constraints
        self._allow_literal_repetitions=False
        self._allow_opposite_literals=False
        self._auto_add_variables=True

        # Load the initial data into the CNF
        for c in clauses or []:
            self.add_clause(c)


    @property
    def header(self):
        """Brief description of the formula"""
        return self._header

    @header.setter
    def header(self, value):
        self._header = value

    #
    #
    # (Strict?) Rules for constraints addition
    #
    #
    def mode_strict(self):
        """Constraints are added with strict rules

        In particular this sets to `False`:
          - :py:attr:`allow_literal_repetition`
          - :py:attr:`allow_opposite_literals`
          - :py:attr:`auto_add_variables`
 
        """
        self.allow_literal_repetitions = False
        self.allow_opposite_literals   = False
        self.auto_add_variables        = False

    def mode_unchecked(self):
        """Constraints are added with no rule

        In particular this sets to `True`:
          - :py:meth:`CNF.allow_literal_repetitions`
          - :py:meth:`CNF.allow_opposite_literals`
          - :py:meth:`CNF.auto_add_variables`
 
        """
        self.allow_literal_repetitions = True
        self.allow_opposite_literals   = True
        self.auto_add_variables        = True
        
    def mode_default(self):
        """Constraint are added with default rules

        In particular this sets to `False`:
          - :py:meth:`CNF.allow_literal_repetitions`
          - :py:meth:`CNF.allow_opposite_literals`

        and sets to `True`:
          - :py:meth:`CNF.auto_add_variables`
 
        """
        self.allow_literal_repetitions   = False
        self.allow_opposite_literals     = False
        self.auto_add_variables          = True

    @property
    def allow_literal_repetitions(self):
        """True if and only if the constraint can have repeated literal.
        
        Useful for sanity check. If the flag is `False` and the
        clause contain two copies of the same literal, then
        `ValueError` is raised. (default: False)
        """
        return self._allow_literal_repetitions

    @allow_literal_repetitions.setter
    def allow_literal_repetitions(self,value):
        self._allow_literal_repetitions = bool(value)
        if self._auto_add_variables and \
           self._allow_literal_repetitions and \
           self._allow_opposite_literals:
            self._check_and_compress_literals = self._check_and_compress_literals_unsafe
        else:
            self._check_and_compress_literals = self._check_and_compress_literals_safe
    
    @property
    def allow_opposite_literals(self):
        """True if and only if the clause can have opposite literals.

        Useful for sanity check. If the flag is `False` and the
        clause contain two opposite literals, then `ValueError`
        is raised. (default: False)
        """
        return self._allow_opposite_literals

    @allow_opposite_literals.setter
    def allow_opposite_literals(self,value):
        self._allow_opposite_literals = bool(value)
        if self._auto_add_variables and \
           self._allow_literal_repetitions and \
           self._allow_opposite_literals:
            self._check_and_compress_literals = self._check_and_compress_literals_unsafe
        else:
            self._check_and_compress_literals = self._check_and_compress_literals_safe
    
    @property
    def auto_add_variables(self):
        """If `True` the clause can contain new variables.

        New variables occurring in the clause will be added to the
        formula, unless the flag is `False`. In that case when
        a clause contains an unknow variables, `ValueError` is
        raised. (default: True)
        """
        return self._auto_add_variables

    @auto_add_variables.setter
    def auto_add_variables(self,value):
        self._auto_add_variables = bool(value)
        if self._auto_add_variables and \
           self._allow_literal_repetitions and \
           self._allow_opposite_literals:
            self._check_and_compress_literals = self._check_and_compress_literals_unsafe
        else:
            self._check_and_compress_literals = self._check_and_compress_literals_safe
            
    
    #
    # Implementation of some standard methods
    #
    def _compressed_clauses(self):
        """Iterates over all (compressed) clauses of the CNF
        """
        length = 0
        for cnst in self._constraints:
            for clause in cnst.clauses():
                length += 1
                yield clause

        if self._length is None:
            self._length = length

        assert length == self._length

    def __iter__(self):
        """Iterates over all clauses of the CNF
        """
        for clause in self._compressed_clauses():
            yield self._uncompress_literals(clause)
                
    def __str__(self):
        """String representation of the formula
        """
        return self._header

    def __len__(self):
        """Number of clauses in the formula
        """
        if self._length is None:
            self._length = 0
            for cnst in self._constraints:
                self._length += cnst.n_clauses()

        return self._length

    
    #
    # Internal implementation methods, use at your own risk!
    #
    def _uncompress_literals(self, literals):
        """(INTERNAL USE) Uncompress a clause from the numeric representation.

        Parameters
        ----------
        literals : a list of int

        Returns
        -------
        a list of pairs (bool,string).
        
        Examples
        --------
        >>> c=CNF()
        >>> c.add_clause([(True,"x"),(False,"y")])
        >>> print(c._uncompress_literals([-1,-2]))
        [(False, 'x'), (False, 'y')]
        """
        return [ (l>0, self._index2name[abs(l)]) for l in literals ]

    def _check_and_compress_literals(self, literals):
        """Convert a list of literals to its numeric representation.

        For reason of efficiency, sequences of literals are memorized
        as tuples of integers. Each integer correspond to a variable,
        with sign +1 or -1 depending whether it represents a positive
        or negative literal. The correspondence between the numbers
        and the variables names depends on the formula itself.

        This methods checks and honors the constraints imposed to the
        literals at the time of insertion. They depends on the choices
        of the CNF user. In particular it is possible to enforce
        either more or less strict rules with :py:meth:`mode_strict`,
        :py:meth:`mode_unchecked`, and :py:meth:`mode_default`.

        Parameters
        ----------
        literals: list of pairs
            a list of literals, which are pairs (bool,string).

        Returns
        -------
        a tuple of int

        Examples
        --------
        >>> c=CNF()
        >>> c.add_clause([(True,"x"),(False,"y")])
        >>> print(c._check_and_compress_literals([(False, 'x'), (False, 'y')]))
        (-1, -2)

        See Also
        --------
        allow_literal_repetition : allows the same literal more than once in a clause
        allow_opposite_literals : allows opposite literals in a clause
        auto_add_variables : automatically add new variables to the formula
        mode_strict : all checks during clause insertion
        mode_default : all checks but allow new variables
        mode_unchecked : no checks at all

        Raises
        ------
        KeyError
            in case clause insertion is unchecked and the clause
            contains a variable which is unknown to the formula.
        """

        # A clause must be an immutable object
        try:
            hash(tuple(literals))
        except TypeError:
            raise TypeError("%s is not a well formatted sequence of literals" %literals)

        # Check literal repetitions
        if (not self.allow_literal_repetitions) and len(set(literals)) != len(literals):
            raise ValueError("Forbidden repeated literals in the constraint {}".format(literals))

        # Check opposite literals
        if not self.allow_opposite_literals:
            positive     = set([v for (p,v) in literals if p ])
            negative     = set([v for (p,v) in literals if not p ])
            if len(positive & negative)>0:
                emsg = "{ " + ", ".join(positive & negative) + " }"
                raise ValueError("Following variable occur with opposite literals: {}".format(emsg))

        # Add the compressed clause
        try:
            return tuple((1 if p else -1) * self._name2index[n] for p, n in literals)
        except KeyError,error:
            if not self.auto_add_variables:
                raise ValueError("The clause contains unknown variable: {}".format(error))
            else:
                for _, var in literals:
                    self.add_variable(var)
                return tuple((1 if p else -1) * self._name2index[n] for p, n in literals)

    def _check_and_compress_literals_unsafe(self, literals):
        """(INTERNAL USE) Builds internal representation of literals with no checks.

        See Also
        --------
        _check_and_compress_literals : safe version of the same method
        """
        return tuple((1 if p else -1) * self._name2index[n] for p, n in literals)

    # By default we start with the safe version
    _check_and_compress_literals_safe  = _check_and_compress_literals

    def _add_compressed_constraints(self, constraints):
        """(INTERNAL USE) Add a list of compressed constraints.

        This method uses the internal compressed constraint
        representation to add a large batch of data into the formula.
        It does not check for internal coherence conditions, and it
        does not need to convert between internal and external
        literals representation, so it is very fast. It is recommended
        to use :py:meth:`_chech_coherence` after using this.

        Parameters
        ----------
        constraints : a list of constraints

        See Also
        --------
        _check_coherence : test that the internal representation is coherent.

        Examples
        --------
        >>> c=CNF()

        We add the variables in advance, so that the internal status
        stays coherent.

        >>> c.add_variable("x")
        >>> c.add_variable("y")
        >>> c.add_variable("z")

        When we add some compressed clauses, we should test the
        internal status of the object. If the test is positive, then
        working with the high level API is possible again.

        >>> c._add_compressed_constraints([disj(-1,2,3),disj(-2,1),disj(1,-3)])
        >>> c._check_coherence()
        True
        >>> print(c.dimacs(export_header=False))
        p cnf 3 3
        -1 2 3 0
        -2 1 0
        1 -3 0

        If we call the internal API several times, we need to test the
        object only once.

        >>> c._add_compressed_constraints([disj(-2,-3)])
        >>> c._add_compressed_constraints([disj(-1, 2)])
        >>> c._check_coherence()
        True
        >>> print(c.dimacs(export_header=False))
        p cnf 3 5
        -1 2 3 0
        -2 1 0
        1 -3 0
        -2 -3 0
        -1 2 0

        """
        if self._length is not None:
            self._length += sum(c.n_clauses() for c in constraints)
        self._constraints.extend(constraints)


    def _check_coherence(self):
        """Check if the formula is internally consistent.

        Certain fast manipulation methods are not safe if used
        incorrectly, so the CNF object may be corrupted. This method
        tests if that was not the case.

        >>> c=CNF()
        >>> c.add_variable("x")
        >>> c.add_variable("y")

        We add clauses mentioning three variables, and the formula is
        not coherent.

        >>> c._add_compressed_constraints([disj(-1,2),disj(1,-2),disj(1,3)])
        >>> c._check_coherence()
        False
        """
        varindex=self._name2index
        varnames=self._index2name
        
        # number of variables and clauses
        N=len(varindex.keys())
        
        # Consistency in the variable dictionary
        if N != len(varnames)-1:
            return False

        for i in range(1,N+1):
            if varindex[varnames[i]]!=i:
                return False


        # Count clauses and check literal representation
        est_length = 0
        for cnst in self._constraints:
            if type(cnst) in (weighted_eq, weighted_geq):
                for weight,lit in cnst:
                    if not 0 < abs(lit) <= N:
                        return False
            else:
                for lit in cnst:
                    if not 0 < abs(lit) <= N:
                        return False
            est_length += cnst.n_clauses()

        if len(self) != est_length:
            return False

        # formula passed all tests
        return True


    #
    # High level API
    #
    def add_variable(self,var,description=None):
        """Add a variable to the formula (if not already resent).

        The variable must be `hashable`. I.e. it must be usable as key
        in a dictionary.  It raises `TypeError` if the variable cannot
        be hashed.

        Parameters
        ----------
        var: hashable
             the variable name to be added/updated. It can be any
             hashable object (i.e. a dictionary key).
        description: str, optional
             an explanation/description/comment about the variable.
        """
        try:
            if not var in self._name2index:
                # name correpsond to the last variable so far
                self._index2name.append(var)
                self._name2index[var] = len(self._index2name)-1
        except TypeError:
            raise TypeError("%s is not a legal variable name" %var)

        # update description
        if description is not None:
            self._name2descr[var] = description


    def add_clause(self,clause):
        """Add a clause to the CNF.

        E.g. (not x3) or x4 or (not x2) is encoded as
             [(False,u"x3"),(True,u"x4"),(False,u"x2")]

        
        By default all variable mentioned in the clause will be added
        to the list of variables of the CNF, in the order of
        appearance in the clauses. The default applies as long as
        :py:attr:`auto_add_variables` is set o true.

        In particular the behavior and the constraints that are
        imposed on the clauses at the time of insertion depends on the
        choices of the class user. In particular it is possible to
        enforce either more or less strict rules with
        :py:meth:`mode_strict`, :py:meth:`mode_unchecked`, and
        :py:meth:`mode_default`.
        
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
 

        See Also
        --------
        allow_literal_repetition : allows the same literal more than once in a clause
        allow_opposite_literals : allows opposite literals in a clause
        auto_add_variables : automatically add new variables to the formula
        mode_strict : all checks during clause insertion
        mode_default : all checks but allow new variables
        mode_unchecked : no checks at all

        Raises
        ------
        KeyError
            in case clause insertion is unchecked and the clause
            contains a variable which is unknown to the formula.
        
        ValueError
            in case the sequence of literals do not satisfies the rules.

        TypeError
            the sequence of literals is not made by pairs of immutable objects.
        """
        self._constraints.append( disj(*self._check_and_compress_literals(clause)))
        if self._length is not None:
            self._length += 1
  

    def variables(self):
        """Returns (a copy of) the list of variable names.
        """
        vars_iterator = iter(self._index2name)
        vars_iterator.next()
        return vars_iterator
    

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
        cnfformula.utils.solver.is_satisfiable : implementation independent of CNF object.
        cnfformula.utils.solver.supported_satsolvers : the SAT solver recognized by `cnfformula`.

        """
        from .utils import solver
        return solver.is_satisfiable(self, cmd=cmd, sameas=sameas, verbose=verbose)

    #
    #  Output formats
    #
    def dimacs(self, export_header=True, extra_text=None):
        """Produce the dimacs encoding of the formula

        The formula is rendered in the DIMACS format for CNF formulas,
        which is a particularly popular input format for SAT solvers [1]_.

        Parameters
        ----------
        export_header : bool
            determines whether the formula header should be inserted as
            a comment in the DIMACS output.

        extra_text : str, optional
            Additional text attached to the header

        Returns
        -------
        string
            the string contains the Dimacs code


        Examples
        --------
        >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")],\
                   [(False,"x_2"),(False,"x_4")], \
                   [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
        >>> print(c.dimacs(export_header=False))
        p cnf 4 3
        -1 2 -3 0
        -2 -4 0
        2 3 -4 0

        >>> c=CNF()
        >>> print(c.dimacs(export_header=False))
        p cnf 0 0
        <BLANKLINE>

        References
        ----------
        .. [1] http://www.satlib.org/Benchmarks/SAT/satformat.ps

        """
        from cStringIO import StringIO
        output = StringIO()
        self._dimacs_dump_clauses(output, export_header, extra_text)
        return output.getvalue()

    def _dimacs_dump_clauses(self, output=None, export_header=True, extra_text=None):
        """Dump the dimacs encoding of the formula to the file-like output

        This is for internal use only. It produces the dimacs output
        of the clauses, and write then on the output buffer, which is
        tipically a StringIO.
        """

        # Count the number of variables and clauses
        n = len(self._index2name)-1
        m = len(self)

        # A nice header
        if export_header:
            for line in self.header.split("\n")[:-1]:
                output.write(("c "+line).rstrip()+"\n")

            if extra_text is not None:
                for line in extra_text.split("\n"):
                    output.write(("c "+line).rstrip()+"\n")


        # Formula specification
        output.write("p cnf {0} {1}".format(n, m))

        if m == 0:
            output.write("\n")   # this newline makes `lingeling` solver happy

        # Clauses
        for cls in self._compressed_clauses():
            output.write("\n" + " ".join([str(l) for l in cls + (0,)]))

    def opb(self, export_header=True, extra_text=None):
        """Produce the OPB encoding of the formula

        The formula is rendered in the OPB format, which is
        a particularly popular input format for pseudo boolean SAT
        solvers [1]_.

        Parameters
        ----------
        export_header : bool
            determines whether the formula header should be inserted as
            a comment in the OPB output.

        extra_text : str, optional
            Additional text attached to the header

        Returns
        -------
        string
            the string contains the OPB code


        Examples
        --------
        >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")],\
                   [(False,"x_2"),(False,"x_4")], \
                   [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
        >>> print(c.opb(export_header=False))
        * #variable= 4 #constraint= 3
        *
        -1 x1 +1 x2 -1 x3 >= -1;
        -1 x2 -1 x4 >= -1;
        +1 x2 +1 x3 -1 x4 >= 0;
        <BLANKLINE>

        >>> c=CNF()
        >>> print(c.opb(export_header=False))
        * #variable= 0 #constraint= 0
        *
        <BLANKLINE>

        References
        ----------
        .. [1] http://www.cril.univ-artois.fr/PB12/format.pdf

        """
        from cStringIO import StringIO
        output = StringIO()

        # count the constraints (can't encode xor in OPB directly)
        nvariables   = len(self._index2name)-1
        nconstraints = 0
        for c in self._constraints:
            if type(c)==xor:
                nconstraints += c.n_clauses()
            else:
                nconstraints += 1
                
        output.write("* #variable= {} #constraint= {}\n*\n".format(
            nvariables,nconstraints))

        # A nice header
        if export_header:
            for line in self.header.split("\n")[:-1]:
                output.write(("* "+line).rstrip()+"\n")

            if extra_text is not None:
                for line in extra_text.split("\n"):
                    output.write(("* "+line).rstrip()+"\n")

        def _print_lit_ineq(lits,sign, thr):

            lhs = " ".join( "{}1 x{}".format("+" if l >= 0 else "-",abs(l)) for l in lits)
            rhs = str(thr - len([i for i in lits if i<0]))
            output.write(lhs + " " + sign + " " + rhs + ";\n")

        def _print_lin_ineq(cnst):

            lhs = " ".join( "{:+} x{}".format(w,v) for w,v in cnst)
            if type(cnst)==weighted_eq:
                rhs = str(cnst.value)
                op  = "="
            elif type(cnst)==weighted_geq:
                rhs = str(cnst.threshold)
                op  = ">="
            else:
                raise RuntimeError("[Internal Error] Unknown type of constraints found: {}".format(type(cnst)))
            output.write(lhs + " " + op + " " + rhs + ";\n")
                    
        # Normalize inequalities
        for cnst in self._constraints:

            # Representation clause by clause
            if type(cnst) in [disj,xor]:
                for cls in cnst.clauses():
                    _print_lit_ineq(cls,">=",1)
                
            # Representation by equation
            elif type(cnst)==eq:
                _print_lit_ineq(cnst,"=",cnst.value)

            # Representation by inequality
            elif type(cnst)==geq:
                _print_lit_ineq(cnst,">=",cnst.threshold)

            elif type(cnst)==greater:
                _print_lit_ineq(cnst,">=",cnst.threshold+1)

            elif type(cnst)==leq:
                _print_lit_ineq([-l for l in cnst],">=", len(cnst) - cnst.threshold)

            elif type(cnst)==less:
                _print_lit_ineq([-l for l in cnst],">=", len(cnst) - cnst.threshold + 1)

            elif type(cnst) in [weighted_eq,weighted_geq]:
                _print_lin_ineq(cnst)
            else:
                raise RuntimeError("[Internal Error] Unknown type of constraints found: {}".format(type(cnst)))
        
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
        >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")],\
                   [(False,"x_2"),(False,"x_4")], \
                   [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
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

        latex_preamble=r"""%
\documentclass[10pt,a4paper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{listings}
"""
        
        from cStringIO import StringIO
        output = StringIO()
        
        # formula header as a LaTeX comment
        if export_header:
            for s in self.header.split("\n")[:-1]:
                output.write( ("% "+s).rstrip()+"\n" )

        # document opening
        if full_document:
            output.write(latex_preamble)
            output.write("\\begin{document}\n")
            title=self.header.split('\n')[0]
            title=title.replace("_","\_")
            output.write("\\title{{{}}}\n".format(title))
            output.write("\\author{CNFgen formula generator}\n")
            output.write("\\maketitle\n")
            output.write("\\noindent\\textbf{Formula header:}\n")
            output.write("\\begin{lstlisting}[breaklines]\n")
            output.write(self.header)
            output.write("\\end{lstlisting}\n")
            output.write("\\bigskip\n")

        if extra_text is not None and full_document:
            output.write(extra_text)
                
        def map_literals(l):
            """Map literals to LaTeX string"""
            assert l!=0
            if l>0 :
                return  "           {"+str(self._index2name[l])+"}"
            else:
                name = self._index2name[-l]
                split_point=name.find("_")
                return "{\\overline{"+name[:split_point]+"}"+name[split_point:]+"}"

        def write_clause(cls, first,full_document):
            """Write the clause in LaTeX."""
            output.write("\n&" if first  else " \\\\\n&")
            output.write("       " if full_document or first else " \\land ")

            # build the latex clause
            if len(cls) == 0:
                output.write("\\square")
            elif full_document:
                output.write(" \\lor ".join(map_literals(l) for l in cls))
            else:
                output.write("\\left( " + \
                             " \\lor ".join(map_literals(l) for l in cls) + \
                             " \\right)")

        # Output the clauses
        clauses_number = len(self)
        if full_document:
            output.write("\\noindent\\textbf{{CNF with {} variables and and {} clauses:}}\n".\
                         format(len(self._name2index),clauses_number))

        output.write("\\begin{align}")
        
        if clauses_number==0:
            output.write("\n   \\top")
        else:
            for i,clause in enumerate(self._compressed_clauses()):
                if i% clauses_per_page ==0 and i!=0 and full_document:
                    output.write("\n\\end{align}\\pagebreak")
                    output.write("\n\\begin{align}")
                    write_clause(clause, True,full_document)
                else:
                    write_clause(clause, i==0,full_document)

        output.write("\n\\end{align}")

        # document closing
        if full_document:
            output.write("\n\\end{document}")
  
        return output.getvalue()

    #
    # Various utility function for CNFs
    #
    def add_parity(self,variables, constant):
        """Output the CNF encoding of a parity constraint
        
        E.g. X1 + X2 + X3 = 1 (mod 2) is encoded as
        
        ( X1 v  X2 v  X3)
        (~X1 v ~X2 v  X3)
        (~X1 v  X2 v ~X3)
        ( X1 v ~X2 v ~X3)

        Parameters
        ----------
        variables : array-like
            variables involved in the constraint
        constant : {0,1}
            the constant of the linear equation

        Returns
        -------
        a list of clauses

        Examples
        --------
        >>> F=CNF()
        >>> F.add_parity(['a','b'],1)
        >>> list(F)
        [[(True, 'a'), (True, 'b')], [(False, 'a'), (False, 'b')]]
        >>> F=CNF()
        >>> F.add_parity(['a','b'],0)
        >>> list(F)
        [[(True, 'a'), (False, 'b')], [(False, 'a'), (True, 'b')]]
        >>> F=CNF()
        >>> F.add_parity(['a'],0)
        >>> list(F)
        [[(False, 'a')]]
        """
        literals = [(True,v) for v in variables]
        parity = xor(*self._check_and_compress_literals(literals),value=constant)
        self._constraints.append(parity)
        if self._length is not None:
            self._length += parity.n_clauses()
        

    def add_strictly_less_than(self,variables, threshold):
        """Clauses encoding a \"strictly less than\" constraint
     
        E.g. X1 + X2 + X3 + X4 < 3
     
        (~X1 v ~X2 v ~X3)
        (~X1 v ~X2 v ~X4)
        (~X1 v ~X3 v ~X4)
        (~X2 v ~X3 v ~X4)
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        threshold: int
           upper bound of the constraint
     
        Returns
        -------
            a list of clauses
     
        Examples
        --------
        >>> F=CNF()
        >>> F.add_strictly_less_than(['a','b','c'],2)
        >>> list(F)
        [[(False, 'a'), (False, 'b')], [(False, 'a'), (False, 'c')], [(False, 'b'), (False, 'c')]]
        >>> F=CNF()
        >>> F.add_strictly_less_than(['a'],1)
        >>> list(F)
        [[(False, 'a')]]
        >>> F=CNF()
        >>> F.add_strictly_less_than(['a','b','c'],-1)
        >>> list(F)
        [[]]
        >>> F=CNF()
        >>> F.add_strictly_less_than(['a','b','c'],10)
        >>> list(F)
        []
        """
        literals = [(True,v) for v in variables]
        ineq = less(*self._check_and_compress_literals(literals),threshold=threshold)
        self._constraints.append(ineq)
        if self._length is not None:
            self._length += ineq.n_clauses()


    def add_less_or_equal(self,variables, threshold):
        """Clauses encoding a \"less than or equal to\" constraint
     
        E.g. X1 + X2 + X3 + X4 <= 2
     
        (~X1 v ~X2 v ~X3)
        (~X1 v ~X2 v ~X4)
        (~X1 v ~X3 v ~X4)
        (~X2 v ~X3 v ~X4)
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        threshold: int
           upper bound of the constraint
     
        Returns
        -------
            a list of clauses
     
        Examples
        --------
        >>> S=CNF()
        >>> L=CNF()
        >>> S.add_strictly_less_than(['a','b','c'],3)
        >>> L.add_less_or_equal(['a','b','c'],2)
        >>> list(S) == list(L)
        True
        >>> F=CNF()
        >>> F.add_less_or_equal(['a','b','c'],1)
        >>> list(F)
        [[(False, 'a'), (False, 'b')], [(False, 'a'), (False, 'c')], [(False, 'b'), (False, 'c')]]
        >>> F=CNF()
        >>> F.add_less_or_equal(['a','b'],0)
        >>> list(F)
        [[(False, 'a')], [(False, 'b')]]
        >>> F=CNF()
        >>> F.add_less_or_equal(['a','b','c'],-1)
        >>> list(F)
        [[]]
        >>> F=CNF()
        >>> F.add_less_or_equal(['a','b','c'],10)
        >>> list(F)
        []
        """
        literals = [(True,v) for v in variables]
        ineq = leq(*self._check_and_compress_literals(literals),threshold=threshold)
        self._constraints.append(ineq)
        if self._length is not None:
            self._length += ineq.n_clauses()
    

    def add_strictly_greater_than(self, variables, threshold):
        """Clauses encoding a \"strictly greater than\" constraint
     
        E.g. X1 + X2 + X3 + X4 > 2
     
        (X1 v X2 v X3)
        (X1 v X2 v X4)
        (X1 v X3 v X4)
        (X2 v X3 v X4)
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        threshold: int
           lower bound of the constraint
     
        Returns
        -------
            a list of clauses
     
        Examples
        --------
        >>> F=CNF()
        >>> F.add_strictly_greater_than(['a','b','c'],2)
        >>> list(F)
        [[(True, 'a')], [(True, 'b')], [(True, 'c')]]
        >>> F=CNF()
        >>> F.add_strictly_greater_than(['a'],0)
        >>> list(F)
        [[(True, 'a')]]
        >>> F=CNF()
        >>> F.add_strictly_greater_than(['a','b','c'],-1)
        >>> list(F)
        []
        >>> F=CNF()
        >>> F.add_strictly_greater_than(['a','b','c'],3)
        >>> list(F)
        [[]]
        """
        literals = [(True,v) for v in variables]
        ineq = greater(*self._check_and_compress_literals(literals),threshold=threshold)
        self._constraints.append(ineq)
        if self._length is not None:
            self._length += ineq.n_clauses()
     

    def add_greater_or_equal(self, variables, threshold):
        """Clauses encoding a \"greater than or equal to\" constraint
     
        E.g. X1 + X2 + X3 + X4 > 1
     
        (X1 v X2 v X3)
        (X1 v X2 v X4)
        (X1 v X3 v X4)
        (X2 v X3 v X4)
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        threshold: int
           lower bound of the constraint
     
        Returns
        -------
            a list of clauses
     
        Examples
        --------
        >>> S=CNF()
        >>> L=CNF()
        >>> S.add_strictly_greater_than(['a','b','c'],1)
        >>> L.add_greater_or_equal(['a','b','c'],2)
        >>> list(L) == list(S)
        True
        >>> F=CNF()
        >>> F.add_greater_or_equal(['a','b','c'],3)
        >>> list(F)
        [[(True, 'a')], [(True, 'b')], [(True, 'c')]]
        >>> F=CNF()
        >>> F.add_greater_or_equal(['a'],0)
        >>> list(F)
        []
        >>> F=CNF()
        >>> F.add_greater_or_equal(['a','b','c'],4)
        >>> list(F)
        [[]]
        """
        literals = [(True,v) for v in variables]
        ineq = geq(*self._check_and_compress_literals(literals),threshold=threshold)
        self._constraints.append(ineq)
        if self._length is not None:
            self._length += ineq.n_clauses()


    def add_equal_to(self, variables, value):
        """Clauses encoding a \"equal to\" constraint
     
        E.g. X1 + X2 + X3 + X4 = 1
     
        (X1 v X2 v X3 v X4)
        (~X1 v ~X2)
        (~X1 v ~X3)
        (~X1 v ~X4)
        (~X2 v ~X3)
        (~X2 v ~X4)
        (~X3 v ~X4)
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        value: int
           target values
            a list of clauses
        """
        literals = [(True,v) for v in variables]
        equ = eq(*self._check_and_compress_literals(literals),value=value)
        self._constraints.append(equ)
        self._length += equ.n_clauses()

    def add_loose_majority(self, variables):
        """Clauses encoding a \"at least half\" constraint
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        """
        threshold = (len(variables)+1)//2
        self.add_greater_or_equal(variables, threshold)

    def add_loose_minority(self, variables):
        """Clauses encoding a \"at most half\" constraint
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        """
        threshold = len(variables)//2
        return self.add_less_or_equal(variables, threshold)
    

    def add_exactly_half_ceil(self, variables):
        """Clauses encoding a \"exactly half\" constraint (rounded up)
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        """
        threshold = (len(variables)+1)/2
        return self.add_equal_to(variables,threshold)
     
    def add_exactly_half_floor(self, variables):
        """Clauses encoding a \"exactly half\" constraint (rounded down)
     
        Parameters
        ----------
        variables : list of variables
           variables in the constraint
        """
        threshold = len(variables)/2
        return self.add_equal_to(variables,threshold)


    def add_linear(self, *args):
        """Add clauses encoding an integer linear constraint
     
        Integer linear constraints can be added as constraints
        to the formula, as a shortcut for an equivalent set of
        clauses. Consider for example

        .. math::

            x_1 + 2 x_2 + 4 x_3 \geq 3
        
        that can be encoded as clauses
     
        .. math::

            (\neg x_1  \lor x_2 \lor x_3) \wedge (x_1  \lor \neg x_2 \lor x_3) \wedge (x_1  \lor x_2 \lor x_3)

        This inequality can be added to a formula `F` using

        ::

            F.add_linear(1,"x_1",2,"x_2",4,"x_3",">=", 3)

        The arguments of :py:meth:`add_linear` are given as a sequence
        of integer and strings: the second to last element is one
        among `==`, `>=`, `<=`, `>`, `<` and determines the type of
        constraint, the last element determines the value to which the
        linear form is compared to. The preceding arguments must form
        an even length sequence in which the summands are represented
        by alternating the weight of each variable in the sum with
        its name.


        Examples
        --------
        >>> F = CNF()
        >>> F.add_linear(1,"x_1",2,"x_2",4,"x_3",">=", 7)
        >>> len(F)
        7
        >>> F = CNF()
        >>> F.add_linear(1,"x_1",2,"x_2",4,"x_3",">=", 0)
        >>> list(F)
        []
        >>> F = CNF()
        >>> F.add_linear(1,"x_1",2,"x_2",4,"x_3","==", 5)
        >>> len(F)
        7
        >>> F = CNF()
        >>> F.add_linear(1,"x_1",2,"x_2",4,"x_3",">", 0)
        >>> len(F)
        1
        
        Parameters
        ----------
        *args : sequence of int and strings
            See above.

        """
        if len(args)<2:
            raise ValueError("Linear constraints require at least 2 args: comparison operator and value.")
        variables = [(True,v) for v in args[1:-2:2]]
        weights   = args[ :-2:2]
        value     = args[-1]
        op        = args[-2]

        variables = self._check_and_compress_literals(variables)
        cnst=None
        
        if op == '==':

            cnst = weighted_eq(*zip(weights,variables),value=value)

        elif op == '>=':

            cnst = weighted_geq(*zip(weights,variables),threshold=value)

        elif op == '>':

            cnst = weighted_geq(*zip(weights,variables),threshold=value+1)

        elif op == '<=':

            cnst = weighted_geq(*zip((-w for w in weights),variables),threshold= - value)

        elif op == '<':

            cnst = weighted_geq(*zip((-w for w in weights),variables),threshold= - value + 1)

        else:
            raise ValueError("Comparison operator must be among ==, >=, <=, >, <.")
        
        self._constraints.append(cnst)
        # Too expensive to count the number of generated clause. Invalidate the estimate.
        self._length = None

    
class unary_mapping(object):
    """Unary CNF representation of a mapping between two sets."""

    Domain = None
    Range  = None

    Pattern = None

    Complete      = False
    Functional    = False
    Surjective    = False
    Injective     = False

    NonDecreasing = False

    @staticmethod
    def var_name(i,b):
        return "X_{{{0},{1}}}".format(i,b)

    def __init__(self, D, R,**kwargs):
        r"""Generator for the clauses of a mapping between to sets

        This generates of the constraints on variables :math:`v(i,j)`
        where :math:`i \in D` and :math:`j in R`, so that they
        represent a mapping (or a relation) between the two sets,
        expressed in unary (i.e. :math:`v(i,j)` expresses whether
        :math:`i` is mapped to :math:`j` or not).

        Parameters
        ----------
        D : iterable
            the domain of the mapping

        R : iterable
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
        self.Domain = list(D)
        self.Range  = list(R)

        # optional parameters of the mapping
        self.Complete      = kwargs.pop('complete',  True)
        self.Functional    = kwargs.pop('functional',False)
        self.Surjective    = kwargs.pop('surjective',False)
        self.Injective     = kwargs.pop('injective', False)

        self.NonDecreasing = kwargs.pop('nondecreasing', False)

        # variable name scheme 
        self.var_name = kwargs.pop('var_name', self.var_name)

        # use a bipartite graph scheme for the mapping?
        self.Pattern  = kwargs.pop('sparsity_pattern', None)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        self.DomainToVertex={}
        self.VertexToDomain={}
        self.RangeToVertex={}
        self.VertexToRange={}

        self.RankRange  = {}
        self.RankDomain = {}

        if self.Pattern is not None:

            gL,gR = bipartite_sets(self.Pattern)

            if len(gL) != len(self.Domain):
                raise ValueError("Domain and the left side of the pattern differ in size")

            if len(gR) != len(self.Range):
                raise ValueError("Range and the right side of the pattern differ in size")
        else:
            gL = self.Domain
            gR = self.Range

        for (d,v) in zip(self.Domain,gL):
            self.DomainToVertex[d]=v
            self.VertexToDomain[v]=d

        for (r,v) in zip(self.Range,gR):
            self.RangeToVertex[r]=v
            self.VertexToRange[v]=r

        for i,d in enumerate(self.Domain,start=1):
            self.RankDomain[d]=i

        for i,r in enumerate(self.Range,start=1):
            self.RankRange[r]=i


    def domain(self):
        return self.Domain

    def range(self):
        return self.Range

    def images(self,d):
        if self.Pattern is None:
            return self.Range
        else:
            v = self.DomainToVertex[d]
            return [ self.VertexToRange[u] for u in neighbors(self.Pattern,v) ]

    def counterimages(self,r):
        if self.Pattern is None:
            return self.Domain
        else:
            v = self.RangeToVertex[r]
            return [ self.VertexToDomain[u] for u in neighbors(self.Pattern,v) ]

    def variables(self):
        for d in self.Domain:
            for r in self.images(d):
                yield self.var_name(d,r)

    def load_variables_to_formula(self,F):
        """Loads the variables of the mapping into a CNF formula"""
        for v in self.variables():
            F.add_variable(v)

    def load_clauses_to_formula(self,F):
        """Loads the clauses of the mapping into a CNF formula"""
        # Completeness axioms
        if self.Complete:
            for d in self.Domain:
                F.add_greater_or_equal([self.var_name(d,r) for r in self.images(d)], 1)

        # Surjectivity axioms
        if self.Surjective:
            for r in self.Range:
                F.add_greater_or_equal([self.var_name(d,r) for d in self.counterimages(r)], 1)

        # Injectivity axioms
        if self.Injective:
            for r in self.Range:
                F.add_less_or_equal([self.var_name(d,r)  for d in self.counterimages(r)],1)

        # Functionality axioms
        if self.Functional:
            for d in self.Domain:
                F.add_less_or_equal([self.var_name(d,r) for r in self.images(d)],1)

        # Mapping is monotone non-decreasing
        if self.NonDecreasing:

            for (a,b) in combinations(self.Domain,2):
                for (i,j) in product(self.images(a),self.images(b)):

                    if self.RankRange[i] > self.RankRange[j]:
                        F.add_clause([(False,self.var_name(a,i)),(False,self.var_name(b,j))])

    def clauses(self):
        temp = CNF()
        temp.mode_unchecked()
        self.load_variables_to_formula(temp)
        self.load_clauses_to_formula(temp)
        for c in temp:
            yield c


class binary_mapping(object):
    """Binary CNF representation of a mapping between two sets."""

    Domain = None
    Range  = None
    Bits   = None

    Injective     = False
    NonDecreasing = False

    @staticmethod
    def var_name(i,b):
        return "Y_{{{0},{1}}}".format(i,b)


    def variables(self):
        for v,b in product(self.Domain,xrange(0,self.Bits)):
            yield self.var_name(v,b)

    def load_variables_to_formula(self,F):
        """Loads the variables of the mapping into a CNF formula"""
        for v in self.variables():
            F.add_variable(v)


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
        self.Range  = list(R)
        self.Bits   = int(ceil(log(len(R),2)))

        # optional parameters of the mapping
        self.Injective     = kwargs.pop('injective', False)
        self.NonDecreasing = kwargs.pop('nondecreasing', False)
        # variable name scheme 
        self.var_name = kwargs.pop('var_name', self.var_name)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        self.ImageToBits={}
        self.BitsToImage={}

        for i,bs in islice(enumerate(product([0,1],repeat=self.Bits)),
                           len(self.Range)):

            self.ImageToBits[ self.Range[i] ] = bs
            self.BitsToImage[ bs ] = self.Range[i]

    def image_to_bitstring(self,im):
        return self.ImageToBits[im]

    def bitstring_to_image(self,bs):
        return self.BitsToImage[bs]

    def forbid_bitstring(self, i, bs):
        """Generates a clause that exclude 'i -> bs' mapping """
        return [ ( bs[b]==0, self.var_name(i,self.Bits-1-b))
                 for b in xrange(self.Bits) ] 

    def forbid_image(self, i, j):
        """Generates a clause that exclude 'i -> j' mapping """
        return self.forbid_bitstring(i,self.ImageToBits[j])

    def clauses(self):

        # Avoid strings that do not correspond to elements from the range
        for i,bs in product(self.Domain,
                            islice(product([0,1],repeat=self.Bits),len(self.Range),None)):
             self.forbid_bitstring(i,bs) 

        # Injectivity
        if self.Injective:
            for j in self.Range:
                for i1,i2 in combinations(self.Domain,2):
                    yield self.forbid_image(i1,j) + self.forbid_image(i2,j)

        # Enforce Non Decreasing Mapping 
        if self.NonDecreasing:
            pairs_of_maps = product(combinations(self.Domain,2),
                                    combinations(self.Range,2))

            for (i1,i2),(j1,j2) in pairs_of_maps:
                yield self.forbid_image(i1,j2) + self.forbid_image(i2,j1)

    def load_clauses_to_formula(self,F):
        for c in self.clauses():
            F.add_clause(c)


class disj(tuple):
    __slots__ = ()

    def __new__(cls,*args):
        """Clause constraint

        Internal representation of a disjunction of a set of literals.
        For example the encoding of

        .. math::

            x_1 \vee \\neg x_3 \vee x_7

        is 

        ::

            disj(1,-3,7)

        Parameters
        ----------
        *args : zero or more ints
            literals in the clause
        """
        self = super(disj,cls).__new__(cls,args)
        return self

    def __repr__(self):
        return "{}({})".format("disj",
                               ", ".join(str(i) for i in self))

    def __str__(self):
        literals = [ "{}{}".format("" if l>0 else "¬",abs(l)) for l in self ]
        return " ∨ ".join(literals)
    

    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        return 1

    def clauses(self):
        """Clauses to represent the constraint"""
        yield self
                    
class xor(tuple):

    def __new__(cls,*args,**kw):
        """Parity constraint
            
        Internal representation of a parity constraint over a set of
        literals. In particular the constraint claims that the boolean
        values of the sequence of literals (contained in the field
        `literals`) must sum to a number which is equal to the field
        `value`, module 2.

        For example the encoding of 

        .. math::

            x_1 \\oplus \\neg x_3 \\oplus x_7 = 1 \\pmod{2}

        is 

        ::
        
            xor(1,-3,7, value = 1)

        Parameters
        ----------
        *args : zero or more int
            literals in the sum

        value : integer
            the value of the parity

        """
        if "value" not in kw:
            raise TypeError("XOR constraints must have \'value\' keyword argument")
        self = super(xor,cls).__new__(cls,args)
        self.value = kw['value'] % 2
        return self

    def __eq__(self,other):
        return self.value == other.value and super(xor,self).__eq__(other)

    def __repr__(self):
        return "{}({}, value={})".format("xor",
                                         ", ".join(str(i) for i in self),
                                         self.value)

    def __str__(self):
        literals = [ "{}{}".format("" if l>0 else "¬",abs(l)) for l in self ]
        return "{} {} {} (mod 2)".format(" ⊕ ".join(literals),"==",self.value)
    
    def n_clauses(self):
        """Number of clauses to represent a XOR"""

        # Parity of an empty sequence
        if len(self)==0:
            return self.value % 2

        # Parity of a non emtpy sequence
        return 2**(len(self)-1)

    def clauses(self):
        """Clauses to represent the constraint"""
        
        value = (self.value + len([lit for lit in self if lit < 0])) % 2
        domains = tuple([(abs(lit),-abs(lit)) for lit in self])
        for c in product(*domains):
            # Save only the clauses with the right polarity
            parity = len([lit for lit in c if lit < 0]) % 2
            if parity != value:
                yield disj(*c)

        
    
    
class less(tuple):

    def __new__(cls,*args,**kw):
        """Less-than constraint

        Represent a 'less than' constraint over a set of literals.
        In particular the constraint claims that the boolean values of the
        sequence of literals (contained in the field `literals`) must sum
        to a number which is strictly less than the field `threshold`.

        For example the encoding of 

        .. math::

             x_2 + \\neg x_3 + x_7 < 2

        is 

        ::

             less(2,-3,7,value=2)

        Repeated or opposite literals are forbidden. In case one of these
        things occur the `n_clauses` and `clauses` methods have
        undefined behavior.

        Parameters
        ----------
        *args : zero or more int
            literals in the sum

        threshold : integer
           the threshold value

        """
        if "threshold" not in kw:
            raise TypeError("LESS THAN constraints must have \'threshold\' keyword argument")
        self = super(less,cls).__new__(cls,args)
        self.threshold = kw['threshold']
        return self

    def __eq__(self,other):
        return self.threshold == other.threshold and super(less,self).__eq__(other)

    def __repr__(self):
        return "{}({}, threshold={})".format("less",
                                             ", ".join(str(i) for i in self),
                                             self.threshold)

    def __str__(self):
        literals = [ "{}{}".format("" if l>0 else "¬",abs(l)) for l in self ]
        return "({}) {} {}".format(" + ".join(literals),"<",self.threshold)
    
    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        if self.threshold > len(self):
            return 0
        elif self.threshold <= 0:
            return 1

        def binom(n,k):
            return factorial(n) // factorial(k) // factorial(n - k)
                
        return binom(len(self),self.threshold)

    def clauses(self):
        """Clauses to represent the constraint"""
        if self.threshold > len(self):
            return
        elif self.threshold < 0:
            yield disj()
            return

        for cls in combinations([-l for l in self], self.threshold):
            yield disj(*cls)

class leq(tuple):

    def __new__(cls,*args,**kw):
        """Less-than-or-equal-to constraint

        Represent a 'less than or equal to' constraint over a set of
        literals. In particular the constraint claims that the boolean
        values of the sequence of literals (contained in the field
        `literals`) must sum to a number which less than or equal to the
        field `threshold`.

        For example the encoding of 

        .. math::

             x_2 + \\neg x_3 + \\neq x_4 + x_7 \leq 2

        is 

        ::

             leq(2,-3,-4,7,value=2)

        If there are repeated or opposite literals, then the constraint
        could make no sense. In particular `n_clauses` and `clauses`
        method have undefined behavior.

        Parameters
        ----------
        *args : zero or more int
            literals in the sum

        threshold : integer
           the threshold value

        """
        if "threshold" not in kw:
            raise TypeError("LESS OR EQUAL constraints must have \'threshold\' keyword argument")
        self = super(leq,cls).__new__(cls,args)
        self.threshold = kw['threshold']
        return self

    def __eq__(self,other):
        return self.threshold == other.threshold and super(leq,self).__eq__(other)

    def __repr__(self):
        return "{}({}, threshold={})".format("leq",
                                             ", ".join(str(i) for i in self),
                                             self.threshold)

    def __str__(self):
        literals = [ "{}{}".format("" if l>0 else "¬",abs(l)) for l in self ]
        return "{} {} {}".format(" + ".join(literals),"<=",self.threshold)
    
        
    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        return less(*self,threshold=self.threshold+1).n_clauses()

    def clauses(self):
        """Clauses to represent the constraint"""
        return less(*self,threshold=self.threshold+1).clauses()


class greater(tuple):
    
    def __new__(cls,*args,**kw):
        """Greater-than constraint

        Represent a 'greater than' constraint over a set of literals.
        In particular the constraint claims that the boolean values of the
        sequence of literals (contained in the field `literals`) must sum
        to a number which greater than the field `threshold`.

        For example the encoding of 

        .. math::

             x_2 + \\neg x_3 + \\neq x_4 + x_7 > 2

        is 

        ::

             greater(2,-3,-4,7,value=2)

        If there are repeated or opposite literals, then the constraint
        could make no sense. In particular `n_clauses` and `clauses`
        method have undefined behavior.

        Parameters
        ----------
        *args : zero or more int
            literals in the sum

        threshold : integer
           the threshold value

        """
        if "threshold" not in kw:
            raise TypeError("GREATER THAN constraints must have \'threshold\' keyword argument")
        self = super(greater,cls).__new__(cls,args)
        self.threshold = kw['threshold']
        return self

    def __eq__(self,other):
        return self.threshold == other.threshold and super(greater,self).__eq__(other)

    def __repr__(self):
        return "{}({}, threshold={})".format("greater",
                                             ", ".join(str(i) for i in self),
                                             self.threshold)

    def __str__(self):
        literals = [ "{}{}".format("" if l>0 else "¬",abs(l)) for l in self ]
        return "{} {} {}".format(" + ".join(literals),">",self.threshold)
        
    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        if self.threshold >= len(self):
            return 1
        elif self.threshold < 0:
            return 0

        def binom(n,k):
            return factorial(n) // factorial(k) // factorial(n - k)

        # logically it should be binom(LEN,LEN-THR)
        return binom(len(self),self.threshold)

    def clauses(self):
        """Clauses to represent the constraint"""
        if self.threshold >= len(self):
            yield disj()
            return
        elif self.threshold < 0:
            return

        for cls in combinations(self, len(self)-self.threshold):
            yield disj(*cls)


class geq(tuple):
    def __new__(cls,*args,**kw):
        """Greater-than-or-equal-to constraint

        Represent a 'greater than or equal to' constraint over a set of
        literals. In particular the constraint claims that the boolean
        values of the sequence of literals (contained in the field
        `literals`) must sum to a number which greater than or equal to the
        field `threshold`.

        For example the encoding of 

        .. math::

             x_2 + \\neg x_3 + \\neq x_4 + x_7 \geq 2

        is 

        ::

             geq(2,-3,-4,7,value=2)

        If there are repeated or opposite literals, then the constraint
        could make no sense. In particular `n_clauses` and `clauses`
        method have undefined behavior.

        Parameters
        ----------
        *args : zero or more int
            literals in the sum

        threshold : integer
           the threshold value

        """
        if "threshold" not in kw:
            raise TypeError("GREATER OR EQUAL constraints must have \'threshold\' keyword argument")
        self = super(geq,cls).__new__(cls,args)
        self.threshold = kw['threshold']
        return self

    def __eq__(self,other):
        return self.threshold == other.threshold and super(geq,self).__eq__(other)

    def __repr__(self):
        return "{}({}, threshold={})".format("geq",
                                             ", ".join(str(i) for i in self),
                                             self.threshold)

    def __str__(self):
        literals = [ "{}{}".format("" if l>0 else "¬",abs(l)) for l in self ]
        return "{} {} {}".format(" + ".join(literals),">=",self.threshold)
    
    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        return greater(*self,threshold=self.threshold-1).n_clauses()

    def clauses(self):
        """Clauses to represent the constraint"""
        return greater(*self,threshold=self.threshold-1).clauses()

class eq(tuple):
    def __new__(cls,*args,**kw):
        """Equal-to constraint

        Represent an 'equal to' constraint over a set of literals.
        In particular the constraint claims that the boolean values of the
        sequence of literals (contained in the field `literals`) must sum
        to a number which equal to the field `value`.

        For example the encoding of 

        .. math::

             x_2 + \\neg x_3 + \\neq x_4 + x_7 = 2

        is 

        ::

             eq(2,-3,-4,7, value=2)

        If there are repeated or opposite literals, then the constraint
        could make no sense. In particular `n_clauses` and `clauses`
        method have undefined behavior.

        Parameters
        ----------
        *args : zero or more int
            literals in the sum

        value : integer
           expected value of the sum

        """
        if "value" not in kw:
            raise TypeError("EQUAL TO constraints must have \'value\' keyword argument")
        self = super(eq,cls).__new__(cls,args)
        self.value = kw['value']
        return self

    def __eq__(self,other):
        return self.value == other.value and super(eq,self).__eq__(other)

    def __repr__(self):
        return "{}({}, value={})".format("eq",
                                         ", ".join(str(i) for i in self),
                                         self.value)

    def __str__(self):
        literals = [ "{}{}".format("" if l>0 else "¬",abs(l)) for l in self ]
        return "{} {} {}".format(" + ".join(literals),"==",self.value)
    
    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        return leq(*self,threshold=self.value).n_clauses() \
               + \
               geq(*self,threshold=self.value).n_clauses()

    def clauses(self):
        """Clauses to represent the constraint"""
        for c in leq(*self,threshold=self.value).clauses():
            yield c
        for c in geq(*self,threshold=self.value).clauses():
            yield c


class weighted_eq(tuple):
    def __new__(cls,*args,**kw):
        """Linear equation constraint

        Represent a general linear equation constraint. It is
        different for :py:class:`eq` because the constraint can have
        arbitrary integer weights on the variables but it is expressed
        in term of positive literals only.

        The object is a tuple of (weight,variable index) pairs, and
        the field :py:attr:`value` is an integer.

        The constraint claims that the boolean values, multiplied by
        their respective weights, of the sequence of literals
        (contained in the field `literals`) must sum to a number which
        equal to the field :py:attr:`value`.

        For example the encoding of 

        .. math::

             3 x_1 + 4 x_3 - 2 x_5 - x_7 = 0

        is

        ::

             weighted_eq((3,1),(4,3),(-2,5),(-1,7),value=0)

        Variable identifiers are expected to be positive.

        Parameters
        ----------
        *args : zero or more (int,positive int) pairs
            weighted sum of variables

        value : integer
           expected value of the sum

        """
        if "value" not in kw:
            raise TypeError("WEIGHTED EQUALITY constraints must have \'value\' keyword argument")
        self = super(weighted_eq,cls).__new__(cls,args)
        self.value = kw['value']
        return self

    def __eq__(self,other):
        return self.value == other.value and super(weighted_eq,self).__eq__(other)

    def __repr__(self):
        return "{}({}, value={})".format("weighted_eq",
                                         ", ".join(str(i) for i in self),
                                         self.value)

    def __str__(self):
        terms = [ "{}*{}".format(w,v) for w,v in self ]
        return "{} {} {}".format(" + ".join(terms),"==",self.value)
    
    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        return sum(1 for _ in self.clauses())
        
    def clauses(self):
        """Clauses to represent the constraint"""

        
        domains = tuple([((w,v),(0,-v)) for w,v in self])

        for summands in product(*domains):
            if sum(w for w,_ in summands) != self.value:
                yield disj(*(-v for _,v in summands))
        
class weighted_geq(tuple):
    def __new__(cls,*args,**kw):
        """Linear inequality constraint (greater than or equal to)

        Represent a general linear inequality constraint. It is
        different for :py:class:`geq` because the constraint can have
        arbitrary integer weights on the variables but it is expressed
        in term of positive literals only.

        The object is a tuple of (weight,variable index) pairs, and
        the field :py:attr:`threshold` is an integer.

        The constraint claims that the boolean values, multiplied by
        their respective weights, of the sequence of literals
        (contained in the field `literals`) must sum to a number which
        greater than or equal to the field :py:attr:`threshold`.

        For example the encoding of 

        .. math::

             3 x_1 + 4 x_3 - 2 x_5 - x_7 \geq 0

        is

        ::

             weighted_geq((3,1),(4,3),(-2,5),(-1,7),value=0)

        Variable identifiers are expected to be positive.

        Parameters
        ----------
        *args : zero or more (int,positive int) pairs
            weighted sum of variables

        threshold : integer
           expected lower bound of the sum

        """
        if "threshold" not in kw:
            raise TypeError("WEIGHTED GREATER OR EQUAL constraints must have \'threshold\' keyword argument")
        self = super(weighted_geq,cls).__new__(cls,args)
        self.threshold = kw['threshold']
        return self

    def __eq__(self,other):
        return self.threshold == other.threshold and super(weighted_geq,self).__eq__(other)

    def __repr__(self):
        return "{}({}, value={})".format("weighted_geq",
                                         ", ".join(str(i) for i in self),
                                         self.threshold)

    def __str__(self):
        terms = [ "{}*{}".format(w,v) for w,v in self ]
        return "{} {} {}".format(" + ".join(terms),">=",self.threshold)

    def n_clauses(self):
        """Number of clauses to represent the constraints"""
        return sum(1 for _ in self.clauses())
        
    def clauses(self):
        """Clauses to represent the constraint"""

        
        domains = tuple([((w,v),(0,-v)) for w,v in self])

        for summands in product(*domains):
            if sum(w for w,_ in summands) < self.threshold:
                yield disj(*(-v for _,v in summands))
        
