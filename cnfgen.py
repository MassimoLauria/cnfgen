#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

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

import sys
from textwrap import dedent
from itertools import product,permutations
from itertools import combinations,combinations_with_replacement

import argparse
import random

try:
    import networkx
    import networkx.algorithms
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",
          file=sys.stderr)
    exit(-1)



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
### Lifted CNFs
###

class Lift(CNF):
    """Lifted formula

    A formula is made harder by the process of lifting.

    For efficiency reasons current implementation do not include
    comments in the lifted version of the formula.
    """

    def __init__(self, cnf):
        """Build a new CNF with by lifing the old CNF

        Arguments:
        - `cnf`: the original cnf
        """
        assert cnf._coherent
        self._orig_cnf = cnf
        CNF.__init__(self,[],header=cnf._header)

        # Load original variable names
        variablenames = [None]+list(self._orig_cnf.variables())
        substitutions = [None]*(2*len(variablenames)-1)

        # Lift all possible literals
        for i in range(1,len(variablenames)):
            substitutions[i] =self.lift_a_literal(True, variablenames[i])
            substitutions[-i]=self.lift_a_literal(False,variablenames[i])

        # Collect new variable names from the CNFs:
        # clause compression needs the variable names
        for i in range(1,len(substitutions)):
            for clause in substitutions[i]:
                for _,varname in clause:
                    self.add_variable(varname)

        # Compress substitution cnfs
        for i in range(1,len(substitutions)):
            substitutions[i] =[list(self._compress_clause(cls))
                               for cls in substitutions[i] ]

        # build and add new clauses
        clauses=self._orig_cnf._clauses

        # dictionary of comments
        commentlines=dict()
        for (i,c) in self._orig_cnf._comments:
            commentlines.setdefault(i,[]).append(c)

        for i in xrange(len(clauses)):

            # add comments if necessary
            if i in commentlines:
                for comment in commentlines[i]:
                    self._comments.append((len(self._clauses),comment))

            # a substituted clause is the OR of the substituted literals
            domains=[ substitutions[lit] for lit in clauses[i] ]
            domains=tuple(domains)

            block = [ tuple([lit for clauses[i] in clause_tuple
                                 for lit in clauses[i] ])
                      for clause_tuple in product(*domains)]

            self._add_compressed_clauses(block)

        # add trailing comments
        if len(clauses) in commentlines:
            for comment in commentlines[len(clauses)]:
                self._comments.append((len(self._clauses),comment))

        assert self._check_coherence()

    def lift_a_literal(self, polarity, name):
        """Substitute a literal with the lifting function

        Arguments:
        - `polarity`: polarity of the literal
        - `name`:     variable to be substituted

        Returns: a list of clauses
        """
        raise NotImplementedError("Specialize this class to implement some type of lifting")



class IfThenElse(Lift):
    """Lifted formula: substitutes variable with a three variables
    if-then-else
    """
    def __init__(self, cnf, rank=1):
        """Build a new CNF obtained by substituting an if-then-else to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: ignored
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="If-Then-Else substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a positive literal with an if then else statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: variable to be substituted

        Returns: a list of clauses
        """
        X = "{{{}}}^{{x}}".format(varname)
        Y = "{{{}}}^{{y}}".format(varname)
        Z = "{{{}}}^{{z}}".format(varname)

        return [ [ (False,X) , (polarity,Y) ] , [ (True, X) , (polarity,Z) ] ]


class Majority(Lift):
    """Lifted formula: substitutes variable with a Majority
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a Majority to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="Majority {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a positive literal with Loose Majority,
        and negative literals with Strict Minority.

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """

        # Majority is espressed as a set of positive clauses,
        # while Minority as a set on negative ones
        lit = [ (polarity,"{{{}}}^{}".format(varname,i)) for i in range(self._rank) ]

        if polarity:
            witness = self._rank // 2 + 1   # avoid strict majority of 'False'
        else:
            witness = (self._rank + 1) // 2 # avoid loose  majority of 'True'

        binom = combinations

        return [ s for s in binom(lit,witness) ]


class InnerOr(Lift):
    """Lifted formula: substitutes variable with a OR
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a OR to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="OR {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a positive literal with an OR,
        and negative literals with its negation.

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        if polarity:
            return [[ (True,name) for name in names ]]
        else:
            return [ [(False,name)] for name in names ]


class Equality(Lift):
    """Lifted formula: substitutes variable with 'all equals'
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting 'all equals' to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="EQ {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a positive literal with an 'all equal' statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        pairs = permutations(names,2)
        if polarity:
            return [ [ (False,a) , (True,b) ] for a,b in pairs ] # a true variable implies all the others to true.

        else:
            return [[ (False,a) for a in names ] , [ (True,a) for a in names ] ] # at least a true and a false variable.


class InnerXor(Lift):
    """Lifted formula: substitutes variable with a XOR
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a XOR to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="XOR {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a literal with a (negated) XOR

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        return parity_constraint(names,polarity)


class Selection(Lift):
    """Lifted formula: Y variable select X values
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by lifting procedures

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="Formula lifted by selectors over {} values\n\n".format(self._rank) \
            +self._header

        # Each selector must select!
        self.add_comment("Selections must be defined")
        for v in cnf.variables():
            self.add_clause([ (True,   "Y_{{{}}}^{}".format(v,i))
                               for i in range(self._rank)])
        # Selection must be unique
        self.add_comment("Selections must be unique")
        for v in cnf.variables():
            for s1,s2 in combinations(["Y_{{{}}}^{}".format(v,i)
                                                 for i in range(self._rank)],2):
                self.add_clause([(False,s1),(False,s2)])

        self._header="Rank {} lifted formula\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a literal with a (negated) XOR

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        clauses=[]
        for i in range(self._rank):
            clauses.append([ (False,   "Y_{{{}}}^{}".format(varname,i)),
                             (polarity,"X_{{{}}}^{}".format(varname,i)) ])
        return clauses


###
### Formula families
###

def PigeonholePrinciple(pigeons,holes,functional=False,onto=False):
    """Pigeonhole Principle CNF formula

    The pigeonhole  principle claims  that no M  pigeons can sit  in N
    pigeonholes  without collision  if M>N.   The  counterpositive CNF
    formulation  requires  such mapping  to  be  satisfied. There  are
    different  variants of this  formula, depending  on the  values of
    `functional` and `onto` argument.

    - PHP: pigeon can sit in multiple holes
    - FPHP: each pigeon sits in exactly one hole
    - onto-PHP: pigeon can  sit in multiple holes, every  hole must be
                covered.
    - Matching: one-to-one bijection between pigeons and holes.

    Arguments:
    - `pigeon`: number of pigeons
    - `hole`:   number of holes
    - `functional`: add clauses to enforce at most one hole per pigeon
    - `onto`: add clauses to enforce that any hole must have a pigeon

    >>> print(PigeonholePrinciple(4,3).dimacs(False,True))
    p cnf 12 22
    c Pigeon axiom: pigeon 1 sits in a hole
    1 2 3 0
    c Pigeon axiom: pigeon 2 sits in a hole
    4 5 6 0
    c Pigeon axiom: pigeon 3 sits in a hole
    7 8 9 0
    c Pigeon axiom: pigeon 4 sits in a hole
    10 11 12 0
    c No collision in hole 1
    -1 -4 0
    -1 -7 0
    -1 -10 0
    -4 -7 0
    -4 -10 0
    -7 -10 0
    c No collision in hole 2
    -2 -5 0
    -2 -8 0
    -2 -11 0
    -5 -8 0
    -5 -11 0
    -8 -11 0
    c No collision in hole 3
    -3 -6 0
    -3 -9 0
    -3 -12 0
    -6 -9 0
    -6 -12 0
    -9 -12 0
    """
    if functional:
        if onto:
            formula_name="Matching"
        else:
            formula_name="Functional pigeonhole principle"
    else:
        if onto:
            formula_name="Onto pigeonhole principle"
        else:
            formula_name="Pigeonhole principle"

    # Clause generator
    def _PHP_clause_generator(pigeons,holes,functional,onto):
        # Pigeon axioms
        for p in xrange(1,pigeons+1):
            yield "Pigeon axiom: pigeon {0} sits in a hole".format(p)
            yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for h in xrange(1,holes+1)]
        # Onto axioms
        if onto:
            for h in xrange(1,holes+1):
                yield "Onto hole axiom: hole {0} hosts a pigeon".format(h)
                yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for p in xrange(1,pigeons+1)]
        # No conflicts axioms
        for h in xrange(1,holes+1):
            yield "No collision in hole {0}".format(h)
            for (p1,p2) in combinations(range(1,pigeons+1),2):
                yield [ (False,'p_{{{0},{1}}}'.format(p1,h)),
                        (False,'p_{{{0},{1}}}'.format(p2,h)) ]
        # Function axioms
        if functional:
            for p in xrange(1,pigeons+1):
                yield "No multiple images for pigeon {0}".format(p)
                for (h1,h2) in combinations(range(1,holes+1),2):
                    yield [ (False,'p_{{{0},{1}}}'.format(p,h1)),
                            (False,'p_{{{0},{1}}}'.format(p,h2)) ]

    php=CNF()
    php.header="{0} formula for {1} pigeons and {2} holes\n".format(formula_name,pigeons,holes) + php.header

    clauses=_PHP_clause_generator(pigeons,holes,functional,onto)
    for c in clauses:
        php.add_clause_or_comment(c)

    return php


def PebblingFormula(digraph):
    """Pebbling formula

    Build a pebbling formula from the directed graph. If the graph has
    an `ordered_vertices` attribute, then it is used to enumerate the
    vertices (and the corresponding variables).

    Arguments:
    - `digraph`: directed acyclic graph.
    """
    if not networkx.algorithms.is_directed_acyclic_graph(digraph):
        raise RuntimeError("Pebbling formula is defined only for directed acyclic graphs")

    peb=CNF()

    if hasattr(digraph,'name'):
        peb.header="Pebbling formula of: "+digraph.name+"\n\n"+peb.header
    else:
        peb.header="Pebbling formula\n\n"+peb.header

    # add variables in the appropriate order
    vertices=enumerate_vertices(digraph)

    for v in vertices:
        peb.add_variable(v)

    # add the clauses
    for v in vertices:

        # If predecessors are pebbled it must be pebbles
        if digraph.in_degree(v)!=0:
            peb.add_comment("Pebbling propagates on vertex {}".format(v))
        else:
            peb.add_comment("Source vertex {}".format(v))

        peb.add_clause([(False,p) for p in digraph.predecessors(v)]+[(True,v)])

        if digraph.out_degree(v)==0: #the sink
            peb.add_comment("Sink vertex {}".format(v))
            peb.add_clause([(False,v)])

    return peb


def OrderingPrinciple(size,total=False,smart=False):
    """Generates the clauses for ordering principle

    Arguments:
    - `size`  : size of the domain
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
    """

    return GraphOrderingPrinciple(networkx.complete_graph(size),total,smart)


def GraphOrderingPrinciple(graph,total=False,smart=False):
    """Generates the clauses for graph ordering principle

    Arguments:
    - `graph` : undirected graph
    - `total` : add totality axioms (i.e. "x < y" or "x > y")
    - `smart` : "x < y" and "x > y" are represented by a single variable (implies totality)
    """
    gop=CNF()

    # Describe the formula
    if total or smart:
        name="Total graph ordering principle"
    else:
        name="Graph ordering principle"

    if smart:
        name = name + "(compact representation)"

    if hasattr(graph,'name'):
        gop.header=name+" on graph:\n"+graph.name+"\n"+gop.header
    else:
        gop.header=name+".\n"+gop.header

    # Non minimality axioms
    gop.add_comment("Each vertex has a predecessor")

    # Fix the vertex order
    V=graph.nodes()

    # Clause is generated in such a way that if totality is enforces,
    # every pair occurs with a specific orientation.
    for med in xrange(len(V)):
        clause = []
        for lo in xrange(med):
            if graph.has_edge(V[med],V[lo]):
                clause += [(True,'x_{{{0},{1}}}'.format(lo,med))]
        for hi in xrange(med+1,len(V)):
            if not graph.has_edge(V[med],V[hi]):
                continue
            elif smart:
                clause += [(False,'x_{{{0},{1}}}'.format(med,hi))]
            else:
                clause += [(True,'x_{{{0},{1}}}'.format(hi,med))]
        gop.add_clause(clause)

    # Transitivity axiom
    gop.add_comment("Relation must be transitive")

    if len(V)>=3:
        if smart:
            # Optimized version if smart representation of totality is used
            for (v1,v2,v3) in combinations(V,3):
                gop.add_clause([ (True,'x_{{{0},{1}}}'.format(v1,v2)),
                                (True,'x_{{{0},{1}}}'.format(v2,v3)),
                                (False,'x_{{{0},{1}}}'.format(v1,v3))])
                gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True,'x_{{{0},{1}}}'.format(v1,v3))])
        else:
            for (v1,v2,v3) in permutations(V,3):
                gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True, 'x_{{{0},{1}}}'.format(v1,v3))])

    if not smart:
        # Antisymmetry axioms (useless for 'smart' representation)
        gop.add_comment("Relation must be anti-symmetric")
        for (v1,v2) in combinations(V,2):
            gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                            (False,'x_{{{0},{1}}}'.format(v2,v1))])

        # Totality axioms (useless for 'smart' representation)
        if total:
            gop.add_comment("Relation must be total")
            for (v1,v2) in combinations(V,2):
                gop.add_clause([ (True,'x_{{{0},{1}}}'.format(v1,v2)),
                                 (True,'x_{{{0},{1}}}'.format(v2,v1))])

    return gop


def RamseyNumber(s,k,N):
    """Formula claiming that Ramsey number r(s,k) > N

    Arguments:
    - `s`: independent set size
    - `k`: clique size
    - `N`: vertices
    """

    ram=CNF()

    ram.header=dedent("""\
        CNF encoding of the claim that there is a graph of %d vertices
        with no indipendent set of size %d and no clique of size %d
        """ % (s,k,N)) + ram.header

    # No independent set of size s
    ram.add_comment("No independent set of size %d" % s)

    for vertex_set in combinations(xrange(1,N+1),s):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause += [(True,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    # No clique of size k
    ram.add_comment("No clique of size %d"%k)

    for vertex_set in combinations(xrange(1,N+1),k):
        clause=[]
        for edge in combinations(vertex_set,2):
            clause+=[(False,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    return ram


def TseitinFormula(graph,charges=None):
    """Build a Tseitin formula based on the input graph.

Odd charge is put on the first vertex by default, unless other
vertices are is specified in input.

    Arguments:
    - `graph`: input graph
    - `charges': odd or even charge for each vertex
    """
    V=graph.nodes()

    if charges==None:
        charges=[1]+[0]*(len(V)-1)             # odd charge on first vertex
    else:
        charges = [bool(c) for c in charges]   # map to boolean

    if len(charges)<len(V):
        charges=charges+[0]*(len(V)-len(charges))  # pad with even charges

    # init formula
    ordered_edges=graph.edges()
    tse=CNF()
    for (v,w) in graph.edges():
        tse.add_variable("E_{{{0},{1}}}".format(v,w))

    # add constraints
    ordered_edges=graph.edges()
    for v,c in zip(V,charges):
        tse.add_comment("Vertex {} must have {} charge".format(v," odd" if c else "even"))

        edges=filter(lambda e: v in e, ordered_edges)

        # produce all clauses and save half of them
        names = [ "E_{{{0},{1}}}".format(v,w) for (v,w) in edges ]
        for cls in parity_constraint(names,c):
            tse.add_clause(list(cls))

    return tse

def SubgraphFormula(graph,templates):
    """Formula which claims that one of the subgraph is contained in a
    graph.

    Arguments:
    - `graph'    : input graph
    - `templates': a sequence of graphs
    """

    F=CNF()

    # One of the templates is chosen to be the subgraph
    if len(templates)==0:
        return F
    elif len(templates)==1:
        selectors=[]
    elif len(templates)==2:
        selectors=['c']
    else:
        selectors=['c_{{{}}}'.format(i) for i in range(len(templates))]

    if len(selectors)>1:

        F.add_comment("Exactly of the graphs must be a subgraph")
        F.add_clause([(True,v) for v in selectors])

        for (a,b) in combinations(selectors):
            F.add_clause( [ (False,a), (False,b) ] )

    # comment the formula accordingly
    if len(selectors)>1:
        F.header=dedent("""\
                 CNF encoding of the claim that a graph contains one among
                 a family of {0} possible subgraphs.
                 """.format(len(templates))) + F.header
    else:
        F.header=dedent("""\
                 CNF encoding of the claim that a graph contains an induced
                 copy of a subgraph.
                 """.format(len(templates)))  + F.header

    # A subgraph is chosen
    N=graph.order()
    k=max([s.order() for s in templates])

    for i,j in product(range(k),range(N)):
        F.add_variable("S_{{{0}}}{{{1}}}".format(i,j))

    # each vertex has an image
    F.add_comment("A subgraph is chosen")
    for i in range(k):
        F.add_clause([(True,"S_{{{0}}}{{{1}}}".format(i,j)) for j in range(N)])

    # and exactly one
    F.add_comment("The mapping is a function")
    for i,(a,b) in product(range(k),combinations(range(N),2)):
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(i,a)),
                      (False,"S_{{{0}}}{{{1}}}".format(i,b))  ])

    # # and there are no collision
    # F.add_comment("The function is injective")
    # for (a,b),j in product(combinations(range(k),2),range(N)):
    #     F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(a,j)),
    #                   (False,"S_{{{0}}}{{{1}}}".format(b,j))  ])

    F.add_comment("Mapping is strictly monotone increasing (so it is also injective)")
    localmaps = product(combinations(range(k),2),
                        combinations_with_replacement(range(N),2))

    for (a,b),(i,j) in localmaps:
        F.add_clause([(False,"S_{{{0}}}{{{1}}}".format(min(a,b),max(i,j))),
                      (False,"S_{{{0}}}{{{1}}}".format(max(a,b),min(i,j)))  ])


    # The selectors choose a template subgraph.  A mapping must map
    # edges to edges and non-edges to non-edges for the active
    # template.

    if len(templates)==1:

        activation_prefixes=[[]]

    elif len(templates)==2:

        activation_prefixes = [[(True,selectors[0])],[(False,selectors[0])]]

    else:
        activation_prefixes = [[(True,v)] for v in selectors]


    # maps must preserve the structure of the template graph
    gV = graph.nodes()

    for i in range(len(templates)):


        k  = templates[i].order()
        tV = templates[i].nodes()

        localmaps = product(combinations(range(k),2),
                            combinations(range(N),2))

        F.add_comment("structure constraints for subgraph {}".format(i))

        for (i1,i2),(j1,j2) in localmaps:

            # check if this mapping is compatible
            tedge=templates[i].has_edge(tV[i1],tV[i2])
            gedge=graph.has_edge(gV[j1],gV[j2])
            if tedge == gedge: continue

            # if it is not, add the corresponding
            F.add_clause(activation_prefixes[i] + \
                         [(False,"S_{{{0}}}{{{1}}}".format(min(i1,i2),min(j1,j2))),
                          (False,"S_{{{0}}}{{{1}}}".format(max(i1,i2),max(j1,j2))) ])

    return F


#################################################################
#          Graph Decoders (first is default)
#################################################################
implemented_graphformats = {
    'dag':   ['kth','gml','dot'],
    'bipartite':   ['kth','gml','dot'],
    'digraph': ['kth','gml','dot'],
    'simple': ['kth','gml','dot']
    }

# remove dot format if graphviz is not installed
# we put it by default for documentation purpose
try:
    import pygraphviz
except ImportError:
    print("WARNING: Missing 'dot' library: no support for graph based formulas.",
          file=sys.stderr)
    for k in implemented_graphformats.values():
        try:
            k.remove('dot')
        except ValueError:
            pass


def readDigraph(file,format,force_dag=False,multi=False):
    """Read a directed graph from file

    Arguments:
    - `file`: file object
    - `format`: file format
    - `force_dag`: enforces whether graph must be acyclic
    - `multi`:     multiple edge allowed

    Return: a networkx.DiGraph / networkx.MultiDiGraph object.
    """
    if format not in implemented_graphformats['digraph']:
        raise ValueError("Invalid format for directed graph")

    if multi:
        grtype=networkx.MultiDiGraph
    else:
        grtype=networkx.DiGraph

    if format=='dot':

        D=grtype(pygraphviz.AGraph(file.read()).edges())

    elif format=='gml':

        D=grtype(networkx.read_gml(file))

    elif format=='kth':

        D=grtype()
        D.name=''
        D.ordered_vertices=[]

        for l in file.readlines():

            # add the comment to the header
            if l[0]=='c':
                D.name+=l[2:]
                continue

            if ':' not in l:
                continue # vertex number spec (we ignore it)

            target,sources=l.split(':')
            target=target.strip()
            sources=sources.split()

            # Load all vertices in this line
            for vertex in [target]+sources:
                if vertex not in D:
                    D.add_node(vertex)
                    D.ordered_vertices.append(vertex)

            for s in sources:
                D.add_edge(s,target)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(format))

    if force_dag and not networkx.algorithms.is_directed_acyclic_graph(D):
        raise ValueError("Graph must be acyclic".format(format))

    return D


def readGraph(file,format,multi=False):
    """Read a graph from file

    Arguments:
    - `file`: file object
    - `format`: file format
    - `multi`: multiple edge allowed

    Return: a networkx.Graph / networkx.MultiGraph object.
    """
    if format not in implemented_graphformats['simple']:
        raise ValueError("Invalid format for undirected graph")

    if multi:
        grtype=networkx.MultiGraph
    else:
        grtype=networkx.Graph

    if format=='dot':

        G=grtype(pygraphviz.AGraph(file.read()).edges())

    elif format=='gml':

        G=grtype(networkx.read_gml(file))

    elif format=='kth':

        G=grtype()
        G.name=''
        G.ordered_vertices=[]

        for l in file.readlines():

            # add the comment to the header
            if l[0]=='c':
                G.name+=l[2:]
                continue

            if ':' not in l:
                continue # vertex number spec

            target,sources=l.split(':')
            target=target.strip()
            sources=sources.split()

            # Load all vertices in this line
            for vertex in [target]+sources:
                if vertex not in G:
                    G.add_node(vertex)
                    G.ordered_vertices.append(vertex)

            for s in sources:
                G.add_edge(s,target)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(format))

    return G


def writeGraph(G,output_file,format,graph_type='simple'):
    """Write a graph to a file

    Arguments:
    - `G`: graph object
    - `output_file`: file name or file handle to write on
    - `output_format`: graph format (e.g. dot, gml)
    - `graph_type`: one among {graph,digraph,dag,bipartite}

    Return: none.
    """
    if graph_type not in implemented_graphformats:
        raise ValueError("Invalid graph type")

    if format not in implemented_graphformats[graph_type]:
        raise ValueError("Invalid format for {} graph".format(graph_type))

    if format=='dot':

        networkx.write_dot(G,output_file)

    elif format=='gml':

        networkx.write_gml(G,output_file)

    elif format=='kth':

        print("c {}".format(G.name),file=output_file)
        print("{}".format(G.order()),file=output_file)

        # we need numerical indices for the vertices
        enumeration = zip( enumerate_vertices(G),
                               xrange(1,G.order()+1))

        # adj list in the same order
        indices = dict( enumeration )

        from cStringIO import StringIO
        output = StringIO()

        for v,i in enumeration:

            if G.is_directed():
                neighbors = [indices[w] for w in G.predecessors(v)]

            else:
                neighbors = [indices[w] for w in G.adj[v].keys()]

            neighbors.sort()

            output.write( str(i)+" : ")
            output.write( " ".join([str(i) for i in neighbors]))
            output.write( "\n")

        print(output.getvalue(),file=output_file)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(format))

    return G


###
### Various utility function
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

def enumerate_vertices(graph):
    """Compute an ordered list of vertices of `graph`

    If the graph as the field `ordered_vertices` use it. Otherwise
    give an arbitrary vertex sequence.

    Arguments:
    - `graph`: input graph
    """
    if hasattr(graph,"ordered_vertices"):
        assert graph.order()==len(graph.ordered_vertices)
        assert set(graph.nodes())==set(graph.ordered_vertices)
        return graph.ordered_vertices
    else:
        return graph.nodes()



#################################################################
#          Command line tool follows
#################################################################

###
### Implemented features
###
implemented_lifting = {

    # lifting name : ("help description", function, default rank)

    'none': ("leaves the formula alone", (lambda c,r:c),1),
    'or'  : ("OR substitution     (default rank: 2)", InnerOr,2),
    'xor' : ("XOR substitution    (default rank: 2)", InnerXor,2),
    'sel' : ("selection lifting   (default rank: 3)", Selection,3),
    'eq'  : ("all variables equal (default rank: 2)", Equality,3),
    'ite' : ("if x then y else z  (rank ignored)",    IfThenElse,3),
    'maj' : ("Loose majority      (default rank: 2)", Majority,3)
    }



###
### Command line helpers
###

class _CMDLineHelper(object):
    """Base Command Line helper

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def setup_command_line(parser):
        """Add command line options for this family of formulas
        """
        pass

    @staticmethod
    def additional_options_check(args):
        pass


class _GeneralCommandLine(_CMDLineHelper):
    """Command Line helper for the general commands

    For every formula family there should be a subclass.
    """

    @staticmethod
    def setup_command_line(parser):
        """Setup general command line options

        Arguments:
        - `parser`: parser to fill with options
        """
        parser.add_argument('--output','-o',
                            type=argparse.FileType('wb',0),
                            metavar="<output>",
                            default='-',
                            help="""Output file. The formula is saved
                            on file instead of being sent to standard
                            output. Setting '<output>' to '-' is another
                            way to send the formula to standard output.
                            (default: -)
                            """)
        parser.add_argument('--output-format','-of',
                            choices=['latex','dimacs'],
                            default='dimacs',
                            help="""
                            Output format of the formulas. 'latex' is
                            convenient to insert formulas into papers, and
                            'dimacs' is the format used by sat solvers.
                            (default: dimacs)
                            """)

        parser.add_argument('--seed','-S',
                            metavar="<seed>",
                            default=None,
                            type=str,
                            action='store',
                            help="""Seed for any random process in the
                            program. Any python hashable object will
                            be fine.  (default: current time)
                            """)
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--verbose', '-v',action='count',default=1,
                       help="""Add comments inside the formula. It may
                            not be supported by very old sat solvers.
                            """)
        g.add_argument('--quiet', '-q',action='store_const',const=0,dest='verbose',
                       help="""Output just the formula with not header
                            or comment.""")
        parser.add_argument('--lift','-l',
                            metavar="<lifting method>",
                            choices=implemented_lifting.keys(),
                            default='none',
                            help="""
                            Apply a lifting procedure to make the CNF harder.
                            See `--help-lifting` for more informations
                            """)
        parser.add_argument('--liftrank','-lr',
                            metavar="<lifting rank>",
                            type=int,
                            help="""
                            Hardness parameter for the lifting procedure.
                            See `--help-lifting` for more informations
                            """)
        parser.add_argument('--help-lifting',action='store_true',help="""
                             Formula can be made harder applying some
                             so called "lifting procedures".
                             This gives information about the implemented lifting.
                             (not implemented yet)
                             """)


### Graph readers/generators

class _GraphHelper(object):
    """Command Line helper for reading graphs
    """

    @staticmethod
    def obtain_graph(args):
        raise NotImplementedError("Graph Input helper must be subclassed")


class _DAGHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group("Reading a directed acyclic graph (DAG) from input")
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The DAG is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Output the DAG to a file. The
                            graph is saved, which is useful if the
                            graph is generated internally.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=implemented_graphformats['dag'],
                        default=implemented_graphformats['dag'][0],
                        help="""
                        Format of the DAG in input/output, several
                        formats are supported if networkx is
                        installed.  (default:  {})
                        """.format(implemented_graphformats['dag'][0]))

        gr=parser.add_argument_group("Generate input DAG from a library")
        gr=gr.add_mutually_exclusive_group()
        gr.add_argument('--tree',type=int,action='store',metavar="<height>",
                            help="tree graph")

        gr.add_argument('--pyramid',type=int,action='store',metavar="<height>",
                            help="pyramid graph")

    @staticmethod
    def obtain_graph(args):
        """Produce a DAG from either input or library
        """
        if hasattr(args,'tree') and args.tree>0:

            D=networkx.DiGraph()
            D.ordered_vertices=[]
            # vertices
            vert=['v_{}'.format(i) for i in range(1,2*(2**args.tree))]
            for w in vert:
                D.add_node(w)
                D.ordered_vertices.append(w)
            # edges
            for i in range(len(vert)//2):
                D.add_edge(vert[2*i+1],vert[i])
                D.add_edge(vert[2*i+2],vert[i])

        elif hasattr(args,'pyramid') and args.pyramid>0:

            D=networkx.DiGraph()
            D.name='Pyramid of height {}'.format(args.pyramid)
            D.ordered_vertices=[]

            # vertices
            X=[
                [('x_{{{},{}}}'.format(h,i),h,i) for i in range(args.pyramid-h+1)]
                for h in range(args.pyramid+1)
              ]

            for layer in X:
                for (name,h,i) in layer:
                    D.add_node(name,rank=(h,i))
                    D.ordered_vertices.append(name)

            # edges
            for h in range(1,len(X)):
                for i in range(len(X[h])):
                    D.add_edge(X[h-1][i][0]  ,X[h][i][0])
                    D.add_edge(X[h-1][i+1][0],X[h][i][0])

        elif args.graphformat:

            D=readDigraph(args.input,args.graphformat,force_dag=True)

        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(D,
                       args.savegraph,
                       args.graphformat,
                       graph_type='dag')

        return D


class _SimpleGraphHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group("Read/Write the underlying undirected graph")
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The graph is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Output the graph to a file. The
                            graph is saved, which is useful if the
                            graph is randomly generated internally.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=implemented_graphformats['simple'],
                        default=implemented_graphformats['simple'][0],
                        help="""
                        Format of the graph in input/output, several
                        formats are supported in networkx is
                        installed.  (default:  {})
                        """.format(implemented_graphformats['simple'][0]))


        gr=parser.add_argument_group("Generate input graph from a library")
        gr=gr.add_mutually_exclusive_group()

        class IntFloat(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                n, p = int(values[0]),float(values[1])
                if not isinstance(n,int):
                    raise ValueError('n must be an integer')
                if not (isinstance(p,float) and p<=1.0 and p>=0):
                    raise ValueError('p must be an float between 0 and 1')
                setattr(args, self.dest, (n,p))

        gr.add_argument('--gnp',nargs=2,action=IntFloat,metavar=('n','p'),
                            help="random graph according to G(n,p) model (i.e. independent edges)")


        gr.add_argument('--gnm',type=int,nargs=2,action='store',metavar=('n','m'),
                            help="random graph according to G(n,m) model (i.e. m random edges)")

        gr.add_argument('--gnd',type=int,nargs=2,action='store',metavar=('n','d'),
                            help="random d-regular graph according to G(n,d) model (i.e. d random edges per vertex)")

        gr.add_argument('--grid',type=int,nargs='+',action='store',metavar=('d1','d2'),
                        help="n-dimensional grid of dimension d1 x d2 x ... ")

        gr.add_argument('--complete',type=int,action='store',metavar="<N>",
                            help="complete graph on N vertices")

        gr=parser.add_argument_group("Graph modifications")
        gr.add_argument('--plantclique',type=int,action='store',metavar="<k>",
                            help="choose k vertices at random and add all edges among them")


    @staticmethod
    def obtain_graph(args):
        """Build a Graph according to command line arguments

        Arguments:
        - `args`: command line options
        """
        if hasattr(args,'gnd') and args.gnd:

            n,d = args.gnd
            if (n*d)%2 == 1:
                raise ValueError("n * d must be even")
            G=networkx.random_regular_graph(d,n)
            return G

        elif hasattr(args,'gnp') and args.gnp:

            n,p = args.gnp
            G=networkx.gnp_random_graph(n,p)

        elif hasattr(args,'gnm') and args.gnm:

            n,m = args.gnm
            G=networkx.gnm_random_graph(n,m)

        elif hasattr(args,'grid') and args.grid:

            G=networkx.grid_graph(args.grid)

        elif hasattr(args,'complete') and args.complete>0:

            G=networkx.complete_graph(args.complete)

        elif args.graphformat:

            G=readGraph(args.input,args.graphformat)
        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Graph modifications
        if hasattr(args,'plantclique') and args.plantclique>1:

            clique=random.sample(G.nodes(),args.plantclique)

            for v,w in combinations(clique,2):
                G.add_edge(v,w)

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(G,
                       args.savegraph,
                       args.graphformat,
                       graph_type='simple')

        return G

### Formula families

class _FormulaFamilyHelper(object):
    """Command Line helper for formula families

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def build_cnf(args):
        pass


class _PHP(_FormulaFamilyHelper,_CMDLineHelper):
    name='php'
    description='pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('pigeons',metavar='<pigeons>',type=int,help="Number of pigeons")
        parser.add_argument('holes',metavar='<holes>',type=int,help="Number of holes")
        parser.add_argument('--functional',action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',action='store_true',
                            help="every hole has a sitting pigeon")
        parser.set_defaults(func=_PHP.build_cnf)

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PigeonholePrinciple(args.pigeons,
                                   args.holes,
                                   functional=args.functional,
                                   onto=args.onto)


class _RAM(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for RamseyNumber formulas
    """
    name='ram'
    description='ramsey number principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('s',metavar='<s>',type=int,help="Forbidden independent set size")
        parser.add_argument('k',metavar='<k>',type=int,help="Forbidden independent clique")
        parser.add_argument('N',metavar='<N>',type=int,help="Graph size")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RamseyNumber(args.s, args.k, args.N)


class _OP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Ordering principle formulas
    """
    name='op'
    description='ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")
        parser.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        parser.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return OrderingPrinciple(args.N,args.total,args.smart)


class _GOP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Graph Ordering principle formulas
    """
    name='gop'
    description='graph ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Graph ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        parser.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return GraphOrderingPrinciple(G,args.total,args.smart)


class _KClique(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for k-clique formula
    """
    name='kclique'
    description='k clique formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k)])


class _RAMLB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for ramsey graph formula
    """
    name='ramlb'
    description='unsat if G witnesses that r(k,s)>|V(G)| (i.e. G has not k-clique nor s-stable)'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for ramsey witness formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        parser.add_argument('s',metavar='<s>',type=int,action='store',help="size of the stable to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k),
                                  networkx.complete_graph(args.s)])



class _TSE(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Tseitin  formulas
    """
    name='tseitin'
    description='tseitin formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Tseitin formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--charge',metavar='<charge>',default='first',
                            choices=['first','random','randomodd','randomeven'],
                            help="""charge on the vertices.
                                    `first'  puts odd charge on first vertex;
                                    `random' puts a random charge on vertices;
                                    `randomodd' puts random odd  charge on vertices;
                                    `randomeven' puts random even charge on vertices.
                                     """)
        _SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)

        if G.order()<1:
            charge=None

        elif args.charge=='first':

            charge=[1]+[0]*(G.order()-1)

        else: # random vector
            charge=[random.randint(0,1) for i in xrange(G.order()-1)]

            parity=sum(charge) % 2

            if args.charge=='random':
                charge.append(random.randint(0,1))
            elif args.charge=='randomodd':
                charge.append(1-parity)
            elif args.charge=='randomeven':
                charge.append(parity)
            else:
                raise ValueError('Illegal charge specification on command line')

        return TseitinFormula(G,charge)


class _OR(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='or'
    description='a single disjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for single or of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build an disjunction

        Arguments:
        - `args`: command line options
        """
        clause = [ (True,"x_{}".format(i)) for i in range(args.P) ] + \
                 [ (False,"y_{}".format(i)) for i in range(args.N) ]
        return CNF([clause],
                   header="""Single clause with {} positive and {} negative literals""".format(args.P,args.N))


class _PEB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='peb'
    description='pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        _DAGHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D=_DAGHelper.obtain_graph(args)
        return PebblingFormula(D)


class _AND(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='and'
    description='a single conjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        clauses = [ [(True,"x_{}".format(i))] for i in range(args.P) ] + \
                  [ [(False,"y_{}".format(i))] for i in range(args.N) ]
        return CNF(clauses,
                   header="""Singleton clauses: {} positive and {} negative""".format(args.P,args.N))


###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv):

    # Commands and subcommand lines
    cmdline = _GeneralCommandLine
    subcommands=[_PHP,_TSE,_OP,_GOP,_PEB,_RAM,_RAMLB,_KClique,_OR,_AND]

    # Python 2.6 does not have argparse library
    try:
        import argparse
    except ImportError:
        print("Sorry: %s requires `argparse` library, which is missing.\n"%argv[0],file=sys.stderr)
        print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
        print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
        print(" * http://code.google.com/p/argparse",file=sys.stderr)
        print("",file=sys.stderr)
        exit(-1)

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog='cnfgen',epilog="""
    Each <formula type> has its own command line arguments and options.
    For more information type 'cnfgen <formula type> [--help | -h ]'
    """)
    cmdline.setup_command_line(parser)
    subparsers=parser.add_subparsers(title="Available formula types",metavar='<formula type>')

    # Setup of various formula command lines options
    for sc in subcommands:
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(subcommand=sc)

    # Process the options
    args=parser.parse_args()
    cmdline.additional_options_check(args)
    args.subcommand.additional_options_check(args)

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    # Generate the basic formula
    cnf=args.subcommand.build_cnf(args)

    # Apply the lifting
    lift_method=implemented_lifting[args.lift][1]
    lift_rank=args.liftrank or implemented_lifting[args.lift][2]
    lcnf=lift_method(cnf,lift_rank)


    # Do we wnat comments or not
    output_comments=args.verbose >= 2
    output_header  =args.verbose >= 1

    if args.output_format == 'latex':
        output = lcnf.latex(add_header=output_header,
                            add_comments=output_comments)

    elif args.output_format == 'dimacs':
        output = lcnf.dimacs(add_header=output_header,
                           add_comments=output_comments)
    else:
        output = lcnf.dimacs(add_header=output_header,
                           add_comments=output_comments)

    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
