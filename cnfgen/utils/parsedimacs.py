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

    return: (n,c) where

    n is the number of variables
    c is the list of compressed clauses.
    """
    n = None  # negative signal that spec line has not been read
    m = None

    my_header = ""
    my_clauses = []

    line_counter = 0
    literal_buffer = []

    for l in infile.readlines():

        line_counter += 1

        # Ignore comments
        if l[0] == 'c':
            continue

        # parse spec line
        if l[0] == 'p':
            if n is not None:
                raise ValueError(
                    "There is a another spec at line {}".format(line_counter))
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
                elif 1 <= abs(lv) <= n:
                    literal_buffer.append(lv)
                else:
                    raise ValueError
        except ValueError:
            raise ValueError("Invalid literal at line {}".format(line_counter))

    # Checks at the end of parsing
    if len(literal_buffer) > 0:
        raise ValueError("Last clause was incomplete")

    if n is None:
        raise ValueError("Missing spec line 'p cnf <n> <m>")

    if m != len(my_clauses):
        raise ValueError("Formula contains {} clauses "
                         "but {} were expected.".format(len(my_clauses), m))

    # return the formula
    return (n, my_clauses)


def readCNF(infile=None):
    """Read dimacs file into a CNF object

    By default it reads the file from standard input.
    """
    if infile is None:
        infile = sys.stdin
    if not hasattr(infile, 'name'):
        infile.name = 'unknown'

    nvariables, clauses = dimacs2compressed_clauses(infile)

    cnf = CNF(
        description='Formula read from DIMACS file {}'.format(infile.name))

    for i in range(1, nvariables + 1):
        cnf.add_variable(i)

    cnf._add_compressed_clauses(clauses)

    # return the formula
    return cnf
