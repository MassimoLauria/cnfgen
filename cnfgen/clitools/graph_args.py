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
import random
import networkx
from itertools import combinations

from cnfgen.graphs import supported_formats
from cnfgen.graphs import sample_missing_edges

constructions = {
    'simple': ['gnp', 'gnm', 'gnd', 'grid', 'torus', 'complete', 'empty'],
    'dag': ['tree', 'pyramid'],
    'digraph': ['tree', 'pyramid'],
    'bipartite': ['glrp', 'glrm', 'glrd', 'regular', 'shift', 'complete']
}

formats = supported_formats()

options = {
    'dag': ['save'],
    'digraph': ['save'],
    'simple': ['plantclique', 'addedges', 'save'],
    'bipartite': ['plantbiclique', 'addedges', 'save']
}


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
        result['graphformat'] = None
        position += 1
        result['args'] = consumenumbers()
    # Or a file with format specification
    elif spec[0] in formats[graphtype]:
        result['construction'] = None
        result['args'] = None
        result['graphformat'] = spec[0]
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
        result['graphformat'] = 'autodetect'
        position += 1

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
                "`{}` is not a valid option for a graph of type `{}`".format(
                    optionname, graphtype))
        elif optionname in result:
            raise ValueError(
                "Multiple occurrences of `{}` option.".format(optionname))
        elif optionname == 'save':
            position += 1
            result['save'] = consumesaveinfo()
        else:
            position += 1
            result[optionname] = consumenumbers()
    # Finally we give back all we got
    return result


def obtain_gnd(parsed):
    """Build a graph according to gnd construction"""
    try:
        n, d = parsed['args']
        n = int(n)
        d = int(d)
        assert n > 0
        assert d > 0
    except (TypeError, AssertionError, ValueError):
        raise ValueError('\'gnd\' expects arguments <N> <D> with N>0, D>0')

    if (n * d) % 2 == 1:
        raise ValueError('\'gnd\' expects arguments <N> <D> with even N * D')

    G = networkx.random_regular_graph(d, n)
    G.name = 'Random {}-regular graph of {} vertices'.format(d, n)
    return G


def obtain_gnp(parsed):
    """Build a graph according to gnp construction"""
    try:
        n, p = parsed['args']
        n = int(n)
        p = float(p)
        assert n > 0
        assert 0 < p < 1
    except (TypeError, ValueError, AssertionError):
        raise ValueError(
            '\'gnp\' expects arguments <N> <p> with N>0, p in [0,1]')

    G = networkx.gnp_random_graph(n, p)
    G.name = 'Random {}-biased graph of {} vertices'.format(p, n)


def obtain_gnm(parsed):
    """Build a graph according to gnm construction"""
    try:
        n, m = parsed['args']
        n = int(n)
        m = int(m)
        assert n > 0
        assert m >= 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'gnm\' expects arguments <N> <M> with N>0, M>=0')

    G = networkx.gnm_random_graph(n, m)
    G.name = 'Random graph of {} vertices with {} edges'.format(n, m)
    return G


def obtain_complete_simple_graph(parsed):
    """Build a simple complete graph"""
    try:
        if len(parsed['args']) != 1:
            raise ValueError
        n = int(parsed['args'][0])
        assert n > 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'complete\' expects argument <N> with N>0')

    G = networkx.complete_graph(n)
    G.name = "Complete graphs of {} vertices".format(n)
    return G


def obtain_empty_simple_graph(parsed):
    """Build a simple empty graph"""
    try:
        if len(parsed['args']) != 1:
            raise ValueError
        n = int(parsed['args'][0])
        assert n > 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'complete\' expects argument <N> with N>0')

    G = networkx.empty_graph(n)
    G.name = "Empty graphs of {} vertices".format(n)
    return G


def obtain_grid_or_torus(parsed, periodic):
    """Build a graph according to grid/toris construction"""
    dimensions = parsed['args']
    if periodic:
        name = 'torus'
    else:
        name = 'grid'
    try:
        dimensions = [int(x) for x in dimensions]
        for d in dimensions:
            if d <= 0:
                raise ValueError
    except (TypeError, ValueError):
        raise ValueError(
            'Dimensions d1 x ... x dn of a {} must be positive integer'.format(
                name))

    G = networkx.grid_graph(dimensions, periodic=periodic)
    G.name = "{} graph of dimension {}".format(name, dimensions)


def modify_simple_graph_plantclique(parsed, G):
    try:
        if len(parsed['plantclique']) != 1:
            raise ValueError
        cliquesize = int(parsed['plantclique'][0])
        assert cliquesize >= 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'plantclique\' expects argument <k> with k>=0')

    if cliquesize > G.order():
        raise ValueError("Planted clique cannot be larger than graph")

    clique = random.sample(G.nodes(), cliquesize)

    for v, w in combinations(clique, 2):
        G.add_edge(v, w)
    G.name += " + planted {}-clique".format(cliquesize)
    return G


def modify_simple_graph_addedges(parsed, G):
    try:
        if len(parsed['addedges']) != 1:
            raise ValueError
        k = int(parsed['addedges'][0])
        assert k >= 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'addedges\' expects argument <k> with k>=0')

    G.add_edges_from(sample_missing_edges(G, k))
    G.name += " + {} random edges".format(k)
    return G


def obtain_simple_graph(parsed):
    """Build a simple graph according to parsed graph argument
    """
    if parsed['construction'] == 'gnd':
        G = obtain_gnd(parsed)

    elif parsed['construction'] == 'gnp':
        G = obtain_gnp(parsed)

    elif parsed['construction'] == 'gnm':
        G = obtain_gnp(parsed)

    elif parsed['construction'] == 'grid':
        G = obtain_grid_or_torus(parsed, periodic=False)

    elif parsed['construction'] == 'torus':
        G = obtain_grid_or_torus(parsed, periodic=True)

    elif parsed['construction'] == 'complete':
        G = obtain_complete_simple_graph(parsed)

    elif parsed['construction'] == 'empty':
        G = obtain_empty_simple_graph(parsed)

    else:
        assert 'filename' in parsed
        assert 'graphformat' in parsed
        raise RuntimeError('reading graph from input is not implemented yet')

    # Graph modifications
    if 'plantclique' in parsed:
        G = modify_simple_graph_plantclique(parsed, G)

    if 'addedges' in parsed:
        G = modify_simple_graph_addedges(parsed, G)

    # Output the graph is requested
    if 'save' in parsed:
        raise ValueError('Saving generated graph not implemented yet')

    assert hasattr(G, 'name')
    return G


class SimpleGraphAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(SimpleGraphAction, self).__init__(option_strings,
                                                dest,
                                                nargs='*',
                                                **kwargs)

    def __call__(self, parser, args, values, option_string=None):
        try:
            parsed = parse_graph_argument('simple', values)
            G = obtain_simple_graph(parsed)
            setattr(args, self.dest, G)
        except ValueError as e:
            parser.error(str(e))
