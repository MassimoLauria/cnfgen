#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
from itertools import product

__docstring__ =\
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git


Create you own CNFs:

>>> c=CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], \
          [(False,"x2"),(True,"x4")] ])
>>> print( c.dimacs(False) )
p cnf 4 2
1 2 -3 0
-2 4 0

You can add clauses later in the process:

>>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
>>> print( c.dimacs(add_header=False))
p cnf 5 3
1 2 -3 0
-2 4 0
-3 4 -5 0

"""

_default_header=r"""Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""


## implementation of lookahead iterator
class _ClosedIterator:
    def __init__(self, iter,endToken=None):
        self.iter = iter
        self.endToken = endToken

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.iter.next()
        except StopIteration:
            return self.endToken

###
### Basic CNF class
###

class CNF(object):
    """Propositional formulas in conjunctive normal form.

    A CNF  formula is a  sequence of  clauses, which are  sequences of
    literals. Each literal is either a variable or its negation.

    Use `add_variable` method to add a variable to the formula. Two
    variable with the same name are considered the same variable, add
    successive additions do not have any effect.

    Use `add_clause` to add new clauses to CNF. Clauses will be added
    multiple times in case of multiple insertion of the same clauses.

    For  documentation purpose  it  is possible  use `add_comment`  to
    interleave  clauses   with  documentation  text,  which   will  be
    *optionally* exported to LaTeX or dimacs.  Note that strict dimacs
    format   do   not   allow   comments   except   for   an   initial
    header.  Nevertheless  most of  SAT  solver  allows such  comments
    anyway.

    Implementation:  for  efficiency reason  clauses and  variable can
    only be added,  and not deleted. Furthermore order  matters in the
    representation.
    """

    def __init__(self, clauses_and_comments=None, header=None):
        """Propositional formulas in conjunctive normal form.

        Arguments:
        - `clauses_and_comments`: ordered list of clauses or comments;
                            a clause with k literals list containing k
                            pairs, each representing a literal (see
                            `add_clause`).  First element is the
                            polarity and the second is the variable,
                            which must be an hashable object. A
                            comment is just a string of text (see
                            `add_comment`)

                     E.g. (not x3) or x4 or (not x2) is encoded as
                     [(False,"x3"),(True,"x4"),False,"x2")]

        - `header`: a preamble which documents the formula
        """

        self._header = header if header!=None else _default_header

        # Initial empty formula
        self._clauses         = []
        self._comments        = []

        # Variable indexes <--> Variable names correspondence
        # first variable is indexed with 1.
        self._index2name      = [None]
        self._name2index      = dict()

        # Internal coherence can be disrupted by some methods.  API
        # methods require it to be rechecked.
        self._coherent        = True

        # Load the initial data into the CNF
        for c in (clauses_and_comments or []):
            self.add_clause_or_comment(c)


    # Formula contains an header property
    def _set_header(self, value):
        self._header = value

    def _get_header(self):
        return self._header

    header = property(_get_header, _set_header)

    #
    # Implementation of some standard methods
    #

    def __iter__(self):
        """Iterates over all clauses of the CNF

        Iterator over all clauses, ignoring the interleaving comments.
        """
        for c in self._clauses:
            assert self._coherent
            yield self._uncompress_clause(c)

    def __str__(self):
        """String representation of the formula
        """
        assert self._coherent
        return self._header

    def __len__(self):
        """Number of clauses in the formula
        """
        return len(self._clauses)


    #
    # Internal implementation methods, use at your own risk!
    #

    def _uncompress_clause(self, clause):
        """(INTERNAL USE) Uncompress a clause for the numeric representation.

        Arguments:
        - `clause`: clause to be uncompressed

        >>> c=CNF()
        >>> c.add_clause([(True,"x"),(False,"y")])
        >>> print(c._uncompress_clause([-1,-2]))
        [(False, 'x'), (False, 'y')]
        """
        return [ (l>0, self._index2name[abs(l)]) for l in clause ]

    def _compress_clause(self, clause):
        """(INTERNAL USE) Compress a clause to the numeric representation.

        Arguments:
        - `clause`: clause to be compressed

        >>> c=CNF()
        >>> c.add_clause([(True,"x"),(False,"y")])
        >>> print(c._compress_clause([(False, 'x'), (False, 'y')]))
        (-1, -2)
        """
        return tuple( (1 if p else -1) * self._name2index[n] for p,n in clause)


    def _add_compressed_clauses(self, clauses):
        """(INTERNAL USE) Add to the CNF a list of compressed clauses.

        This method uses the internal compressed clause representation
        to add a large batch of data  into the CNF.  It does not check
        for internal  coherence conditions,  and it  does not  need to
        convert between  internal and external  clause representation,
        so it  is very fast.   When assertions  are tested, a  call to
        this method will  disable the standard API, since  the CNF can
        be in an inconsistent state.

        Whenever the high level API is used with an inconsisten state
        the code will fail some assertion.

        In particular it does not check if the indexes correspond to a
        variable in the formula.

        To test consistency and re-enable the API, please call method
        `CNF._check_coherence`.

        Arguments:
        - `clauses`: a sequence of compressed clauses.

        >>> c=CNF()

        We add the variables in advance, so that the internal status
        stays coherent.

        >>> c.add_variable("x")
        >>> c.add_variable("y")
        >>> c.add_variable("z")

        When we add some compressed clauses, we need to test the
        internal status of the object. If the test is positive, then
        the high level API is available again.

        >>> c._add_compressed_clauses([[-1,2,3],[-2,1],[1,-3]])
        >>> c._check_coherence()
        True
        >>> print(c.dimacs(add_header=False,add_comments=False))
        p cnf 3 3
        -1 2 3 0
        -2 1 0
        1 -3 0

        If we call the internal API several times, we need to test the
        object only once.

        >>> c._add_compressed_clauses([[-2,-3]])
        >>> c._add_compressed_clauses([[-1, 2]])
        >>> c._check_coherence()
        True
        >>> print(c.dimacs(add_header=False,add_comments=False))
        p cnf 3 5
        -1 2 3 0
        -2 1 0
        1 -3 0
        -2 -3 0
        -1 2 0
        """
        self._coherent = False
        self._clauses.extend(tuple(c) for c in clauses)


    def _check_coherence(self, force=False):
        """Check if the formula is internally consistent.

        Certain fast manipulation methods are not safe if used
        incorrectly, so the CNF object may be corrupted. This method
        tests if that was not the case.

        Arguments:
        - `force`: force check even if the formula claims coherence

        >>> c=CNF()
        >>> c.add_variable("x")
        >>> c.add_variable("y")

        We add clauses mentioning three variables, and the formula is
        not coherent.

        >>> c._add_compressed_clauses([(-1,2),(1,-2),(1,3)])
        >>> c._check_coherence()
        False

        We cannot use the API now

        >>> c.clauses()
        Traceback (most recent call last):
        AssertionError
        """
        if not force and self._coherent: return True

        varindex=self._name2index
        varnames=self._index2name

        # number of variables and clauses
        N=len(varindex.keys())
        M=len(self._clauses)


        # Consistency in the variable dictionary
        if N != len(varnames)-1:      return False
        for i in range(1,N+1):
            if varindex[varnames[i]]!=i: return False


        # Count clauses and check literal representation
        for clause in self._clauses:
            for literal in clause:
                if not 0 < abs(literal) <= N: return False

        # Check that comments refer to actual clauses (or one more)
        oldpos=0
        for pos,text in self._comments:
            if not oldpos <= pos <= M: return False
            oldpos = pos

        # formula passed all tests
        self._coherent = True
        return True

    #
    # High level API: build the CNF
    #

    def add_clause(self,clause):
        """Add a clause to the CNF.

        The clause must be well formatted. Otherwise it raises
        `TypeError` if the clause is not well formatted.

        E.g. (not x3) or x4 or (not x2) is encoded as
             [(False,u"x3"),(True,u"x4"),(False,u"x2")]

        All variable mentioned in the clause will be added to the list
        of variables  of the CNF,  in the  order of appearance  in the
        clauses.

        Arguments:
        - `clause`: a clause with k literals is a list with k pairs.
                    First coords are the polarities, second coords are
                    utf8 encoded strings with variable names.
        """
        assert self._coherent

        # A clause must be an immutable object
        try:
            hash(tuple(clause))
        except TypeError:
            raise TypeError("%s is not a well formatted clause" %clause)

        # Add all missing variables
        try:
            for _,var in clause:
                self.add_variable(var)
        except TypeError:
            raise TypeError("%s is not a well formatted clause" %clause)

        # Add the compressed clause
        self._clauses.append( self._compress_clause(clause) )


    def add_variable(self,var):
        """Add a variable to the formula (if not already resent).

        The variable must be `hashable`. I.e. it must be usable as key
        in a dictionary.  It raises `TypeError` if the variable cannot
        be hashed.

        Arguments:
        - `var`: the variable to add.
        """
        assert self._coherent
        try:
            if not var in self._name2index:
                # name correpsond to the last variable so far
                self._index2name.append(var)
                self._name2index[var] = len(self._index2name)-1
        except TypeError:
            raise TypeError("%s is not a legal variable name" %var)

    def add_comment(self,comment):
        """Add a comment to the formula.

        This is useful for documenting cnfs in DIMACS format which may
        be quite cryptic.  Notice that you have the option to
        intersperse comments among the clauses, but that may not be
        supported by your SAT solver. Anyway comments can be removed
        from you Dimacs/LaTeX output.

        Arguments:
        - `comment`: an unicode string of text.

        >>> c=CNF()
        >>> c.add_comment("First clause")
        >>> c.add_clause([(True,"x"),(False,"y")])
        >>> c.add_comment("Second clause")
        >>> c.add_clause([(True,"y"),(False,"z")])
        >>> print( c.dimacs(False,True) )
        p cnf 3 2
        c First clause
        1 -2 0
        c Second clause
        2 -3 0
        >>> print(c.dimacs(add_header=False,add_comments=False))
        p cnf 3 2
        1 -2 0
        2 -3 0
        """
        self._comments.append((len(self),comment[:]))

    def add_clause_or_comment(self, data):
        """Add a clause or a comment to the formula

        Call either `add_comment` or `add_clause`, depending on the
        type of the input value. If it is a string then it is a
        comment.

        Arguments:
        - `data`: either a clause or a comment.

        >>> c=CNF()
        >>> data=["Hej",[(False,"x"),(True,"y")],"Hej da"]
        >>> for d in data: c.add_clause_or_comment(d)
        >>> print(c.dimacs(add_header=False,add_comments=True))
        p cnf 2 1
        c Hej
        -1 2 0
        c Hej da
        """
        assert self._coherent
        if isinstance(data,basestring):
            self.add_comment(data)
        else:
            self.add_clause(data)

    #
    # High level API: read the CNF
    #

    def variables(self):
        """Returns (a copy of) the list of variable names.
        """
        assert self._coherent
        vars=iter(self._index2name)
        vars.next()
        return vars

    def clauses(self):
        """Return the list of clauses
        """
        assert self._coherent
        return self.__iter__()

    #
    #  Export to useful output format
    #

    def dimacs(self,add_header=True,add_comments=False):
        """Produce the dimacs encoding of the formula

        >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")],\
                   [(False,"x_2"),(False,"x_4")], \
                   [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
        >>> print(c.dimacs())
        c Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
        c https://github.com/MassimoLauria/cnfgen.git
        c
        p cnf 4 3
        -1 2 -3 0
        -2 -4 0
        2 3 -4 0

        The empty formula

        >>> c=CNF()
        >>> print(c.dimacs(add_header=False))
        p cnf 0 0
        """
        assert self._coherent

        from cStringIO import StringIO
        output = StringIO()

        # Count the number of variables and clauses
        n = len(self._index2name)-1
        m = len(self)

        # A nice header
        if add_header:
            for s in self.header.split("\n"): output.write( ("c "+s).rstrip()+"\n")

        # Formula specification
        output.write( "p cnf {0} {1}".format(n,m) )

        # No comments
        if not add_comments:
            for c in self._clauses:
                output.write("\n" +  " ".join([str(l) for l in c])  + " 0")
            return output.getvalue()


        # with comments
        assert add_comments
        clauseidx=_ClosedIterator(enumerate(self._clauses),(m+1,None))
        comments =_ClosedIterator(iter(self._comments),(m+1,None))

        index_clause,clause   = clauseidx.next()
        index_comment,comment = comments.next()

        while True:

            if index_clause==index_comment==m+1: break

            if index_comment <= index_clause:
                for s in comment.split("\n"): output.write( ("\nc "+s).rstrip())
                index_comment,comment = comments.next()
            else:
                output.write("\n" +  " ".join([str(l) for l in clause])  + " 0")
                index_clause,clause   = clauseidx.next()

        # final formula
        return output.getvalue()

    def latex(self,add_header=True,add_comments=True):
        """Produce the LaTeX version of the formula

        >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")],\
                   [(False,"x_2"),(False,"x_4")], \
                   [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
        >>> print(c.latex())
        % Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
        % https://github.com/MassimoLauria/cnfgen.git
        %
        \\ensuremath{%
              \\left( \\neg{x_1} \\lor     {x_2} \\lor \\neg{x_3} \\right)
        \\land \\left( \\neg{x_2} \\lor \\neg{x_4} \\right)
        \\land \\left(     {x_2} \\lor     {x_3} \\lor \\neg{x_4} \\right) }
        >>> c=CNF()
        >>> print(c.latex(add_header=False))
        \\ensuremath{%
           \\top }

        """
        assert self._coherent

        from cStringIO import StringIO
        output = StringIO()

        # A nice header
        if add_header:
            for s in self.header.split("\n"): output.write( ("% "+s).rstrip()+"\n" )

        # map literals to latex formulas
        def map_literals(l):
            if l>0 :
                return  "    {"+self._index2name[ l]+"}"
            else:
                return "\\neg{"+self._index2name[-l]+"}"


       # We produce clauses and comments
        output.write( "\\ensuremath{%" )
        empty_cnf=True

        # format clause
        def write_clause(cls,first):
            """
            """
            output.write( "\n      " if first else "\n\\land " )
            first = False

            # build the latex clause
            if len(cls)==0:
                output.write("\\square")

            else:
                output.write("\\left( " + \
                             " \\lor ".join(map_literals(l) for l in cls) + \
                             " \\right)")

        # with comments
        m = len(self._clauses)
        clauseidx=_ClosedIterator(enumerate(self._clauses),(m+1,None))
        if add_comments:
            comments =_ClosedIterator(iter(self._comments),(m+1,None))
        else:
            comments =_ClosedIterator(iter([]),(m+1,None))

        index_clause,clause   = clauseidx.next()
        index_comment,comment = comments.next()

        while True:

            if index_clause==index_comment==m+1: break

            if index_comment <= index_clause:
                for s in comment.split("\n"): output.write( ("\n% "+s).rstrip(' ') )
                index_comment,comment = comments.next()
            else:
                write_clause(clause,empty_cnf)
                index_clause,clause   = clauseidx.next()
                empty_cnf=False

        # No clause in the CNF
        if empty_cnf: output.write("\n   \\top")

        # final formula
        output.write(" }")
        return output.getvalue()



###
### Various utility function for CNFs
###
def parity_constraint( vars, b ):
    """Output the CNF encoding of a parity constraint

    E.g. X1 + X2 + X3 = 1 (mod 2) is encoded as

    ( X1 v  X2 v  X3)
    (~X1 v ~X2 v  X3)
    (~X1 v  X2 v ~X3)
    ( X1 v ~X2 v ~X3)

    Arguments:
    - `vars`: variables in the constraint
    - `b`   : the requested parity

    Returns: a list of clauses
    >>> parity_constraint(['a','b'],1)
    [[(True, 'a'), (True, 'b')], [(False, 'a'), (False, 'b')]]
    >>> parity_constraint(['a','b'],0)
    [[(True, 'a'), (False, 'b')], [(False, 'a'), (True, 'b')]]
    >>> parity_constraint(['a'],0)
    [[(False, 'a')]]
    """
    domains = tuple([ ((True,var),(False,var)) for var in vars] )
    clauses=[]
    for c in product(*domains):
        # Save only the clauses with the right polarity
        parity = sum(1-l[0] for l in c) % 2
        if parity != b : clauses.append(list(c))
    return clauses
