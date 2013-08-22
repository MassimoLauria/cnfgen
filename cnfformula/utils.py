#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
from .cnf import CNF

__docstring__ =\
"""Various utilities for the manipulation of the CNFs.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

__all__ = ["dimacs2cnf"]

def dimacs2cnf(file_handle):
    """Load dimacs file into a CNF object
    """
    cnf=CNF(header="")

    n = -1  # negative signal that spec line has not been read
    m = -1

    line_counter=0
    clause_counter=0
    literal_buffer=[]

    for l in file_handle.readlines():

        line_counter+=1

        # Add all the comments to the header. If a comment is found
        # inside the formula, add it to the header as well. Comments
        # interleaving clauses are not allowed in dimacs format.
        if l[0]=='c':
            cnf.header = cnf.header+(l[2:] or '\n')
            continue

        # parse spec line
        if l[0]=='p':
            if n>=0:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(line_counter))
            _,_,nstr,mstr = l.split()
            n = int(nstr)
            m = int(mstr)
            for i in range(1,n+1):
                cnf.add_variable(i)
            continue


        # parse literals
        for lv in [int(lit) for lit in l.split()]:
            if lv==0:
                cnf._add_compressed_clauses([tuple(literal_buffer)])
                literal_buffer=[]
                clause_counter +=1
            else:
                literal_buffer.append(lv)

    # Checks at the end of parsing
    if len(literal_buffer)>0:
        raise ValueError("Syntax error: last clause was incomplete")

    if m=='-1':
        raise ValueError("Warning: empty input formula ")

    if m!=clause_counter:
        raise ValueError("Warning: input formula "+
                         "contains {} instead of expected {}.".format(clause_counter,m))

    # return the formula
    cnf._check_coherence(force=True)
    return cnf

