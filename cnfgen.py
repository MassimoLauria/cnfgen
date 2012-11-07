#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

"""
-------------
CNF generator
-------------

The module  `cnfgen` contains facilities to generate  cnf formulas, in
order  to be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In  particular the module implements
both a library of CNF generators and a command line utility.

Copyright (C) 2012  Massimo Lauria <lauria@kth.se>
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

`cnfgen` module contains a lot of prepackaged CNF generator
"""

import sys
import itertools

import argparse

import random
import pygraphviz
import networkx
import networkx.algorithms

_default_header=r"""
Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""

###
### Basic CNF class
###

class CNF(object):
    """Propositional formulas in conjunctive normal form.
    """

    def __init__(self, clauses_and_comments=[], header=None):
        """Propositional formulas in conjunctive normal form.

        To add commented clauses use the `add_clause` and
        `add_comment` methods.

        Arguments:
        - `clauses`: ordered list of clauses; a clause with k literals
                     is a `frozenset` object containing k pairs,
                     each representing a literal.
                     First element is the polarity and the second is
                     the variable, which must be an hashable object.

                     E.g. (not x3) or x4 or (not x2) is encoded as (False,"x3",True,"x4",False,"x2")

        - `header`: a preamble which documents the formula
        """
        self._clauses   = []
        self._variables = []

        self._header = header or _default_header

        for c in clauses_and_comments:
            self.add_clause_or_comment(c)

    # Header
    def _set_header(self, value):
        self._header = value

    def _get_header(self):
        return self._header

    header = property(_get_header, _set_header)

    # Variable/Clause management
    @staticmethod
    def is_legal_variable(v):
        try:
            hash(v)
            return True
        except TypeError:
            return False

    class Clause(tuple):
        """Clause object
        """
        # def __init__(self, seq, check=True):
        #     """A clause of a CNF

        #     A clause is a sequence of literals represented as
        #     (bool,value) where 'value' is any hashable data. The
        #     clause is basically an ordered tuple of such literals.

        #     Arguments:
        #     - `seq`  : a sequence of literals
        #     - `check`: check if the elements are legal literals
        #     """
        #     if check:
        #         for b,v in seq:
        #             if not CNF.is_legal_variable(v):
        #                 raise TypeError("%s is not a legal variable name" %v)

        #     tuple.__init__(self, [(bool(b),v) for b,v in seq ] )

        def __str__(self):
            lit=[]
            for p,v in self:
                if not p: lit.append("~"+unicode(v))
                else: lit.append(unicode(v))
            return '( '+' V '.join(lit)+' )'

        def __repr__(self):
            return 'Clause('+repr(list(self))+')'


    def add_clause(self,clause,repetition=False):
        """Add a well formatted clause to the CNF. It raises
           `ValueError` if the clause is not well formatted.

        Arguments:
        - `clause`: a clause with k literals is a list with k pairs.
                    First coords are the polarities, second coords are
                    utf8 encoded strings with variable names.

                    E.g. (not x3) or x4 or (not x2) is encoded as
                         [(False,u"x3"),(True,u"x4"),(False,u"x2")]
        - `repetition`: allow repeated clauses
        """
        new_clause=[]
        # Check for the format
        for neg,var in clause:
            if type(neg)!=bool or not CNF.is_legal_variable(var):
                raise TypeError("%s is not a well formatted clause" %clause)
            new_clause.append((neg,var))

        # Check for clause repetition
        if (not repetition):
            for cla in self:
                if set(cla)==set(new_clause): return

        # Add all missing variables
        for _,var in new_clause:
            if not var in self._variables:
                self._variables.append(var)
        # Add the clause
        self._clauses.append(CNF.Clause(new_clause))

    def add_variable(self,var):
        """Add a variable to the formula. This is useful to add
        the variable in a nice order than the appearence one.

        Arguments:
        - `var`: the variable to add.
        """
        if not CNF.is_legal_variable(var):
                raise TypeError("%s is not a legal variable name" %var)

        if not var in self._variables:
            self._variables.append(var)

    def add_comment(self,comment):
        """Add a comment to the formula.

        This is useful for documenting cnfs in DIMACS format which may
        be  quite  cryptic.   Notice  that  you  have  the  option  to
        intersperse comments  among the clauses,  but that may  not be
        supported by  your tool. Anyway  comments can be  removed from
        you Dimacs/LaTeX output.

        Arguments:
        - `comment`: an unicode string of text.

        >>> c=CNF()
        >>> c.add_comment("First clause")
        >>> c.add_clause([(True,"x"),(False,"y")])
        >>> c.add_comment("Second clause")
        >>> c.add_clause([(True,"y"),(False,"z")])
        >>> c.dimacs(add_header=False,add_comments=True)
        p cnf 3 2
        c First clause
        1 -2 0
        c Second clause
        2 -3 0
        >>> print c.dimacs(add_header=False,add_comments=False)
        p cnf 3 2
        1 -2 0
        2 -3 0
        """
        self._clauses.append(comment[:])

    def add_clause_or_comment(self, data):
        """Add a clause or a comment to the formula

        Arguments:
        - `data`: either a clause or a comment.

        >>> c=CNF()
        >>> data=["Hej",[(False,"x"),(True,"y")],"Hej da"]
        >>> for d in data: c.add_clause_or_comment(d)
        >>> c.dimacs(add_header=False)
        p cnf 2 1
        c Hej
        -1 2 0
        c Hej da
        """
        if isinstance(data,basestring):
            self.add_comment(data)
        else:
            self.add_clause(data)

    def get_variables(self):
        """Return the list of variable names
        """
        return self._variables[:]

    def get_clauses_and_comments(self):
        """Return the list of clauses
        """
        return self._clauses[:]

    def get_clauses(self):
        """Return the list of clauses
        """
        return [c for c in self._clauses if isinstance(c,self.__class__.Clause)]

    # Clauses iterator
    def __iter__(self):
        """Iterates over all clauses of the CNF
        """
        for c in self._clauses:
            if isinstance(c,self.__class__.Clause): yield c


    def __str__(self):
        return "\n".join([str(c) for c in self._clauses])+'\n'

    def dimacs(self,add_header=True,add_comments=True):
        """
        Produce the dimacs encoding of the formula
        """

        output = u""

        # Count the number of variables and clauses
        n = len(self._variables)
        m = len(self.get_clauses())

        # give numerical indexes to variables
        numidx = {}
        idx = 1
        for v in self._variables:
            numidx[v]=idx
            idx = idx + 1

        # A nice header
        if add_header:
            for s in self.header.split("\n"): output+="c {0}\n".format(s.strip())

        # Formula specification
        output += "p cnf {0} {1}\n".format(n,m)

        # We produce clauses and comments
        for c in self._clauses:

            if isinstance(c,basestring) and add_comments:
                for s in c.split("\n"): output+="c {0}\n".format(s.strip())

            elif isinstance(c,CNF.Clause):

                for neg,var in c:

                    v = numidx[var]
                    if not neg: v = -v
                    output += "{0} ".format(v)

                output+="0\n"

        # final formula
        return output.strip()

    def latex(self,add_header=True,add_comments=True):
        r"""
        Produce the LaTeX version of the formula

        >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")],
                   [(False,"x_2"),(False,"x_4")],
                   [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
        >>> print(c.latex())
        %
        % Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
        % https://github.com/MassimoLauria/cnfgen.git
        %
        \ensuremath{%
              \\left( \\neg{x_1} \\lor     {x_2} \\lor \\neg{x_3} \\right)
        \\land \\left( \\neg{x_2} \\lor \\neg{x_4} \\right)
        \\land \\left(     {x_2} \\lor     {x_3} \\lor \\neg{x_4} \\right)}
        >>> c=CNF()
        >>> print(c.latex(add_header=False))
        \ensuremath{%
           \top }
        """

        output = u""

        # A nice header
        if add_header:
            for s in self.header.split("\n"): output+="% {0}\n".format(s.strip())

        # map literals (neg,var) to latex formulas
        def map_literals(l):
            if l[0]: return "    {%s}"%l[1]
            else: return "\\neg{%s}"%l[1]


        # We produce clauses and comments
        output += "\ensuremath{%"
        empty_cnf=True

        for c in self._clauses:

            if isinstance(c,basestring) and add_comments:
                for s in c.split("\n"): output+="\n% {0}".format(s.strip())

            elif isinstance(c,CNF.Clause):

                output += "\n      " if empty_cnf else "\n\\land "
                empty_cnf = False

                # build the latex clause
                if len(c)==0:
                    output += "\\square"

                else:
                    output += "\\left( " + \
                              " \\lor ".join(map_literals(l) for l in c) + \
                              " \\right)"


        # No clause in the CNF
        if empty_cnf: output+="\n   \\top"

        # final formula
        output +=" }"
        return output.strip()



###
### Lifted CNFs
###

class Lift(CNF):
    """Lifted formula

A formula is made harder by the process of lifting.
    """

    def __init__(self, cnf):
        """Build a new CNF with by lifing the old CNF

        Arguments:
        - `cnf`: the original cnf
        """
        self._orig_cnf = cnf
        CNF.__init__(self,[],header=cnf._header)

        for c in self._orig_cnf.get_clauses_and_comments():
            if type(c)==str:
                self.add_comment(c)
            else:
                for x in self.lift_a_clause(c):
                    self.add_clause(x)




    def lift_a_literal(self, polarity, name):
        """Substitute a literal with the lifting function

        Arguments:
        - `polarity`: polarity of the literal
        - `name`:     variable to be substituted

        Returns: a list of clauses
        """
        raise NotImplementedError("Specialize this class to implement some type of lifting")


    def lift_a_clause(self, clause):
        """Substitute each variables with the lifted function

        Arguments:
        - `clause`: lifting is applied to this clause

        Returns: a list of clauses
        """
        if len(clause)==0:
            return []
        else:
            domains=[ self.lift_a_literal(n,v) for n,v in clause  ]
            domains=tuple(domains)
            return [reduce(lambda x,y: x+y,c,[])
                    for c in itertools.product(*domains)]


class IfThenElse(Lift):
    """Lifted formula: substitutes variable with a three variables
    if-then-else
    """
    def __init__(self, cnf, rank=3):
        """Build a new CNF obtained by substituting an if-then-else to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: ignored
        """
        self._rank = 3

        Lift.__init__(self,cnf)

        self._header="If-Then-Else substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a positive literal with an if then else statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        X = "{{{}}}^{x}".format(varname)
        Y = "{{{}}}^{y}".format(varname)
        Z = "{{{}}}^{z}".format(varname)

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

        total    =  self._rank
        majority = (self._rank +1) // 2

        if polarity:
            witness = self._rank // 2 + 1   # avoid strict majority of 'False'
        else:
            witness = (self._rank + 1) // 2 # avoid loose  majority of 'True'

        binom = itertools.combinations

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
        pairs = itertools.permutations(names,2)
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
        for v in cnf.get_variables():
            self.add_clause([ (True,   "Y_{{{}}}^{}".format(v,i))
                               for i in range(self._rank)])
        # Selection must be unique
        self.add_comment("Selections must be unique")
        for v in cnf.get_variables():
            for s1,s2 in itertools.combinations(["Y_{{{}}}^{}".format(v,i)
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
            for (p1,p2) in itertools.combinations(range(1,pigeons+1),2):
                yield [ (False,'p_{{{0},{1}}}'.format(p1,h)),
                        (False,'p_{{{0},{1}}}'.format(p2,h)) ]
        # Function axioms
        if functional:
            for p in xrange(1,pigeons+1):
                yield "No multiple images for pigeon {0}".format(p)
                for (h1,h2) in itertools.combinations(range(1,holes+1),2):
                    yield [ (False,'p_{{{0},{1}}}'.format(p,h1)),
                            (False,'p_{{{0},{1}}}'.format(p,h2)) ]

    php=CNF();
    php.header="{0} formula for {1} pigeons and {2} holes\n".format(formula_name,pigeons,holes) + php.header

    clauses=_PHP_clause_generator(pigeons,holes,functional,onto)
    for c in clauses:
        php.add_clause_or_comment(c)

    return php


def PebblingFormula(digraph):
    """Pebbling formula

    Arguments:
    - `digraph`: directed acyclic graph
    """
    if not networkx.algorithms.is_directed_acyclic_graph(digraph):
        raise RuntimeError("Pebbling formula is defined only for directed acyclic graphs")

    peb=CNF()

    if hasattr(digraph,'header'):
        peb.header="Pebbling formula of:\n"+digraph.header+peb.header
    else:
        peb.header="Pebbling formula\n"+peb.header

    # add clauses in topological order, to get a much readable formula
    for v in networkx.algorithms.topological_sort(digraph):

        peb.add_variable(v)

        # If predecessors are pebbled it must be pebbles
        if digraph.in_degree(v)!=0:
            peb.add_comment("Pebbling propagates on vertex {}".format(v))
        else:
            peb.add_comment("Source vertex {}".format(v))

        peb.add_clause([(False,p) for p in digraph.predecessors(v)]+[(True,v)])

        if digraph.out_degree(v)==0: #the sink
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

    if hasattr(graph,'header'):
        gop.header=name+" on graph:\n"+graph.header+gop.header
    else:
        gop.header=name+" on graph:\n"+gop.header

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
            for (v1,v2,v3) in itertools.combinations(V,3):
                gop.add_clause([ (True,'x_{{{0},{1}}}'.format(v1,v2)),
                                (True,'x_{{{0},{1}}}'.format(v2,v3)),
                                (False,'x_{{{0},{1}}}'.format(v1,v3))])
                gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True,'x_{{{0},{1}}}'.format(v1,v3))])
        else:
            for (v1,v2,v3) in itertools.permutations(V,3):
                gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True, 'x_{{{0},{1}}}'.format(v1,v3))])

    # Antisymmetry axioms (useless for 'smart' representation)
    if (not total) and (not smart):
        gop.add_comment("Relation must be anti-symmetric")
        for (v1,v2) in itertools.permutations(V,2):
            gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                            (False,'x_{{{0},{1}}}'.format(v2,v1))])

    # Antisymmetry axioms and totality (useless for 'smart' representation)
    elif total and (not smart):
        gop.add_comment("Relation must be anti-symmetric and total")
        for (v1,v2) in itertools.permutations(V,2):
            gop.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                            (False,'x_{{{0},{1}}}'.format(v2,v1))])
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

    ram.header="""
CNF encoding of the claim that there is a graph of %d vertices with no
indipendent set of size %d and no clique of size %d
""" % (s,k,N) + ram.header

    # No independent set of size s
    ram.add_comment("No independent set of size %d" % s)

    for vertex_set in itertools.combinations(xrange(1,N+1),s):
        clause=[]
        for edge in itertools.combinations(vertex_set,2):
            clause+=[(True,'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause)

    # No clique of size k
    ram.add_comment("No clique of size %d"%k)

    for vertex_set in itertools.combinations(xrange(1,N+1),k):
        clause=[]
        for edge in itertools.combinations(vertex_set,2):
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


#################################################################
#          Graph Decoders (first is default)
#################################################################
implemented_graphformats = {
    'dag':   ['dot','kth'],
    'bipartite':   ['dot','kth'],
    'digraph': ['dot','kth'],
    'simple': ['dot','kth']
    }


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

    elif format=='kth':

        D=grtype()
        D.header=''

        for l in file.readlines():

            # add the comment to the header
            if l[0]=='c':
                D.header+=l[2:]

            if ':' not in l: continue # vertex number spec

            target,sources=l.split(':')
            target=target.strip()
            sources=sources.split()
            D.add_node(target)
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

    elif format=='kth':

        G=grtype()
        G.header=''

        for l in file.readlines():

            # add the comments to the header
            if l[0]=='c':
                G.header+=l[2:]

            if ':' not in l: continue # vertex number spec

            target,sources=l.split(':')
            target=target.strip()
            sources=sources.split()
            for s in sources:
                G.add_edge(s,target)

    else:
        raise RuntimeError("Internal error, format {} not implemented".format(format))

    return G


def writeGraph(G,output_file,format,graph_type='simple',sort_dag=False):
    """Write a graph to a file

    Arguments:
    - `G`: graph object
    - `output_file`: file name or file handle to write on
    - `output_format`: graph format (e.g. dot, gml)
    - `graph_type`: one among {graph,digraph,dag,bipartite}
    - `sort_dag`: if DAG output maintaining topological order.

    Return: none.
    """
    if graph_type not in implemented_graphformats.keys():
        raise ValueError("Invalid graph type")

    if format not in implemented_graphformats[graph_type]:
        raise ValueError("Invalid format for {} graph".format(graph_type))

    if sort_dag and not networkx.algorithms.is_directed_acyclic_graph(G):
        raise ValueError("Graph must be acyclic")

    if format=='dot':

        networkx.write_dot(G,output_file)

    elif format=='kth':

        print("c {}".format(G.name))
        print("{}".format(G.order()))

        # we need numerical indices for the vertices
        if sort_dag:
            enumeration = zip( networkx.algorithms.topological_sort(G),
                               xrange(G.order()))
        else:
            enumeration = zip( G.nodes(), xrange(G.order()))

        # adj list in the same order
        indices = dict( enumeration )

        for v,i in enumeration:

            if G.is_directed():
                neighbors = [indices[w] for w in G.nodes() if v in G.adj[w] ]  # kth format inverts arcs

            else:
                neighbors = [indices[w] for w in G.adj[v].keys()]

            neighbors.sort()

            print( "{0} : ".format(i) , end="", file=output_file)
            print( " ".join([str(i) for i in neighbors]), file=output_file )

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
    for c in itertools.product(*domains):
        # Save only the clauses with the right polarity
        parity = sum(1-l[0] for l in c) % 2
        if parity != b : clauses.append(list(c))
    return clauses



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
            # vertices
            v=['v_{}'.format(i) for i in range(2*(2**args.tree)-1)]
            # edges
            for i in range(len(v)//2):
                D.add_edge(v[2*i+1],v[i])
                D.add_edge(v[2*i+2],v[i])

        elif hasattr(args,'pyramid') and args.pyramid>0:

            D=networkx.DiGraph()
            D.name='Pyramid of height {}'.format(args.pyramid)
            # vertices
            X=[ ['x_{{{},{}}}'.format(h,i) for i in range(args.pyramid-h+1) ]
                for h in range(args.pyramid+1)]
            # edges
            for h in range(1,len(X)):
                for i in range(len(X[h])):
                    D.add_edge(X[h-1][i]  ,X[h][i])
                    D.add_edge(X[h-1][i+1],X[h][i])

        elif args.inputformat:

            D=readDigraph(args.input,args.inputformat,force_dag=True)

        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(D,
                       args.savegraph,
                       args.graphformat,
                       graph_type='dag',sort_dag=True)

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

        elif args.inputformat:

            G=readGraph(args.input,args.graphformat)
        else:
            raise RuntimeError("Invalid graph specification on command line")


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
### Main program
###

if __name__ == '__main__':

    # Commands and subcommand lines
    cmdline = _GeneralCommandLine
    subcommands=[_PHP,_TSE,_OP,_GOP,_PEB,_RAM,_OR,_AND]

    # Python 2.6 does not have argparse library
    try:
        import argparse
    except ImportError:
        print("Sorry: %s requires `argparse` library, which is missing.\n"%sys.argv[0],file=sys.stderr)
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
        output=lcnf.latex(add_header=output_header,
                          add_comments=output_comments)

    elif args.output_format == 'dimacs':
        output=lcnf.dimacs(add_header=output_header,
                           add_comments=output_comments)
    else:
        output=lcnf.dimacs(add_header=output_header,
                           add_comments=output_comments)

    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()
