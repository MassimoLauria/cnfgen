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
import sys
import itertools


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
                     is a tuple with 2k position. Odd ones are the
                     polarities, even one are utf8 encoded string with
                     variable names.

                     E.g. (not x3) or x4 or (not x2) is encoded as (False,u"x3",True,u"x4",False,u"x2")
        - `header`: a preamble which documents the formula
        """
        self._clauses = []
        self._name_to_id = {}
        self._id_to_name = {}

        self._header = header or _default_header

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
            raise TypeError("The name of a variable must be a string")

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

    def get_variables(self):
        """Return the list of variable names
        """
        return self._name_to_id.keys()[:]

    def get_clauses_and_comments(self):
        """Return the list of clauses
        """
        return self._clauses[:]

    def get_clauses(self):
        """Return the list of clauses
        """
        return [c for c in self._clauses if type(c)!=str]




    def dimacs(self,output_file=sys.stdout,output_header=True,output_comments=True):
        """
        Produce the dimacs encoding of the formula
        """
        # Count the number of variables and clauses
        n = len(self._name_to_id)
        m = len([c for c in self._clauses if type(c)!=str])

        # A nice header
        if output_header:
            for s in self.header.split("\n"): print(u"c "+s,file=output_file)

        # Formula specification
        print(u"p cnf {0} {1}".format(n,m),file=output_file)

        # We produce clauses and comments
        for c in self._clauses:
            if type(c)==str:
                if output_comments: print(u"c "+c,file=output_file)
            else:
                for neg,var in c:
                    v = self._name_to_id[var]
                    if not neg: v = -v
                    print(u"{0} ".format(v),end="",file=output_file)
                print(u"0",file=output_file)

    def latex(self,output_file=sys.stdout,output_header=True,output_comments=True):
        r"""
        Produce the LaTeX version of the formula

        >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")], \
                   [(False,"x_2"),(False,"x_4")], \
                   [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
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
            for s in self.header.split("\n"): print((u"% "+s).strip(),file=output_file)

        # We produce clauses and comments
        if len(self._clauses)==0:
            print("\\ensuremath{\\square}",file=output_file)
            return

        # map literals (neg,var) to latex formulas
        def map_literals(l):
            if l[0]: return "    {%s}"%l[1]
            else: return "\\neg{%s}"%l[1]

        print(r"\ensuremath{%",end="",file=output_file)
        first_clause=True

        for c in self._clauses:
            if type(c)==str:
                if output_comments:
                    print('\n',file=output_file)
                    print((u"% {}".format(c)).strip(),end='',file=output_file)
            else:
                if first_clause: print("\n      ",end="",file=output_file)
                else: print("\n\\land ",end="",file=output_file)
                # build the latex clause
                print("\\left( " + \
                      " \\lor ".join(map(map_literals,c)) + \
                      " \\right)",end="",file=output_file)
                first_clause=False
        print(" }",file=output_file)

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
        CNF.__init__(self)

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
        raise ImplementationError("Specialize this class to implement some type of lifting")


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

class InnerXor(Lift):
    """Lifted formula: substitutes variable with a XOR
    """
    name='xor'
    description='substitute variables with xors'

    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a XOR to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="XOR {} substituted formula\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a literal with a (negated) XOR

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        domains=[]
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        domains = tuple([ ((True,name),(False,name)) for name in names] )
        clauses=[]
        for c in itertools.product(*domains):
            # Save only the clauses with the right polarity
            parity = sum(l[0] for l in c) % 2
            if parity ^ polarity : clauses.append(list(c))
        return clauses

class Selection(Lift):
    """Lifted formula: Y variable select X values
    """
    name='select'
    description='substitute variables V[i] with X[i][Y[i]]'

    def __init__(self, cnf, rank):
        """Build a new CNF obtained by lifting procedures

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        # Add additional clauses to realize the lifting
        for v in cnf.get_variables():
            self.add_clause([ (False,   "Y_{{{}}}^{}".format(v,i))
                               for i in range(self._rank)])

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
    def build_cnf(args):
        pass

    @staticmethod
    def additional_options_check(args):
        pass


class _GeneralCommandLine(_CMDLineHelper)
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
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--verbose', '-v',action='store_const',default=1,const=2,
                       help="""Add comments inside the formula. It may
                            not be supported by very old sat solvers.
                            """)
        g.add_argument('--quiet', '-q',action='store_const',const=0,dest='verbose',
                       help="""Output just the formula with not header
                            or comment.""")


class _GraphInputHelper(_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """
        gr=parser.add_argument_group("Reading graph from input")
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The graph is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
        gr.add_argument('--input-format','-if',
                        choices=['dimacs','graph6','sparse6',],
                        default='dimacs',
                        help="""
                        Format of the graph in input, several formats are
                        supported in networkx is installed.  (default:
                        dimacs)
                        """)


class _PHP(_CMDLineHelper):
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


class _RAM(_CMDLineHelper):
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


class _OP(_CMDLineHelper):
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
        parser.add_argument('--total','-t',action='store_true',help="assume a total order")

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return OrderingPrinciple(args.N,args.total)


###
### Main program
###

if __name__ == '__main__':

    # Commands and subcommand lines
    cmdline = _GeneralCommandLine
    subcommands=[_PHP,_RAM,_OP]

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

    # Generate the basic formula
    cnf=args.subcommand.build_cnf(args)

    # Do we wnat comments or not
    output_comments=args.verbose >= 2
    output_header  =args.verbose >= 1

    if args.output_format == 'latex':
        cnf.latex(output_file=args.output,
                  output_header=output_header,
                  output_comments=output_comments)
    elif args.output_format == 'dimacs':
        cnf.dimacs(output_file=args.output,
                  output_header=output_header,
                  output_comments=output_comments)
    else:
        cnf.dimacs(output_file=args.output,
                  output_header=output_header,
                  output_comments=output_comments)

    if args.output!=sys.stdout:
        args.output.close()
