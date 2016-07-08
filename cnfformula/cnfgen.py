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


    # Formula generators cmdline setup 
    import families
    import transformations
    from .cmdline import is_cnfgen_subcommand
    from .cmdline import is_cnf_transformation_subcommand
    from .cmdline import find_methods_in_package

    
    # Cmdline parser for formula transformations
    t_parser = argparse.ArgumentParser(usage=os.path.basename(argv[0]) + " ..."
                                       +" [-T <transformation> <params> -T <transformation> <params> ...]",
                                       epilog="""Each <transformation> has its own command line arguments and options.
                                       For more information type 'cnfgen ... -T <transformation> [--help | -h]'

                                       """)
    
    t_subparsers = t_parser.add_subparsers(title="Available formula transformation",
                                           metavar="<transformation>")
    for sc in find_methods_in_package(transformations,
                                      is_cnf_transformation_subcommand,
                                      sortkey=lambda x:x.name):
        p=t_subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(transformation=sc)
    
    # Main cmdline setup
    parser=argparse.ArgumentParser(prog=os.path.basename(argv[0]),
                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                   epilog=
"""Each <formula type> has its own command line arguments and options.
For more information type 'cnfgen <formula type> [--help | -h ]'.
Furthermore it is possible to postprocess the formula by applying
a sequence of transformations.

"""+t_parser.format_help())
    

    setup_command_line_args(parser)
    
        
    
    subparsers=parser.add_subparsers(title="Available formula types",metavar='<formula type>')
    for sc in find_methods_in_package(families,
                                      is_cnfgen_subcommand,
                                      sortkey=lambda x:x.name):
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(generator=sc)

   
        
    # Split the command line into formula generation and transformation
    # applications
    def splitlist(L,key):
        argbuffer=[]
        for e in L:
            if e == key:
                yield argbuffer
                argbuffer = []
            else:
                argbuffer.append(e)
        yield argbuffer

    cmd_chunks = list(splitlist(argv,"-T"))
    generator_cmd = cmd_chunks[0][1:]
    transformation_cmds = cmd_chunks[1:]
    
    # Parse the various component of the command line
    args=parser.parse_args(generator_cmd)
    t_args=[]
    for cmd in transformation_cmds:
        t_args.append(t_parser.parse_args(cmd))

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    # Generate the formula
    try:
        cnf = args.generator.build_cnf(args)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(os.EX_DATAERR)


    # Apply the sequence of transformations
    for argdict in t_args:
        cnf = argdict.transformation.transform_cnf(cnf,argdict)
        
    # Output
    if args.output_format == 'latex':
        cmdline_descr="\\noindent\\textbf{Command line:}\n" + \
            "\\begin{lstlisting}[breaklines]\n" + \
            "$ cnfgen " + " ".join(argv[1:]) + "\n" + \
            "\\end{lstlisting}\n"
        if hasattr(args.generator,"docstring"):
            cmdline_descr += \
                             "\\noindent\\textbf{Docstring:}\n" +\
                             "\\begin{lstlisting}[breaklines,basicstyle=\\small]\n" +\
                             args.generator.docstring+ \
                             "\\end{lstlisting}\n"
        output = cnf.latex(export_header=args.verbose,
                            full_document=True,extra_text=cmdline_descr)
        
    elif args.output_format == 'dimacs':
        output = cnf.dimacs(export_header=args.verbose)

    else:
        output = cnf.dimacs(export_header=args.verbose)

    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
