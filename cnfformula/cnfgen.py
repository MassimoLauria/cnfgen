#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git


Create you own CNFs:

>>> from . import CNF
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

from __future__ import print_function

import os

from . import CNF
from . import TransformFormula,available_transform

from .cmdline import DirectedAcyclicGraphHelper
from .cmdline import SimpleGraphHelper
from .cmdline import BipartiteGraphHelper
from .cmdline import is_formula_cmdhelper

from .families import *



import sys

from itertools import combinations

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

import random

try:
    import networkx
    import networkx.algorithms
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",file=sys.stderr)
    exit(-1)

#################################################################
#          Command line tool follows
#################################################################


class HelpTransformAction(argparse.Action):
    def __init__(self, **kwargs):
        super(HelpTransformAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        print("""
        Formula transformations available
        """)
        for k,entry in available_transform().iteritems():
            print("{}\t:  {}".format(k,entry[0]))
        print("\n")
        sys.exit(0)

###
### Command line helpers
###
def setup_command_line_args(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
    parser.add_argument('--output','-o',
                        type=argparse.FileType('wb',0),
                        metavar="<output>",
                        default='-',
                        help="""Save the formula to <output>. Setting '<output>' to '-' sends the
                        formula to standard output. (default: -)
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
                        program. (default: current time)
                        """)
    g=parser.add_mutually_exclusive_group()
    g.add_argument('--verbose', '-v',action='store_true',default=True,
                   help="""Output formula header and comments.""")
    g.add_argument('--quiet', '-q',action='store_false',dest='verbose',
                   help="""Output just the formula with no header.""")
    parser.add_argument('--Transform','-T',
                        metavar="<transformation method>",
                        choices=available_transform().keys(),
                        default='none',
                        help="""
                        Transform the CNF formula to make it harder.
                        See `--help-transform` for more information
                        """)
    parser.add_argument('--Tarity','-Ta',
                        metavar="<transformation arity>",
                        type=int,
                        default=None,
                        help="""
                        Hardness parameter for the transformation procedure.
                        See `--help-transform` for more informations
                        """)
    parser.add_argument('--help-transform',nargs=0,action=HelpTransformAction,help="""
                         Formula can be made harder applying some
                         so called "transformation procedures".
                         This gives information about the implemented transformation.
                         """)



    
### Formula families
    
class _SSC:
    name='subsetcard'
    description='subset cardinality formulas'

    @staticmethod
    def setup_command_line(parser):
        BipartiteGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        B = BipartiteGraphHelper.obtain_graph(args)
        return SubsetCardinalityFormula(B)

    
class _MARKSTROM:
    name='markstrom'
    description='markstrom formulas'

    @staticmethod
    def setup_command_line(parser):
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        G = SimpleGraphHelper.obtain_graph(args) 
        return MarkstromFormula(G)

    

class _RAM:
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


class _OP:
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
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return OrderingPrinciple(args.N,args.total,args.smart,args.plant,args.knuth)


class _GOP:
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
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G= SimpleGraphHelper.obtain_graph(args)
        return GraphOrderingPrinciple(G,args.total,args.smart,args.plant,args.knuth)


class _PARITY:
    """Command line helper for Matching Principle formulas
    """
    name='parity'
    description='parity principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Parity Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")

    @staticmethod
    def build_cnf(args):
        return ParityPrinciple(args.N)


class _PMATCH:
    """Command line helper for Perfect Matching Principle formulas
    """
    name='matching'
    description='perfect matching principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Perfect Matching Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        G = SimpleGraphHelper.obtain_graph(args)
        return PerfectMatchingPrinciple(G)


class _COUNT:
    """Command line helper for Counting Principle formulas
    """
    name='count'
    description='counting principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Counting Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('M',metavar='<M>',type=int,help="domain size")
        parser.add_argument('p',metavar='<p>',type=int,help="size of the parts")

    @staticmethod
    def build_cnf(args):
        """Build an Counting Principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CountingPrinciple(args.M,args.p)

    
class _KClique:
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
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k)])


class _KColor:
    """Command line helper for k-color formula
    """
    name='kcolor'
    description='k-colorability formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-color formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="number of available colors")
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-colorability formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return ColoringFormula(G,range(1,args.k+1))


class _GAuto:
    """Command line helper for Graph Automorphism formula
    """
    name='gauto'
    description='graph automorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph automorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return GraphAutomorphism(G)



class _GIso:
    """Command line helper for Graph Isomorphism formula
    """
    name='giso'
    description='graph isomorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser,suffix="1",required=True)
        SimpleGraphHelper.setup_command_line(parser,suffix="2",required=True)


    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G1 = SimpleGraphHelper.obtain_graph(args,suffix="1")
        G2 = SimpleGraphHelper.obtain_graph(args,suffix="2")
        return GraphIsomorphism(G1,G2)


    
class _RAMLB:
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
        parser.add_argument('k',metavar='<k>',type=int,
                            action='store',help="size of the clique to be found")
        parser.add_argument('s',metavar='<s>',type=int,
                            action='store',help="size of the stable to be found")
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k),
                                  networkx.complete_graph(args.s)])



class _TSE:
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
        SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)

        if G.order()<1:
            charge=None

        elif args.charge=='first':

            charge=[1]+[0]*(G.order()-1)

        else: # random vector
            charge=[random.randint(0,1) for _ in xrange(G.order()-1)]

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



class _RANDOM:
    """Command line helper for random formulas
    """
    name='randkcnf'
    description='random k-CNF'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,help="clause width")
        parser.add_argument('n',metavar='<n>',type=int,help="number of variables")
        parser.add_argument('m',metavar='<m>',type=int,help="number of clauses")

    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        return RandomKCNF(args.k,args.n,args.m)


class _PEB:
    """Command line helper for pebbling formulas
    """
    name='peb'
    description='pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        try:
            return PebblingFormula(D)
        except ValueError:
            print("\nError: input graph must be directed and acyclic.",file=sys.stderr)
            sys.exit(-1)

class _Stone:
    """Command line helper for stone formulas
    """
    name='stone'
    description='stone formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        DirectedAcyclicGraphHelper.setup_command_line(parser)
        parser.add_argument('s',metavar='<s>',type=int,help="number of stones")

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        try:
            return StoneFormula(D,args.s)
        except ValueError:
            print("\nError: Input graph must be a DAG, and a non negative # of stones.",file=sys.stderr)
            sys.exit(-1)
            



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
def command_line_utility(argv=sys.argv):
    """CNFgen main command line interface

    This function provide the main interface to CNFgen. It sets up the
    command line, parses the command line arguments, builds the
    appropriate formula and outputs its representation.
    
    It **must not** raise exceptions.

    Parameters
    ----------
    argv: list, optional
        The list of token with the command line arguments/options.

    """

    # Commands and subcommand lines
    subcommands=[_TSE,
                 _OP,_GOP,
                 _KClique,
                 _KColor,
                 _RANDOM,
                 _PARITY,_PMATCH,
                 _COUNT,
                 _PEB,
                 _Stone,
                 _GIso,_GAuto,
                 _RAM,_RAMLB,
                 _MARKSTROM,
                 _SSC]

    # Collect formula families
    import pkgutil
    import cnfformula.families

    for loader, module_name, _ in  pkgutil.walk_packages(cnfformula.families.__path__):
        module_name = cnfformula.families.__name__+"."+module_name
        module = loader.find_module(module_name).load_module(module_name)
        for objname in dir(module):
            obj = getattr(module, objname)
            if is_formula_cmdhelper(obj):
                subcommands.append(obj)
    subcommands.sort(key=lambda x: x.name)
    del pkgutil,cnfformula.families

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog=os.path.basename(argv[0]),
                                   epilog="""
    Each <formula type> has its own command line arguments and options.
    For more information type 'cnfgen <formula type> [--help | -h ]'
    """)
    setup_command_line_args(parser)
    subparsers=parser.add_subparsers(title="Available formula types",metavar='<formula type>')

    # Setup of various formula command lines options
    for sc in subcommands:
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(subcommand=sc)

    # Process the options
    args=parser.parse_args(argv[1:])

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    # Generate the formula
    cnf=args.subcommand.build_cnf(args)
    if args.Transform == 'none':
        tcnf = cnf
    else:
        tcnf = TransformFormula(cnf,args.Transform,args.Tarity)
        
    # Output
    if args.output_format == 'latex':
        cmdline_descr="\\noindent\\textbf{Command line:}\n" + \
            "\\begin{lstlisting}[breaklines]\n" + \
            "$ cnfgen " + " ".join(argv[1:]) + "\n" + \
            "\\end{lstlisting}\n"
        # "\\noindent\\textbf{Docstring:}\n" +
        # "\\begin{lstlisting}[breaklines,basicstyle=\\small]\n" +
        # StoneFormula.__doc__ +
        # "\\end{lstlisting}\n"
        output = tcnf.latex(export_header=args.verbose,
                            full_document=True,extra_text=cmdline_descr)
        
    elif args.output_format == 'dimacs':
        output = tcnf.dimacs(export_header=args.verbose)

    else:
        output = tcnf.dimacs(export_header=args.verbose)

    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
