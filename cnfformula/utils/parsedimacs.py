#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Various utilities for the manipulation of the CNFs.
"""

import sys
from ..cnf import CNF



def dimacs2compressed_clauses(infile):
    """
    Parse a dimacs cnf file into a list of
    compressed clauses.

    return: (h,n,c) where

    h is a string of text (the header)
    n is the number of variables
    c is the list of compressed clauses.
    """
    n = -1  # negative signal that spec line has not been read
    m = -1

    my_header = ""
    my_clauses = []

    line_counter = 0
    literal_buffer = []

    for l in infile.readlines():

        line_counter += 1

        # Add all the comments to the header. If a comment is found
        # inside the formula, add it to the header as well. Comments
        # interleaving clauses are not allowed in dimacs format.
        #
        # Notice the hack in the comment parsing, the dimacs output
        # will always put a space between the 'c' character and the
        # header line. If such character is found during parsing, it
        # is not memorized, and if the CNF is dumped again it is
        # introduced again.
        #
        # It there is no such separator, then a cycle of
        # reading/writing the cnf will change the header section.
        #
        if l[0] == 'c':
            if l[1] == ' ':
                my_header += l[2:] or '\n'
            else:
                my_header += l[1:] or '\n'
            continue

        # parse spec line
        if l[0] == 'p':
            if n >= 0:
                raise ValueError("There is a another spec at line {}".format(line_counter))
            try:
                _, _, nstr, mstr = l.split()
                n = int(nstr)
                m = int(mstr)
                l.split()
            except ValueError:
                raise ValueError("Spec at line {} should have "
                                 "format 'p cnf <n> <m>'".format(line_counter))
            continue
            

        # parse literals
        try:
            for lv in [int(lit) for lit in l.split()]:
                if lv == 0:
                    my_clauses.append(tuple(literal_buffer))
                    literal_buffer = []
                else:
                    literal_buffer.append(lv)
        except ValueError:
            raise ValueError("Invalid literal at line {}".format(line_counter))

    # Checks at the end of parsing
    if len(literal_buffer) > 0:
        raise ValueError("Last clause was incomplete")

    if m == '-1':
        raise ValueError("Missing spec line 'p cnf <n> <m>")

    if m != len(my_clauses):
        raise ValueError("Formula contains {} clauses "
                         "but {} were expected.".format(len(my_clauses), m))

    # return the formula
    return (my_header, n, my_clauses)




def readCNF(infile=None):
    """Read dimacs file into a CNF object

    By default it reads the file from standard input.
    """
    if infile is None:
        infile = sys.stdin

    header, nvariables, clauses = dimacs2compressed_clauses(infile)

    cnf = CNF(header=header)

    for i in range(1, nvariables+1):
        cnf.add_variable(i)

    cnf._add_compressed_clauses(clauses)

    # return the formula
    cnf._check_coherence(force=True)
    return cnf
