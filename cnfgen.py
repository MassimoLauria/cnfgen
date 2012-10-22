#!/usr/bin/env python
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
>>> c.dimacs(output_header=False)
p cnf 4 2
1 2 -3 0
-2 4 0

You can add clauses later in the process:

>>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
>>> c.dimacs(output_header=False)
p cnf 5 3
1 2 -3 0
-2 4 0
-3 4 -5 0

`cnfgen` module contains a lot of prepackaged CNF generator

>>>
"""

from __future__ import print_function
import itertools

_default_header="""
Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""

class CNF(object):
    """Propositional formulas in conjunctive normal form.
    """

    def __init__(self, clauses_and_comments=[],header=None):
        """Propositional formulas in conjunctive normal form.

        To add commented clauses use the `add_clause` and
        `add_comment` methods.

        Arguments:
        - `clauses`: ordered list of clauses; a clause with k literals
                     is a tuple with 2k position. Odd ones are the
                     polarities, even one are utf8 encoded string with
                     variable names.

                     E.g. (not x3) or x4 or (not x2) is encoded as (False,u"x3",True,u"x4",False,u"x2")
        - `header`: a preamble which documents the formula
        """
        self._clauses = []
        self._name_to_id = {}
        self._id_to_name = {}
        if header:
            self._header=header
        else:
            self._header=_default_header

        for c in clauses_and_comments:
            self.add_clause_or_comment(c)

    def _set_header(self, value):
        self._header = value

    def _get_header(self):
        return self._header

    header = property(_get_header, _set_header)

    def add_clause(self,clause):
        """Add a well formatted clause to the CNF. It raises
           `ValueError` if the clause is not well formatted.

        Arguments:
        - `clause`: a clause with k literals is a list with k pairs.
                    First coords are the polarities, second coords are
                    utf8 encoded strings with variable names.

                    E.g. (not x3) or x4 or (not x2) is encoded as
                         [(False,u"x3"),(True,u"x4"),(False,u"x2")]
        """
        new_clause=[]
        # Check for the format
        for neg,var in clause:
            if type(neg)!=bool or type(var) != str:
                raise TypeError("%s is not a well formatted clause" %clause)
            new_clause.append((neg,var))
        # Add all missing variables
        for _,var in new_clause:
            if not var in self._name_to_id:
                id=len(self._name_to_id)+1
                self._name_to_id[var]=id
                self._id_to_name[id]=var
        # Add the clause
        self._clauses.append(new_clause)

    def add_variable(self,var):
        """Add a variable to the formula. This is useful to add
        the variable in a nice order than the appearence one.

        Arguments:
        - `var`: the name of the variable to add (string).
        """
        if type(var) != str:
            raise TypeError("The name of a variable must be a string" %clause)

        if not var in self._name_to_id:
            id=len(self._name_to_id)+1
            self._name_to_id[var]=id
            self._id_to_name[id]=var

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
        >>> c.dimacs(output_header=False,output_comments=True)
        p cnf 3 2
        c First clause
        1 -2 0
        c Second clause
        2 -3 0
        >>> c.dimacs(output_header=False,output_comments=False)
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
        >>> c.dimacs(output_header=False)
        p cnf 2 1
        c Hej
        -1 2 0
        c Hej da
        """
        if type(data)==str:
            self.add_comment(data)
        else:
            self.add_clause(data)



    def dimacs(self,outputfile=None,output_header=True,output_comments=True):
        """
        Produce the dimacs encoding of the formula
        """

        # Count the number of variables and clauses
        n = len(self._name_to_id)
        m = len([c for c in self._clauses if type(c)!=str])

        # A nice header
        if output_header:
            for s in self.header.split("\n"): print(u"c "+s)

        # Formula specification
        print(u"p cnf {0} {1}".format(n,m))

        # We produce clauses and comments
        for c in self._clauses:
            if type(c)==str:
                if output_comments: print(u"c "+c)
            else:
                for neg,var in c:
                    v = self._name_to_id[var]
                    if not neg: v = -v
                    print(u"{0} ".format(v),end="")
                print(u"0")

    def latex(self,outputfile=None,output_header=True,output_comments=True):
        """
        Produce the LaTeX version of the formula

        >>> c=CNF([[(True,"x_1"),(False,"x_2"),(True,"x_3")], \
                   [(True,"x_2"),(True,"x_4")], \
                   [(False,"x_2"),(False,"x_3"),(True,"x_4")]])
        >>> c.latex()
        %
        % Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
        % https://github.com/MassimoLauria/cnfgen.git
        %
        \ensuremath{%
              \\left( \\neg{x_1} \\lor     {x_2} \\lor \\neg{x_3} \\right)
        \\land \\left( \\neg{x_2} \\lor \\neg{x_4} \\right)
        \\land \\left(     {x_2} \\lor     {x_3} \\lor \\neg{x_4} \\right)}
        >>> c=CNF()
        >>> c.latex(output_header=False)
        \ensuremath{\square}
        """

        # A nice header
        if output_header:
            for s in self.header.split("\n"): print((u"% "+s).strip())

        # We produce clauses and comments
        if len(self._clauses)==0:
            print("\\ensuremath{\\square}")
            return

        # map literals (neg,var) to latex formulas
        def map_literals(l):
            if l[0]: return "\\neg{%s}"%l[1]
            else: return "    {%s}"%l[1]

        print("\ensuremath{%",end="")
        first_clause=True

        for c in self._clauses:
            if type(c)==str:
                if output_comments: print((u"% "+c).strip())
            else:
                if first_clause: print("\n      ",end="")
                else: print("\n\\land ",end="")
                # build the latex clause
                print("\\left( " + \
                      " \\lor ".join(map(map_literals,c)) + \
                      " \\right)",end="")
                first_clause=False
        print("}")


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

    >>> PigeonholePrinciple(4,3).dimacs(output_header=False,output_comments=True)
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



def OrderingPrinciple(size,total=False):
    """Generates the clauses of ordering principle

    Arguments:
    - `size`:   numer of elements
    - `total`:  add clauses to enforce totality
    """
    gt=CNF()
    # Describe the formula
    if total:
        gt.header="Total ordering principle on domain of size %s\n"%size+gt.header
    else:
        gt.header="Ordering principle on domain of size %s\n"%size+gt.header

    # Non minimality axioms
    gt.add_comment("Each vertex has a predecessor")
    for v in xrange(size):
        clause = []
        for u in xrange(v):
            clause += [(True,'x_{{{0},{1}}}'.format(u,v))]
        for w in xrange(v+1,size):
            if total:
                clause += [(False,'x_{{{0},{1}}}'.format(v,w))]
            else:
                clause += [(True,'x_{{{0},{1}}}'.format(w,v))]
        gt.add_clause(clause)

    # Transitivity axiom
    gt.add_comment("Relation must be transitive")

    if size>=3:
        if total:
            # Optimized version if totality is included (less formulas)
            for (v1,v2,v3) in itertools.combinations(xrange(size),3):
                gt.add_clause([ (True,'x_{{{0},{1}}}'.format(v1,v2)),
                                (True,'x_{{{0},{1}}}'.format(v2,v3)),
                                (False,'x_{{{0},{1}}}'.format(v1,v3))])
                gt.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True,'x_{{{0},{1}}}'.format(v1,v3))])
        else:
            for (v1,v2,v3) in itertools.permutations(xrange(size),3):
                gt.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                                (False,'x_{{{0},{1}}}'.format(v2,v3)),
                                (True, 'x_{{{0},{1}}}'.format(v1,v3))])

    # Antisymmetry axioms
    if not total:
        gt.add_comment("Relation must be anti-symmetric")
        for (v1,v2) in itertools.permutations(xrange(size),2):
            gt.add_clause([ (False,'x_{{{0},{1}}}'.format(v1,v2)),
                            (False,'x_{{{0},{1}}}'.format(v2,v1))])

    return gt

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

class _Graph(object):
    """Simple graph class for internal representation.
    """

    def __init__(self, V,E):
        """
        Build the graph for a set of vertices and edges. If the
        list of edges names some vertex which is not in the list V, it
        is appended to the list. In particular the list is given for
        adding isolated vertices or to enforce some order.

        Arguments:
        - `V`: initial list of vertices
        - `E`: edges of the graph.
        """
        self._V = V
        self._E = []
        # Sanitize edge list
        for (u,v) in E:
            if (u,v) in self._E: pass
            if (v,u) in self._E: pass
            if not u in V: V.append(u)
            if not v in V: V.append(v)

    def _get_edges(self):
        return self._E

    edges = property(_get_edges)

    def _get_vertices(self):
        return self._vertices

    vertices = property(_get_vertices)




if __name__ == '__main__':
    # Parse the command line arguments

    # Select the appropriate generator

    # Output the formula
    c=CNF(RAM(4,3,8))
    c.dimacs()
