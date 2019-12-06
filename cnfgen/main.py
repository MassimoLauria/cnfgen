#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Create the CNFs:

>>> from cnfformula import CNF
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

import os
import sys
import random
import argparse
import io

from cnfformula.prjdata import __version__

from .cmdline import paginate_or_redirect_stdout
from .cmdline import setup_SIGINT

from .cmdline import get_formula_helpers
from .cmdline import get_transformation_helpers

from .msg import interactive_msg
from .msg import error_msg
from .msg import msg_prefix

#################################################################
#          Command line tool follows
#################################################################


# Help strings
usage_string = """{} [-h] [-V] [--output <output>]
                 [--output-format {{latex,dimacs}}] [--seed <seed>]
                 [--verbose | --quiet] [--tutorial]
                 <formula> <args> ...
                 [-T <transformation> <args>]
                 [-T <transformation> <args>]
                 ..."""

tutorial_string = """
-------------------------- TUTORIAL --------------------------------- 
{0} builds CNF formulas mostly coming from proof complexity
literature, to use as benchmark against SAT solvers. Basic usage is

    {0} <formula> <arg1> <arg2> ...

which builds a CNF from family <formula> with various parameters.
For example a Pigeonhole principle formula from 5 to 4 pigeons can be
build with command line

    {0} php 5 4

Various transformations can be applied to the generated formula, one
after the other. For example.

    {0} php 5 4 -T shuffle -T xor 3

Create a pigeonhole principle formula first, then applies the
'shuffle' transformation and finally the 'xor' transformation with
parameter 3.

Some formulas are built on top of graph structures, passed as input
files or randomly generated. The command lines

    {0} tseitin -i graph.dot
    {0} tseitin --gnd 10 4

build Tseitin formulas, respectively, over a graph passed as a DOT
file, and over a random 4-regular graph of 10 vertices.

For the full list of formulas and formula transformations type one of

    {0} -h
    {0} --help

For the help of a specific CNF family named <formula> type one of

    {0} <formula> -h
    {0} <formula> --help 

For the help of a specific formula transformation pick any CNF family
<formula> and type one of 

    {0} <formula> <args> -T <transformation> -h
    {0} <formula> <args> -T <transformation> --help

where <transformation> is the name of the formula transformation to
get the help for.
----------------------------  END ----------------------------------
"""


def setup_command_line_parsers(progname, fhelpers, thelpers):
    """Create the parser for formula and transformation arguments.

    General options
    - query version
    - verbosity/silence
    - outputfile
    - outputformat
    - random seed

    Formula options via subcommands
    - one for each formula helper

    Parameters:
    -----------
    progname:
        the name of the program
    fhelpers:
        the cmdline helpers for the formulas
    thelpers:
        the cmdline helpers for the transformations

    Return:
    -------
    two parsers, one for formula commands and one for transformation commands.
    """

    # First we setup the parser for transformation command lines
    t_parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    t_subparsers = t_parser.add_subparsers(
        prog=progname + " <formula> <args> -T",
        title="Available formula transformation",
        metavar="<transformation>")
    for sc in thelpers:
        p = t_subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(transformation=sc)

    # now we setup the main parser for the formula generation command
    parser = argparse.ArgumentParser(
        prog=progname,
        usage=usage_string.format(progname),
        description=tutorial_string.format(progname),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    class PrintTutorial(argparse.Action):
        def __call__(self, parser, args, values, option_string = None):
            with paginate_or_redirect_stdout(sys.stdout):
                print(tutorial_string.format(progname))
            sys.exit(os.EX_OK)

    parser.add_argument('-V', '--version',
                        action='version',
                        version="%(prog)s ("+__version__+")")
    parser.add_argument('--tutorial',
                        nargs=0,
                        action=PrintTutorial)
    parser.add_argument('--output', '-o',
                        type=argparse.FileType('w', encoding='utf-8'),
                        metavar="<output>",
                        default='-',
                        help="""Save the formula to <output>. Setting '<output>' to '-' sends the
                        formula to standard output. (default: -)
                        """)
    parser.add_argument('--output-format', '-of',
                        choices=['latex', 'dimacs'],
                        default='dimacs',
                        help="""
                        Output format of the formulas. 'latex' is
                        convenient to insert formulas into papers, and
                        'dimacs' is the format used by sat solvers.
                        (default: dimacs)
                        """)

    parser.add_argument('--seed', '-S',
                        metavar="<seed>",
                        default=None,
                        type=str,
                        action='store',
                        help="""Seed for any random process in the
                        program. (default: current time)
                        """)
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--verbose', '-v', action='store_true', default=True,
                   help="""Output formula header and comments.""")
    g.add_argument('--quiet', '-q', action='store_false', dest='verbose',
                   help="""Output just the formula with no header.""")

    # setup each formula command parser
    subparsers = parser.add_subparsers(prog=progname,
                                       title="Available formula types",
                                       metavar='<formula>')
    for sc in fhelpers:
        p = subparsers.add_parser(sc.name,
                                  help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(generator=sc)

    # Attach the list of available transformations
    # but without usage string
    extension = t_parser.format_help().splitlines()
    extension = "\n".join(extension[2:])
    parser.epilog = extension

    return parser, t_parser


def build_latex_cmdline_description(argv, args, t_args):
    """Build the latex documentation of the components of the formula.

    Insert additonal latex documentation of the formula. For example
    it includes the input files used to build it.

    Parameters
    ----------
    argv : list(str) 
        arguments on command line
    args:
        parsed arguments for the formula
    t_args: list
        group of parsed arguments for the transformations

    """
    # The full command line 
    cmdline_descr=["\\noindent\\textbf{Command line:}",
                   "\\begin{lstlisting}[breaklines]",
                   "$ cnfgen " + " ".join(argv[1:]),
                   "\\end{lstlisting}"]

    # The docstring of the formula family generator
    if hasattr(args.generator, "docstring"):
        cmdline_descr += ["\\noindent\\textbf{Docstring:}",
                          "\\begin{lstlisting}[breaklines,basicstyle=\\small]",
                          args.generator.docstring,
                          "\\end{lstlisting}"]

    # Find input files specified in the command line
    input_files = []
    for l in [args] + t_args:
        data = iter(vars(l).items())
        data = [v for k, v in data if not k.startswith("_")]
        data = [f for f in data if isinstance(f, io.IOBase)]
        data = [f for f in data if (f != sys.stdin) and f.mode == 'r']
        input_files.extend(data)

    # Add them all to the latex document
    for f in input_files:
        f.seek(0, 0)
        cmdline_descr += ["\\noindent\\textbf{Input file} \\verb|%s|" % f.name,
                          "\\begin{lstlisting}[breaklines,basicstyle=\\small]",
                          f.read(),
                          "\\end{lstlisting}"]

    # Return all as a single string
    cmdline_descr += ['\n']
    return "\n".join(cmdline_descr)


# Main program
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

    formula_helpers = get_formula_helpers()
    transformation_helpers = get_transformation_helpers()

    parser, t_parser = setup_command_line_parsers(
        os.path.basename(argv[0]),
        formula_helpers,
        transformation_helpers)

    # Split the command line into formula generation and transformation
    # applications
    def splitlist(L, key):
        argbuffer = []
        for e in L:
            if e == key:
                yield argbuffer
                argbuffer = []
            else:
                argbuffer.append(e)
        yield argbuffer

    cmd_chunks = list(splitlist(argv, "-T"))
    generator_cmd = cmd_chunks[0][1:]
    transformation_cmds = cmd_chunks[1:]

    # Parse the various component of the command line
    args = parser.parse_args(generator_cmd)
    t_args = []
    for cmd in transformation_cmds:
        t_args.append(t_parser.parse_args(cmd))

    # If necessary, init the random generator
    if hasattr(args, 'seed') and args.seed:
        random.seed(args.seed)

    # Comment character useful for error reporting
    if args.output_format == 'latex':
        cprefix = '% '
    elif args.output_format == 'dimacs':
        cprefix = 'c '
    else:
        raise RuntimeError("INTERNAL ERROR: output format must always be defined.")
        
        
    # Check arguments
    if not hasattr(args, 'generator'):
        with msg_prefix(cprefix+"ERROR: "):
            error_msg("You did not tell which formula you wanted to generate.",
                      filltext=70)
            error_msg(parser.format_usage().rstrip())
            error_msg("See '{0} -h' or '{0} --help' for more info.".format(os.path.basename(argv[0])),
                      filltext=70)
            sys.exit(os.EX_DATAERR)

    for argdict in t_args:
        if not hasattr(argdict, 'transformation'):
            with msg_prefix(cprefix+"ERROR: "):
                error_msg("You used option '-T' but did not pick a transformation.",
                          filltext=70)
                error_msg(parser.format_usage().rstrip())
                error_msg("See '{0} -h' or '{0} --help' for more info.".format(os.path.basename(argv[0])),
                          filltext=70)
            sys.exit(os.EX_DATAERR)

    # Generate the formula and apply transformations
    with msg_prefix(cprefix):
        try:

            cnf = args.generator.build_cnf(args)

            for argdict in t_args:
                cnf = argdict.transformation.transform_cnf(cnf, argdict)

        except (ValueError) as e:
            with msg_prefix("BUILD ERROR: "):
                error_msg("Some error occurred while building the formula.")
                error_msg(str(e))
            sys.exit(os.EX_DATAERR)

    # Output
    if args.output_format == 'latex':

        extra_text = build_latex_cmdline_description(argv, args, t_args)

        output = cnf.latex(
            export_header=args.verbose,
            extra_text=extra_text,
            full_document=True)

    elif args.output_format == 'dimacs':

        output = cnf.dimacs(
            export_header=args.verbose,
            extra_text="COMMAND LINE: cnfgen " + " ".join(argv[1:]) + "\n")

    else:
        raise RuntimeError("INTERNAL ERROR: output format must always be defined.")

    with paginate_or_redirect_stdout(args.output):
        print(output)


# command line entry point
if __name__ == '__main__':
    setup_SIGINT()
    command_line_utility(sys.argv)
