#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF transformation, it increases the hardness of a CNF.

This is the implementation of a command line utility that transform
CNF files in DIMACS format into new  CNFs

Utilities to apply to a dimacs CNF file, a transformation which
increase the hardness of the formula

Accept a cnf in dimacs format in input
"""

from __future__ import print_function
import os

from .. import available_transform
from ..transformation import transform_compressed_clauses,StopClauses
from . import dimacs2compressed_clauses


import sys

# Python 2.6 does not have argparse library
try:
    import argparse
    from argparse import RawDescriptionHelpFormatter
except ImportError:
    print("Sorry: %s requires `argparse` library, which is missing.\n"%__progname__,file=sys.stderr)
    print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
    print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
    print(" * http://code.google.com/p/argparse",file=sys.stderr)
    print("",file=sys.stderr)
    exit(-1)



def setup_command_line(parser):
    """Setup general command line options

    Arguments:
    - `parser`: parser to fill with options
    """
    parser.add_argument('transformation',
                        metavar="<method>",
                        choices=available_transform().keys(),
                        default='none',
                        help="""
                        Transformation method the CNF formula to make it harder.
                        """)

    parser.add_argument('hardness',
                        metavar="<hardness>",
                        nargs='?',
                        type=int,
                        default=None,
                        help="""
                        Hardness parameter for the transformation procedure.
                        """)

    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The input formula is read as a dimacs CNF file file
                        instead of standard input. Setting '<input>'
                        to '-' is another way to read from standard
                        input. (default: -) """)

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

    parser.add_argument('--noheader',
                        '-n',action='store_false',dest='header',
                        help="""Do not output the preamble, so that
                        formula generation is faster (one pass on the
                        data).""")


### Produce the dimacs output from the data
def dimacstransform(inputfile, method, hardness, output, header=True):
    """Applies the transformation to a DIMACS file. 

    Parameters
    ----------
    inputfile : file
        a file object containing the DIMACS CNF formula

    method: string
        the name of the transformation method

    hardness: int or None
        the hardness parameter. If None, then the default for the
        transformation method is used.

    output : file
        the place where to print the output to.
 
    header: boolean
        if `False` only the clauses will be printed. This is fast but 
        does not produce a proper DIMACS file.

    Returns
    -------
        an object with two fields: `variables` and `clauses` with 
        the number of variables and clauses in the output formula
     """
    # Generate the basic formula
    if header:
        
        from cStringIO import StringIO
        output_cache=StringIO()

    else:
        output_cache=output

    o_header,_,o_clauses = dimacs2compressed_clauses(inputfile)

    cls_iter=transform_compressed_clauses(o_clauses,method,hardness)

    try:

        while True:
            cls = cls_iter.next()
            print(" ".join([str(l) for l in cls])+" 0",file=output_cache)
            
    except StopClauses as cnfinfo:

        if header:
            # clauses cached in memory
            print("c Formula transformed with method '{}' and parameter {}\nc".format(method,hardness),
                  file=output)

            lines=o_header.split('\n')[:-1]

            if len(lines)>0:
                print("\n".join(("c "+line).rstrip() for line in lines),
                      file=output)
                
            print("p cnf {} {}".format(cnfinfo.variables,cnfinfo.clauses),
                  file=output)
            output.write(output_cache.getvalue())

        else:
            # clauses have been already sent to output
            pass    
        return cnfinfo

###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    assert(insignal!=None)
    assert(frame!=None)
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv=sys.argv):

    # Parse the command line arguments
    help_epilogue = "Available transformations:\n\n" + \
                    "\n".join("  {}\t:  {}".format(k,entry[0])
                              for k,entry in available_transform().iteritems()) 
    

    parser=argparse.ArgumentParser(prog   = os.path.basename(argv[0]),
                                   epilog = help_epilogue ,
                                   formatter_class = RawDescriptionHelpFormatter)


    setup_command_line(parser)

    # Process the options
    args=parser.parse_args(argv[1:])

    dimacstransform(args.input,
                    args.transformation,
                    args.hardness,
                    args.output,
                    args.header)

### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
