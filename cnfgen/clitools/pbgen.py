#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Utility to build Pseudo boolean formulas interesting for proof complexity.

This is a simplified version of `cnfgen` designed to produce formulas
in opb format, and leveraging on a smarter pseudo boolean encoding.

Create the formula:

>>> from cnfgen.formula.opb import OPB
>>> c=OPB()
>>> c.add_constraint([(1,3),(2,1),(3,-2),'>=',3])
>>> print( c.to_opb() )
* #variable= 3 #constraint= 1
+1 x3 +2 x1 +3 ~x2 >= 3
<BLANKLINE>

Constraints are normalized

>>> from cnfgen.formula.opb import OPB
>>> c=OPB()
>>> c.add_constraint([(1,3),(-2,2),(1,4),'>',3])
>>> print( c.to_opb() )
* #variable= 4 #constraint= 1
+1 x3 +2 ~x2 +1 x4 >= 6
<BLANKLINE>
"""

import os
import sys
import random
import io
import argparse

from cnfgen.info import info
from cnfgen.formula.cnfio import guess_output_format

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
USAGE_STRING = """usage:
 pbgen [-h] [-V] [--tutorial] [...options...]
       <formula> <args>
       ..."""

DESCRIPTION_STRING = """example:
 pbgen php 100 40       --- Pigeonhole principle 100 pigeons 40 holes (unsat)
 pbgen op  14           --- Ordering principle on 14 elements (unsat)
 pbgen randkcnf 3 10 5  --- Random 3-CNF with 10 vars and 5 clauses

tutorial:
 pbgen --tutorial       --- show a brief tutorial on CNFgen

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --tutorial            show a brief tutorial on CNFgen
  --help-graph          help on specifying simple graphs on the command line
  --help-bipartite      help on specifying bipartite graphs on the command line
  --help-dag            help on specifying DAGs on the command line
  --output <output>, -o <output>
                        Save the formula to <output>.
                        Setting '<output>' to '-' sends the
                        formula to standard output. (default: -)
  --output-format {latex,opb}, -of {latex,opb}
                        Output format of the formulas. 'latex' is
                        convenient to insert formulas into papers, and
                        'opb' format is suitable for pseudo boolean solvers.
                        (default: opb)
  --latex, -l           Outputs formula in 'latex' format
  --seed <seed>, -S <seed>
                        Seed for any random process in the program.
                        (default: current time)

  --verbose, -v         Output formula header and comments.
  --quiet, -q           Output just the formula with no header.
  --varnames            Output map from variable indices to names.

Choices for <formula>:
    and                 a single conjunction
    bphp                binary pigeonhole principle
    cliquecoloring      There is a graph G with a k-clique and a c-coloring
    count               counting principle
    cpls                Thapen's Coloured Polynomial Local Search formula
    dimacs              Read dimacs file
    domset              k-Dominating set
    ec                  even coloring formulas
    false               CNF with one empty clause
    iso                 graph isomorphism/automorphism formula
    kclique             k clique formula
    kcliquebin          Binary k clique formula
    kcolor              k-colorability formula
    matching            perfect matching principle
    op                  ordering principle
    or                  a single disjunction
    parity              parity principle
    peb                 pebbling formula
    php                 pigeonhole principle
    pitfall             Pitfall formula
    ptn                 Bicoloring of N with no monochromatic
                        Pythagorean Triples
    ram                 ramsey number principle
    ramlb               unsat if G witnesses that r(k,s)>|V(G)|
                        (i.e. G has neither a k-clique nor an s-stable)
    randkcnf            random k-CNF
    rphp                relativized pigeonhole principle
    stone               stone formula (dense and sparse)
    subgraph            subgraph formula
    subsetcard          subset cardinality formulas
    tiling              tiling formula
    true                CNF formula with no clauses
    tseitin             tseitin formula
    vdw                 van der Waerden principle
"""

TUTORIAL_STRING = """
                 CNFGEN TUTORIAL

pbgen builds OPB formulas mostly coming from proof complexity
literature, to use as benchmark against pseudo-boolean solvers. Basic usage is

    pbgen <formula> <arg1> <arg2> ...

which builds a OPB file from family <formula> with various parameters.
For example a Pigeonhole principle formula from 5 to 4 pigeons can be
build with command line

    pbgen php 5 4

Tseitin formula are class implemented in pbgen. The command

    pbgen tseitin 100

Produces an unsatisfiable Tseitin formula on a 4-regular random graph
of 100 vertices. To have additional control on the formula you can
also use the command line

    pbgen tseitin <charge> <graph spec>

For example:

    pbgen tseitin randomodd graph.dot
    pbgen tseitin random gnd 10 6

gives two Tseitin formulas. The first has random charges of odd parity
over the encoded in the file 'graph.dot'; the second has random
changes over a random 6-regular graph of 10 vertices.

For the full list of formulas and formula transformations type one of

    pbgen -h
    pbgen --help

For the help of a specific family named <formula> type one of

    pbgen <formula> -h
    pbgen <formula> --help
"""


def setup_command_line_parsers(progname, fhelpers):
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

    Return:
    -------
    a parser for formula commands
    """

    # now we setup the main parser for the formula generation command
    parser = CLIParser(prog=progname,
                       usage=USAGE_STRING,
                       description=DESCRIPTION_STRING)

    def print_help(string):
        class _PrintHelp(argparse.Action):
            def __call__(self, parser, args, values, option_string=None):
                with paginate_or_redirect_stdout(sys.stdout):
                    print(string)
                sys.exit(os.EX_OK)

        return _PrintHelp

    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version='{project} ({version})'.format(**info))
    parser.add_argument('--tutorial',
                        nargs=0,
                        action=print_help(TUTORIAL_STRING))
    parser.add_argument(
        '--help-graph',
        nargs=0,
        action=print_help(make_graph_doc('simple',progname)))
    parser.add_argument(
        '--help-bipartite',
        nargs=0,
        action=print_help(make_graph_doc('bipartite', progname)))
    parser.add_argument('--help-dag',
                        nargs=0,
                        action=print_help(make_graph_doc('dag', progname)))
    parser.add_argument(
        '--output',
        '-o',
        type=argparse.FileType('w', encoding='utf-8'),
        metavar="<output>",
        default='-')
    ofgroup = parser.add_mutually_exclusive_group()
    ofgroup.add_argument('--output-format',
                         '-of',
                         choices=['latex','opb'],
                         default='opb')
    ofgroup.add_argument('--latex',
                         '-l',
                         dest='output_format',
                         action='store_const',
                         const='latex')
    parser.add_argument('--seed',
                        '-S',
                        metavar="<seed>",
                        default=None,
                        type=int,
                        action='store')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--verbose',
                   '-v',
                   action='store_true',
                   default=True)
    g.add_argument('--quiet',
                   '-q',
                   action='store_false',
                   dest='verbose')

    parser.add_argument('--varnames',
                        action='store_true',
                        default=False)

    # setup each formula command parser
    subparsers = parser.add_subparsers(prog=progname,
                                       metavar='<formula>')
    for sc in fhelpers:
        p = subparsers.add_parser(sc.name)
        sc.setup_command_line(p)
        sc.subparser = p
        p.set_defaults(generator=sc)

    return parser


def parse_command_line(argv, fparser):
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

    Return:
    -------
    fargs
        setup for the formula commands
    """
    for arg in argv:
        if arg == '-T':
            raise CLIError("'-T' in command line unsupported by 'pbgen', try 'cnfgen -of opb'")

    generator_cmd = argv[1:]

    # Parse the various component of the command line
    fargs = fparser.parse_args(generator_cmd)
    return fargs


def build_latex_cmdline_description(argv, args):
    """Build the latex documentation of the components of the formula.

    Insert additonal latex documentation of the formula. For example
    it includes the input files used to build it.

    Parameters
    ----------
    argv : list(str)
        arguments on command line
    args:
        parsed arguments for the formula
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
    data = iter(vars(args).items())
    data = [v for k, v in data if not k.startswith("_")]
    data = [f for f in data if isinstance(f, io.IOBase)]
    data = [f for f in data if not isinstance(f, io.IOBase) and f.mode == 'r']
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
def cli(argv=None, mode='output'):
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
        - 'formula' return a OPB object
        - 'string' return the string with the output of pbgen
        - 'output' output the formula to the user

    Raises
    ------
    CLIError:
        The command line arguments are wrong or inconsistent

    Return
    ------
    depends on the 'mode' argument
    """

    if argv is None:
        argv = sys.argv

    progname = "pbgen"

    formula_helpers = get_formula_helpers()

    parser = setup_command_line_parsers(progname, formula_helpers)

    # Be lenient on non string arguments
    argv = [str(x) for x in argv]
    with msg_prefix('* '):
        args = parse_command_line(argv, parser)

    #  Determine output format
    output_format = guess_output_format(args.output, args.output_format)

    if output_format == 'dimacs':
        raise CLIError("Please use 'cnfgen' to generate DIMACS files")

    # Correctly infer the comment character, useful to shield
    # the output.
    comment_char = {'latex': '% ', 'opb': '* '}
    try:
        cprefix = comment_char[output_format]
    except KeyError as e:
        raise InternalBug("Unknown output format") from e

    with msg_prefix(cprefix):

        # Check basics: formula family and transformation specs
        if not hasattr(args, 'generator'):
            parser.error(
                "You did not tell which formula you wanted to generate.\n")

        # Generate the formula and apply transformations
        if hasattr(args, 'seed') and args.seed:
            random.seed(args.seed)

        try:
            opb = args.generator.build_cnf(args)
        except (CLIError, ValueError) as e:
            args.generator.subparser.error(e)
        except RuntimeError as e:
            raise InternalBug(e) from e

        if hasattr(args, 'seed') and args.seed:
            opb.header['random seed'] = args.seed
        opb.header['command line'] = "pbgen " + " ".join(argv[1:])

        if mode == 'formula':
            return opb

        if mode == 'string':
            if output_format == 'latex':
                return opb.to_latex()

            if output_format == 'opb':
                return opb.to_opb()

            raise InternalBug("Unknown output format")

        extra_text = build_latex_cmdline_description(argv, args)
        opb.to_file(args.output,
                    fileformat=output_format,
                    export_header=args.verbose,
                    export_varnames=args.varnames,
                    extra_text=extra_text)

    return None

# command line entry point
def main():
    """The starting point of CNFgen program"""

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
