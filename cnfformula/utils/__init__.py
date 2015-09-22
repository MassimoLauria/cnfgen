#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Various utilities for the manipulation of the CNFs.
"""

from __future__ import print_function
from ..cnf import CNF



def dimacs2compressed_clauses(file_handle):
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

    my_header=""
    my_clauses=[]

    line_counter=0
    literal_buffer=[]

    for l in file_handle.readlines():

        line_counter+=1

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
        if l[0]=='c':
            if l[1]==' ':
                my_header += l[2:] or '\n'
            else: 
                my_header += l[1:] or '\n'
            continue

        # parse spec line
        if l[0]=='p':
            if n>=0:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(line_counter))
            _,_,nstr,mstr = l.split()
            n = int(nstr)
            m = int(mstr)
            continue
            

        # parse literals
        for lv in [int(lit) for lit in l.split()]:
            if lv==0:
                my_clauses.append(tuple(literal_buffer))
                literal_buffer=[]
            else:
                literal_buffer.append(lv)

    # Checks at the end of parsing
    if len(literal_buffer)>0:
        raise ValueError("Syntax error: last clause was incomplete")

    if m=='-1':
        raise ValueError("Warning: empty input formula ")

    if m!=len(my_clauses):
        raise ValueError("Warning: input formula "+
                         "contains {} instead of expected {}.".format(len(my_clauses),m))

    # return the formula
    return (my_header,n,my_clauses)




def dimacs2cnf(file_handle):
    """Load dimacs file into a CNF object
    """

    header, nvariables, clauses = dimacs2compressed_clauses(file_handle)

    cnf = CNF(header=header)

    for i in xrange(1,nvariables+1):
        cnf.add_variable(i)

    cnf._add_compressed_clauses(clauses)

    # return the formula
    cnf._check_coherence(force=True)
    return cnf
