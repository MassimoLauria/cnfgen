#!/usr/bin/env python
"""Graph arguments on the command line

Whenever the argument of a command line is a graph <G>, this graph
should be specified using one from a number of choices. For example

 : gnp 10 .5
 : gnm 10 40 addedges 4
 : grid 4 3 5 plantclique 5

Since a graph specification is very commonly an argument in our
formulas, we need a functionality that can be reused.

The first element in a graph argument must either be
- a graph distribution/construction, followed by its arguments; or
- a filename which implies the graph format; or
- a graph format followed by filename.

Other options may follow:

The option `plantedclique` (followed by a positive integer) implies
that a random clique of given size must be added to the graph.
It applies only to simple graphs.

The option `plantedclique` (followed by two positive integers) implies
that a random biclique of given size must be added to the graph.
It applies only to bipartite graphs.

The option `addedges` (followed by a non negative integer) adds to the
graph a the specified number of edges, chosen at random among the
missing ones.

The option `save` indicates that the graph generated must be saved
into a file. `save` must be followed either by
- a filename which implies the graph format; or
- a graph format followed by filename.

Copyright (C) 2020  Massimo Lauria <massimo.lauria@uniroma1.it>
https://github.com/MassimoLauria/cnfgen.git

"""
import os
import argparse

from cnfgen.graphs import supported_formats
from cnfgen.graphs import readGraph, writeGraph
from cnfgen.clitools.msg import InternalBug

# Simple graphs
from cnfgen.clitools.graph_build import obtain_gnp
from cnfgen.clitools.graph_build import obtain_gnm
from cnfgen.clitools.graph_build import obtain_gnd
from cnfgen.clitools.graph_build import obtain_grid
from cnfgen.clitools.graph_build import obtain_torus
from cnfgen.clitools.graph_build import obtain_complete_simple
from cnfgen.clitools.graph_build import obtain_empty_simple
from cnfgen.clitools.graph_build import modify_simple_graph_plantclique

# Bipartite graphs
from cnfgen.clitools.graph_build import obtain_glrp
from cnfgen.clitools.graph_build import obtain_glrm
from cnfgen.clitools.graph_build import obtain_glrd
from cnfgen.clitools.graph_build import obtain_bipartite_regular
from cnfgen.clitools.graph_build import obtain_bipartite_shift
from cnfgen.clitools.graph_build import obtain_complete_bipartite
from cnfgen.clitools.graph_build import obtain_empty_bipartite
from cnfgen.clitools.graph_build import modify_bipartite_graph_plantbiclique

# Directed (Acyclic) graphs
from cnfgen.clitools.graph_build import obtain_tree
from cnfgen.clitools.graph_build import obtain_pyramid
from cnfgen.clitools.graph_build import obtain_path

# Generic
from cnfgen.clitools.graph_build import modify_graph_addedges

# Read input
from cnfgen.clitools.graph_fileinput import read_graph_from_input

constructions = {
    'simple': {
        'gnp': obtain_gnp,
        'gnm': obtain_gnm,
        'gnd': obtain_gnd,
        'grid': obtain_grid,
        'torus': obtain_torus,
        'complete': obtain_complete_simple,
        'empty': obtain_empty_simple
    },
    'dag': {
        'path': obtain_path,
        'tree': obtain_tree,
        'pyramid': obtain_pyramid
    },
    'digraph': {
        'tree': obtain_tree,
        'pyramid': obtain_pyramid
    },
    'bipartite': {
        'glrp': obtain_glrp,
        'glrm': obtain_glrm,
        'glrd': obtain_glrd,
        'regular': obtain_bipartite_regular,
        'shift': obtain_bipartite_shift,
        'complete': obtain_complete_bipartite,
        'empty': obtain_empty_bipartite
    }
}

options = {
    'dag': ['save'],
    'digraph': ['save'],
    'simple': ['plantclique', 'addedges', 'save'],
    'bipartite': ['plantbiclique', 'addedges', 'save']
}

formats = supported_formats()


def determine_graph_format_from_filename(filename):
    try:
        fext = os.path.splitext(filename)[-1][1:]
    except AttributeError:
        fext = None
    return fext


def construction_for_another_type(cname, graphtype):
    """Check if the construction name is valid for other types of graph"""
    for t in constructions:
        if t == graphtype:
            continue
        if cname in constructions[t]:
            return True
    return False


def format_for_another_type(fname, graphtype):
    for t in formats:
        if t == graphtype:
            continue
        if fname in formats[t]:
            return True
    return False


def parse_graph_argument(graphtype, spec):
    """Parse the command line part that corresponds to a graph argument

Here we assume that all parts have numeric arguments, except for
'save'"""
    if isinstance(spec, str):
        return parse_graph_argument(graphtype, spec.split())
    if len(spec) == 0:
        raise ValueError('Empty graph specification')

    result = {}
    result['graphtype'] = graphtype
    position = 0  # next place to parse

    def consumenumbers():
        nonlocal position
        res = []
        while position < len(spec):
            try:
                float(spec[position])
                res.append(spec[position])
                position += 1
            except ValueError:
                break
        return res

    def consumesaveinfo():
        nonlocal position
        # either a filename or a graph format + filename follows
        if position >= len(spec):
            raise ValueError(
                "Missing information about where to save the graph")
        if spec[position] in formats[graphtype]:
            if position == len(spec) - 1:
                raise ValueError("Missing file name where to save the graph")
            position += 2
            return spec[position - 2:position]
        else:
            position += 1
            return spec[position - 1:position]

    # Check that first element is a graph construction
    if spec[0] in constructions[graphtype]:
        result['construction'] = spec[0]
        result['filename'] = None
        result['fileformat'] = None
        position += 1
        result['args'] = consumenumbers()
    # Or a file with format specification
    elif spec[0] in formats[graphtype]:
        result['construction'] = None
        result['args'] = None
        result['fileformat'] = spec[0]
        if len(spec) < 2:
            raise ValueError('Filename expected after graph format')
        result['filename'] = spec[1]
        position += 2
    # Test common mistakes. I.e. the format or the construction of
    # another graph type
    elif format_for_another_type(spec[0], graphtype):
        raise ValueError('Graph format `{}` not valid for `{}` graphs'.format(
            spec[0], graphtype))
    elif construction_for_another_type(spec[0], graphtype):
        raise ValueError('Construction `{}` not valid for `{}` graphs'.format(
            spec[0], graphtype))
    # Or a file without format specification
    else:
        result['construction'] = None
        result['filename'] = spec[0]
        result['fileformat'] = 'autodetect'
        position += 1

    # Improve error message
    grmsg = ""
    if result['construction'] is not None:
        grmsg = "build with construction '{}'".format(result['construction'])
    elif result['filename'] is not None:
        grmsg = "read from file '{}'".format(result['filename'])

    # Now we load the graph options
    while position < len(spec):
        optionname = spec[position]
        if optionname in constructions:
            raise ValueError("No need for another construction specification")
        elif optionname not in options[graphtype] and optionname[0] == '-':
            raise ValueError(
                "Optional arguments as `{}` should be before any positional/graph argument"
                .format(optionname))
        elif optionname not in options[graphtype]:
            raise ValueError(
                "`{}` is not a valid option for '{}' graph\n{}".format(
                    optionname, graphtype, grmsg))
        elif optionname in result:
            raise ValueError(
                "Multiple occurrences of `{}` option.".format(optionname))
        elif optionname == 'save':
            position += 1
            result['save'] = consumesaveinfo()
            if len(result['save']) == 1:
                result['save'].insert(0, 'autodetect')
        else:
            position += 1
            result[optionname] = consumenumbers()
    # Finally we give back all we got
    return result


def obtain_graph(parsed):
    """Build a graph according to parsed graph argument
    """
    try:
        graphtype = parsed['graphtype']
    except KeyError:
        raise InternalBug(
            "Unknown graph type has been accepted on command line.")

    assert graphtype in constructions

    if parsed['construction'] in constructions[graphtype]:
        obtain_G = constructions[graphtype][parsed['construction']]
        G = obtain_G(parsed)

    else:
        assert parsed['construction'] is None
        assert 'filename' in parsed
        assert 'fileformat' in parsed
        filename = parsed['filename']
        fileformat = parsed['fileformat']
        G = read_graph_from_input(graphtype, filename, fileformat)

    # Add planted cliques
    if graphtype == 'simple':
        if 'plantclique' in parsed:
            G = modify_simple_graph_plantclique(parsed, G)
    elif graphtype == 'bipartite':
        if 'plantbiclique' in parsed:
            G = modify_bipartite_graph_plantbiclique(parsed, G)
    # Add random edges
    if 'addedges' in parsed:
        G = modify_graph_addedges(parsed, G)

    # Output the graph when requested
    if 'save' in parsed:
        saveformat, savefilename = parsed['save']
        writeGraph(G, savefilename, graphtype, saveformat)

    assert hasattr(G, 'name')
    return G


def make_graph_from_spec(graphtype, args):
    """Produce a graph from a graph specification string"""
    parsed = parse_graph_argument(graphtype, args)
    assert parsed['graphtype'] == graphtype
    return obtain_graph(parsed)


class ObtainGraphAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ObtainGraphAction, self).__init__(option_strings,
                                                dest,
                                                nargs='+',
                                                **kwargs)


def _make_graph_action(graphtype):
    """Create an Argparse action for the appropriate graph type"""
    class X(ObtainGraphAction):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(ObtainSimpleGraph, self).__init__(option_strings, dest,
                                                    **kwargs)

        def __call__(self, parser, args, values, option_string=None):
            try:
                G = make_graph_from_spec(graphtype, values)
                setattr(args, self.dest, G)
            except ValueError as e:
                parser.error(str(e))
            except FileNotFoundError as e:
                parser.error(str(e))


# ObtainSimpleGraph = _make_graph_action('simple')
# ObtainBipartiteGraph = _make_graph_action('bipartite')
# ObtainDirectedAcyclicGraph = _make_graph_action('dag')


class ObtainSimpleGraph(ObtainGraphAction):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ObtainSimpleGraph, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, args, values, option_string=None):
        try:
            G = make_graph_from_spec('simple', values)
            setattr(args, self.dest, G)
        except ValueError as e:
            parser.error(str(e))
        except FileNotFoundError as e:
            parser.error(str(e))


class ObtainBipartiteGraph(ObtainGraphAction):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ObtainBipartiteGraph, self).__init__(option_strings, dest,
                                                   **kwargs)

    def __call__(self, parser, args, values, option_string=None):
        try:
            B = make_graph_from_spec('bipartite', values)
            setattr(args, self.dest, B)
        except ValueError as e:
            parser.error(str(e))
        except FileNotFoundError as e:
            parser.error(str(e))


class ObtainDirectedAcyclicGraph(ObtainGraphAction):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ObtainDirectedAcyclicGraph,
              self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, args, values, option_string=None):
        try:
            D = make_graph_from_spec('dag', values)
            setattr(args, self.dest, D)
        except ValueError as e:
            parser.error(str(e))
        except FileNotFoundError as e:
            parser.error(str(e))
