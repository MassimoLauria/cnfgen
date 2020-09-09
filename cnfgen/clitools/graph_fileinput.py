#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Functionality for reading graphs on the command line

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import os
import sys
import textwrap
import contextlib
from fileinput import FileInput

from cnfgen.graphs import supported_formats as supported_graph_formats
from cnfgen.graphs import readGraph

from cnfgen.clitools.msg import interactive_msg, msg_prefix


@contextlib.contextmanager
def open_input(filename):
    if filename == '-':
        fh = sys.stdin
    else:
        fh = open(filename, 'r')
    try:
        yield fh
    finally:
        if filename != '-':
            fh.close()


def read_graph_from_input(graphtype, filename, fileformat):
    """Read a graph from input according to command line arguments

    Parameters:
    -----------
    graphtype: str
         one of {dag,bipartite, simple}
    filename:
         filename for be read
    fileformat:
         either 'autodetect' or an appropriate graph file format
    """
    # is file source stdin?
    try:
        fext = os.path.splitext(filename)[-1][1:]
    except AttributeError:
        fext = ''
    allowed = supported_graph_formats()[graphtype]

    no_ext = """
    The formula generation process you asked for needs a {} graph in
    input. Graph format was not specified on the command line and there no
    file name extension to guess that from, thus it is impossible
    to proceed.""".format(graphtype)

    bad_ext = """
    The formula generation process you asked for needs a {} graph in
    input. Graph format was not specified on the command line and the
    file name extension do not corresponds to any of the allowed
    format, thus it is impossible to proceed.""".format(graphtype)

    ask_opt = """
    Please put the 'format' in the graph specification before the file name,
    where <format> in one of {}""".format(allowed)

    ask_gr = "Please insert on <stdin> a simple undirected graph in {} format.".format(
        fileformat)

    no_ext = textwrap.dedent(no_ext)
    # no_ext = textwrap.fill(no_ext, width=60)
    bad_ext = textwrap.dedent(bad_ext)
    # bad_ext = textwrap.fill(bad_ext, width=60)

    ask_opt = textwrap.dedent(ask_opt)
    # ask_opt = textwrap.fill(ask_opt, width=60)

    with open_input(filename) as filesource:
        # detect graph format
        if fileformat == 'autodetect':
            if len(fext) == 0:
                raise ValueError(no_ext + "\n" + ask_opt)

            elif fext not in allowed:
                raise ValueError(bad_ext + "\n" + ask_opt)

            fileformat = fext

        if filesource == sys.stdin:
            with msg_prefix("INPUT: "):
                interactive_msg(ask_gr, filltext=70)

        G = readGraph(filesource, graphtype, fileformat)

    G.name = "{} graph from file '{}' (format: {})".format(
        graphtype, filename, fileformat)
    return G
