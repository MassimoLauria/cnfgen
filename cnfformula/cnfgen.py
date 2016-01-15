#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Create the CNFs:

>>> from . import CNF
>>> c=CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], \
          [(False,"x2"),(True,"x4")] ])
>>> print( c.dimacs(export_header=False) )
p cnf 4 2
1 2 -3 0
-2 4 0

You can add clauses later in the process:

>>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
>>> print( c.dimacs(export_header=False))
p cnf 5 3
1 2 -3 0
-2 4 0
-3 4 -5 0

"""

from __future__ import print_function

import os
import sys
import random

from . import TransformFormula,available_transform

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

###
### Explore the cnfformula.families modules to find formula implementations
###

def find_formula_subcommands():
    """Look in cnfformula.families package for implementations of CNFs"""

    
    import pkgutil
    from .        import families
    from .cmdline import is_cnfgen_subcommand

    result = []
    
    for loader, module_name, _ in  pkgutil.walk_packages(families.__path__):
        module_name = families.__name__+"."+module_name
        module = loader.find_module(module_name).load_module(module_name)
        for objname in dir(module):
            obj = getattr(module, objname)
            if is_cnfgen_subcommand(obj):
                result.append(obj)
    result.sort(key=lambda x: x.name)
    return result



###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT,signal_handler)

###
### Main program
###
def command_line_utility(argv=sys.argv):
    """CNFgen main command line interface

    This function provide the main interface to CNFgen. It sets up the
    command line, parses the command line arguments, builds the
    appropriate formula and outputs its representation.
    
    It **must not** raise exceptions, but fail with error messages for
    the user.

    Parameters
    ----------
    argv: list, optional
        The list of token with the command line arguments/options.
    """

    # Main command line setup
    parser=argparse.ArgumentParser(prog=os.path.basename(argv[0]),
                                   epilog="""
    Each <formula type> has its own command line arguments and options.
    For more information type 'cnfgen <formula type> [--help | -h ]'
    """)
    setup_command_line_args(parser)

    # Sub command lines setup 
    subparsers=parser.add_subparsers(title="Available formula types",metavar='<formula type>')
    for sc in find_formula_subcommands():
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(subcommand=sc)

    # Process the options
    args=parser.parse_args(argv[1:])

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    # Generate the formula
    try:
        cnf = args.subcommand.build_cnf(args)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(os.EX_DATAERR)
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
        if hasattr(args.subcommand,"docstring"):
            cmdline_descr += \
                             "\\noindent\\textbf{Docstring:}\n" +\
                             "\\begin{lstlisting}[breaklines,basicstyle=\\small]\n" +\
                             args.subcommand.docstring+ \
                             "\\end{lstlisting}\n"
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
