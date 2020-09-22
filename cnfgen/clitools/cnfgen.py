#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Create the CNFs:

>>> from cnfgen.cnf import CNF
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
import io
import argparse

from cnfgen.info import info

from cnfgen.clitools.cmdline import paginate_or_redirect_stdout
from cnfgen.clitools.cmdline import setup_SIGINT
from cnfgen.clitools.cmdline import CLIParser, CLIError, CLIHelpFormatter

from cnfgen.clitools.cmdline import get_formula_helpers
from cnfgen.clitools.cmdline import get_transformation_helpers

from cnfgen.clitools.msg import error_msg
from cnfgen.clitools.msg import msg_prefix
from cnfgen.clitools.msg import InternalBug

from cnfgen.clitools.graph_docs import make_graph_doc

#################################################################
#          Command line tool follows
#################################################################

# Help strings
usage_string = """{} [-h] [-V] [--tutorial] [...options...]
              <formula> <args>
              [-T <transformation> <args>]
              [-T <transformation> <args>]
              ..."""

description_string = """example:
 {0} php 100 40         --- Pigeonhole principle 100 pigeons 40 holes (unsat)
 {0} op  14             --- Ordering principle on 14 elements (unsat)
 {0} randkcnf 3 10 5    --- Random 3-CNF with 10 vars and 5 clauses

tutorial:
 {0} --tutorial         --- show a brief tutorial on CNFgen

"""

tutorial_string = """
                 CNFGEN TUTORIAL

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

    {0} tseitin randomodd graph.dot
    {0} tseitin random gnd 10 4

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
    t_parser = CLIParser(add_help=False)

    t_subparsers = t_parser.add_subparsers(
        prog=progname + " <formula> <args> -T",
        title="Available formula transformation",
        metavar="<transformation>")
    for sc in thelpers:
        p = t_subparsers.add_parser(sc.name,
                                    help=sc.description,
                                    formatter_class=CLIHelpFormatter)
        sc.setup_command_line(p)
        sc.subparser = p
        p.set_defaults(transformation=sc)

    # now we setup the main parser for the formula generation command
    parser = CLIParser(prog=progname,
                       usage=usage_string.format(progname),
                       description=description_string.format(progname),
                       formatter_class=CLIHelpFormatter)

    def print_help(string):
        class _PrintHelp(argparse.Action):
            def __call__(self, parser, args, values, option_string=None):
                with paginate_or_redirect_stdout(sys.stdout):
                    print(string.format(progname))
                sys.exit(os.EX_OK)

        return _PrintHelp

    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version='{project} ({version})'.format(**info))
    parser.add_argument('--tutorial',
                        nargs=0,
                        action=print_help(tutorial_string),
                        help="show a brief tutorial on CNFgen")
    parser.add_argument(
        '--help-graph',
        nargs=0,
        action=print_help(make_graph_doc('simple', '{0} ...')),
        help="how to specify simple graphs on the command line")
    parser.add_argument(
        '--help-bipartite',
        nargs=0,
        action=print_help(make_graph_doc('bipartite', '{0} ...')),
        help="how to specify bipartite graphs on the command line")
    parser.add_argument('--help-dag',
                        nargs=0,
                        action=print_help(make_graph_doc('dag', '{0} ...')),
                        help="how to specify DAGs on the command line")
    parser.add_argument(
        '--output',
        '-o',
        type=argparse.FileType('w', encoding='utf-8'),
        metavar="<output>",
        default='-',
        help="""Save the formula to <output>. Setting '<output>' to '-' sends the
                        formula to standard output. (default: -)
                        """)
    ofgroup = parser.add_mutually_exclusive_group()
    ofgroup.add_argument('--output-format',
                         '-of',
                         choices=['latex', 'dimacs'],
                         default='dimacs',
                         help="""
                        Output format of the formulas. 'latex' is
                        convenient to insert formulas into papers, and
                        'dimacs' is the format used by sat solvers.
                        (default: dimacs)
                        """)
    ofgroup.add_argument('--latex',
                         '-l',
                         dest='output_format',
                         action='store_const',
                         const='latex',
                         help="Outputs formula in 'latex' format")
    parser.add_argument('--seed',
                        '-S',
                        metavar="<seed>",
                        default=None,
                        type=int,
                        action='store',
                        help="""Seed for any random process in the
                        program. (default: current time)
                        """)
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--verbose',
                   '-v',
                   action='store_true',
                   default=True,
                   help="""Output formula header and comments.""")
    g.add_argument('--quiet',
                   '-q',
                   action='store_false',
                   dest='verbose',
                   help="""Output just the formula with no header.""")

    # setup each formula command parser
    subparsers = parser.add_subparsers(prog=progname,
                                       title="Available formula types",
                                       metavar='<formula>')
    for sc in fhelpers:
        p = subparsers.add_parser(sc.name,
                                  help=sc.description,
                                  formatter_class=CLIHelpFormatter)
        sc.setup_command_line(p)
        sc.subparser = p
        p.set_defaults(generator=sc)

    # Attach the list of available transformations
    # but without usage string
    extension = t_parser.format_help().splitlines()
    extension = "\n".join(extension[2:])
    parser.epilog = extension

    return parser, t_parser


def parse_command_line(argv, fparser, tparser):
    """Parser command line arguments

    Split command line around '-T' options in parts. Extract the
    formula generator setup from the first part, and extract a chain
    of formula transformation commands

    Parameters:
    -----------
    argv:
        command line arguments
    parser:
        parser for the formulas commands
    t_parser:
        parser for the transformations commands

    Return:
    -------
    fargs, list(targs)
        setup for the various commands
    """
    # Split the command line
    cmd_chunks = [[]]
    for arg in argv:
        if arg == '-T':
            cmd_chunks.append([])
        else:
            cmd_chunks[-1].append(arg)

    generator_cmd = cmd_chunks[0][1:]
    transformation_cmds = cmd_chunks[1:]

    # Parse the various component of the command line
    fargs = fparser.parse_args(generator_cmd)
    targs = []
    for cmd in transformation_cmds:
        targs.append(tparser.parse_args(cmd))

    return fargs, targs


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
    # The docstring of the formula family generator
    cmdline_descr = []
    if hasattr(args.generator, "docstring"):
        cmdline_descr += [
            "\\noindent\\textbf{Docstring:}",
            "\\begin{lstlisting}[breaklines,basicstyle=\\small]",
            args.generator.docstring, "\\end{lstlisting}"
        ]

    # Find input files specified in the command line
    input_files = []
    for namespace in [args] + t_args:
        data = iter(vars(namespace).items())
        data = [v for k, v in data if not k.startswith("_")]
        data = [f for f in data if isinstance(f, io.IOBase)]
        data = [f for f in data if (f != sys.stdin) and f.mode == 'r']
        input_files.extend(data)

    # Add them all to the latex document
    for f in input_files:
        f.seek(0, 0)
        cmdline_descr += [
            "\\noindent\\textbf{Input file} \\verb|%s|" % f.name,
            "\\begin{lstlisting}[breaklines,basicstyle=\\small]",
            f.read(), "\\end{lstlisting}"
        ]

    # Return all as a single string
    cmdline_descr += ['\n']
    return "\n".join(cmdline_descr)


# Command line interface
def cli(argv=sys.argv, mode='output'):
    """CNFgen main command line interface

    This function provide the main interface to CNFgen. It sets up the
    command line, parses the command line arguments, builds the
    appropriate formula and outputs its representation.


    Parameters
    ----------
    argv: list, optional
        The list of token with the command line arguments/options.

    mode: str
        One among 'formula', 'string', 'output' (latter is the default)
        - 'formula' return a CNF object
        - 'string' return the string with the output of CNFgen
        - 'output' output the formula to the user

    Raises
    ------
    CLIError:
        The command line arguments are wrong or inconsistent

    Return
    ------
    depends on the 'mode' argument
    """

    progname = os.path.basename(argv[0])

    formula_helpers = get_formula_helpers()
    transformation_helpers = get_transformation_helpers()

    parser, t_parser = setup_command_line_parsers(progname, formula_helpers,
                                                  transformation_helpers)

    # Be lenient on non string arguments
    argv = [str(x) for x in argv]
    with msg_prefix('c '):
        args, t_args = parse_command_line(argv, parser, t_parser)

    # Correctly infer the comment character, useful to shield
    # the output.
    comment_char = {'dimacs': 'c ', 'latex': '% '}
    try:
        cprefix = comment_char[args.output_format]
    except KeyError:
        raise InternalBug("Unknown output format")

    with msg_prefix(cprefix):

        # Check basics: formula family and transformation specs
        if not hasattr(args, 'generator'):
            parser.error(
                "You did not tell which formula you wanted to generate.\n")

        for argdict in t_args:
            if not hasattr(argdict, 'transformation'):
                t_parser.error(
                    "You used option '-T' but did not pick a transformation.\n"
                )

        # Generate the formula and apply transformations
        if hasattr(args, 'seed') and args.seed:
            random.seed(args.seed)

        try:
            cnf = args.generator.build_cnf(args)
        except (CLIError, ValueError) as e:
            args.generator.subparser.error(e)
        except RuntimeError as e:
            raise InternalBug(e)

        for argdict in t_args:
            try:
                cnf = argdict.transformation.transform_cnf(cnf, argdict)
            except (CLIError, ValueError) as e:
                argdict.transformation.subparser.error(e)
            except RuntimeError as e:
                raise InternalBug(e)

        if hasattr(args, 'seed') and args.seed:
            cnf.header['random seed'] = args.seed
        cnf.header['command line'] = "cnfgen " + " ".join(argv[1:])

        if mode == 'formula':
            return cnf

        # Output
        if args.output_format == 'latex':

            extra_text = build_latex_cmdline_description(argv, args, t_args)

            output = cnf.latex(export_header=args.verbose,
                               extra_text=extra_text,
                               full_document=True)

        elif args.output_format == 'dimacs':

            output = cnf.dimacs(export_header=args.verbose)

        else:
            raise InternalBug("Unknown output format")

    if mode == 'string':
        return output

    with paginate_or_redirect_stdout(args.output):
        print(output)


# command line entry point
def main():

    setup_SIGINT()

    try:

        cli(sys.argv, mode='output')

    except CLIError as e:
        error_msg(e)
        sys.exit(-1)

    except InternalBug as e:
        print(e, file=sys.stderr)
        sys.exit(-1)

    except (BrokenPipeError, IOError):
        # avoid errors when stdout is closed before the end of the
        # program (i.e. piping into a command line which does
        # not work.)
        pass

    # avoid signaling BrokenPipeError as whatnot
    sys.stderr.close()


if __name__ == '__main__':
    main()
