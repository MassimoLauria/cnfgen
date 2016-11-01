#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Components for command line interface

CNFgen has many command line entry points to its functionality, and
some of them expose the same functionality over and over. This module
contains useful common components.

Copyright (C) 2012, 2013, 2014, 2015, 2016  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

from __future__ import print_function

    
import sys
import argparse

import networkx
import random

from itertools import combinations, product

from .graphs import supported_formats as graph_formats
from .graphs import readGraph,writeGraph
from .graphs import bipartite_random_left_regular,bipartite_random_regular,bipartite_shift
from .graphs import bipartite_sets
from .graphs import dag_complete_binary_tree,dag_pyramid
from .graphs import sample_missing_edges



try: # NetworkX >= 1.10

    complete_bipartite_graph    = networkx.bipartite.complete_bipartite_graph
    bipartite_random_graph      = networkx.bipartite.random_graph
    bipartite_gnmk_random_graph = networkx.bipartite.gnmk_random_graph

except AttributeError: # Networkx < 1.10
    
    from networkx import complete_bipartite_graph
    from networkx import bipartite_random_graph
    from networkx import bipartite_gnmk_random_graph



__all__ = [ "register_cnfgen_subcommand","is_cnfgen_subcommand",
            "DirectedAcyclicGraphHelper", "SimpleGraphHelper", "BipartiteGraphHelper"]


__cnfgen_subcommand_mark = "_is_cnfgen_subcommand"

def register_cnfgen_subcommand(cls):
    """Register the class as a formula subcommand

    CNFgen command line tool invokes subcommands to generate formula
    families. This class decorator is used to declare that a class is
    indeed the implementation of a formula generator subcommand.
    In this way CNFgen setup code will automatically find it and
    integrate it into the CNFgen command line interface.

    The class argument is tested to check whether it is a suitable
    implementation of a CNFgen subcommand.

    In particular the class must have four attributes
    
    + ``name`` the name of the CNF formula 
    + ``description`` a short description of the formulas
    + ``setup_command_line`` a method that takes a command line parser 
      object and populates it with appropriate options.
    + ``build_cnf`` a method that takes the arguments and produce the CNF.

    The parser expected by ``setup_command_line(parser)`` in such as the one produced by
    ``argparse.ArgumentParser``.

    The argument for ``build_cnf(args)`` is the dictionary of flags and
    options parsed from the command line as produced by ``args=parser.parse_args``

    Parameters
    ----------
    class : any
        the class to test

    
    Returns
    -------
    None

    Raises
    ------
    AssertionError 
        when the class is not formula subcommand
    """
    assert \
        hasattr(cls,'build_cnf') and \
        hasattr(cls,'setup_command_line') and \
        hasattr(cls,'name') and \
        hasattr(cls,'description')

    setattr(cls,__cnfgen_subcommand_mark,True)
    return cls

def is_cnfgen_subcommand(cls):
    """Test whether the object is a registered CNFgen subcommand

    Parameters
    ----------
    class : any
        the class to test

    Returns
    -------
    bool
    """
    return hasattr(cls,__cnfgen_subcommand_mark)


__cnf_transformation_subcommand_mark = "_is_cnf_transformation_subcommand"

def register_cnf_transformation_subcommand(cls):
    """Register the class as a transformation subcommand

    CNFgen command line tool invokes subcommands to apply
    transformations to formula families. This class decorator is used
    to declare that a class is indeed the implementation of a formula
    transformation subcommand. In this way CNFgen setup code will
    automatically find it and integrate it into the CNFgen command
    line interface.

    The class argument is tested to check whether it is a suitable
    implementation of a CNFgen subcommand.

    In particular the class must have four attributes
    
    + ``name`` the name of the CNF transformation
    + ``description`` a short description of the transformation
    + ``setup_command_line`` a method that takes a command line parser object and populates it with appropriate options.
    + ``transform_cnf`` a method that takes a CNF, the arguments and produce a new CNF.

    The parser expected by ``setup_command_line(parser)`` in such as the one produced by
    ``argparse.ArgumentParser``.

    The arguments for ``transform_cnf(F,args)`` are a CNF, and the dictionary of flags and
    options parsed from the command line as produced by ``args=parser.parse_args``

    Parameters
    ----------
    class : any
        the class to test

    
    Returns
    -------
    None

    Raises
    ------
    AssertionError 
        when the class is not a transformation subcommand

    """
    assert \
        hasattr(cls,'transform_cnf') and \
        hasattr(cls,'setup_command_line') and \
        hasattr(cls,'name') and \
        hasattr(cls,'description')

    setattr(cls,__cnf_transformation_subcommand_mark,True)
    return cls

def is_cnf_transformation_subcommand(cls):
    """Test whether the object is a registered CNFgen transformation

    Parameters
    ----------
    class : any
        the class to test

    Returns
    -------
    bool
    """
    return hasattr(cls,__cnf_transformation_subcommand_mark)



def find_methods_in_package(package,test, sortkey=None):
    """Explore a package for functions and methods that implement a specific test"""

    
    import pkgutil

    result = []

    if sortkey == None :
        sortkey = lambda x : x
    
    for loader, module_name, _ in  pkgutil.walk_packages(package.__path__):
        module_name = package.__name__+"."+module_name
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            module = loader.find_module(module_name).load_module(module_name)
        for objname in dir(module):
            obj = getattr(module, objname)
            if test(obj):
                result.append(obj)
    result.sort(key=sortkey)
    return result
            




### Graph readers/generators

def positive_int(string):
    """Type checker for positive integers
    """
    value = int(string)
    if (value<=0) : raise ValueError('integer is not positive: {}'.format(value))
    return value


class GraphHelper(object):
    """Command Line helper for reading graphs
    """

    @staticmethod
    def setup_command_line(parser):
        """Setup command line options for getting graphs"""
        raise NotImplementedError("Graph Input helper must be subclassed")

    @staticmethod
    def obtain_graph(args):
        """Read/Generate the graph according to the command line options"""
        raise NotImplementedError("Graph Input helper must be subclassed")


class DirectedAcyclicGraphHelper(GraphHelper):

    @staticmethod
    def setup_command_line(parser, suffix="", required=False):
        """Setup command line options for reading a DAG

        Parameters
        ----------
        parser : ArgParse parser object
            it is populated with options for input graphs

        suffix: string, optional
            add a suffix to all input options. Useful if you need to input 
            multiple graphs in the same command line (default: empty)

        require : bool, optional
            enforce that at least one input specification is required. 
            If it is not the case the standard input is the default input. 
            Not a good idea if we read multiple graphs in input.
        """

        gr=parser.add_argument_group(title="Input directed acyclic graph (DAG) " + suffix,
                                     description="""
                                     You can either read the input DAG from file according to one of
                                     the formats, or generate it using one of the constructions included.""")

        gr=gr.add_mutually_exclusive_group(required=required)
       
        gr.add_argument('--input'+suffix,'-i'+suffix,
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Read the DAG from <input>. Setting '<input>' to '-' is another way
                        to read from standard input. (default: -) """)

        gr.add_argument('--tree'+suffix,type=positive_int,action='store',metavar="<height>",
                            help="rooted tree digraph")

        gr.add_argument('--pyramid'+suffix,type=positive_int,action='store',metavar="<height>",
                            help="pyramid digraph")

        gr=parser.add_argument_group("I/O options")

        gr.add_argument('--savegraph'+suffix,'-sg'+suffix,
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Save the DAG to <graph_file>.
                            Setting '<graph_file>' to '-' is
                            another way to send the DAG to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat'+suffix,'-gf'+suffix,
                        choices=graph_formats()['dag'],
                        default='autodetect',
                        help="Format of the DAG file. (default: autodetect)")


    @staticmethod
    def obtain_graph(args,suffix=""):
        """Produce a DAG from either input or library
        """
        if getattr(args,'tree'+suffix) is not None:
            assert getattr(args,'tree'+suffix) > 0

            D = dag_complete_binary_tree( getattr(args,'tree'+suffix) )

        elif getattr(args,'pyramid'+suffix) is not None:
            assert getattr(args,'pyramid'+suffix) > 0

            D = dag_pyramid( getattr(args,'pyramid'+suffix))

        elif getattr(args,'graphformat'+suffix) is not None:

            try:
                print("INFO: reading directed acyclic graph {} from '{}'".format(suffix,getattr(args,"input"+suffix).name),
                      file=sys.stderr)
                D=readGraph(getattr(args,'input'+suffix),
                            "dag",
                            getattr(args,'graphformat'+suffix))
            except ValueError,e:
                print("ERROR ON '{}'. {}".format(getattr(args,'input'+suffix).name,e),file=sys.stderr)
                exit(-1)
        else:
            raise RuntimeError("Command line does not specify a directed acyclic graph")

        # Output the graph is requested
        if getattr(args,'savegraph'+suffix) is not None:
            writeGraph(D,
                       getattr(args,'savegraph'+suffix),
                       "dag",
                       getattr(args,'graphformat'+suffix))

        return D


class SimpleGraphHelper(GraphHelper):

    @staticmethod
    def setup_command_line(parser,suffix="",required=False):
        """Setup input options for command lines

        Parameters
        ----------
        parser : ArgParse parser object
            it is populated with options for input graphs

        suffix: string, optional
            add a suffix to all input options. Useful if you need to input 
            multiple graphs in the same command line (default: empty)

        require : bool, optional
            enforce that at least one input specification is required. 
            If it is not the case the standard input is the default input. 
            Not a good idea if we read multiple graphs in input.
        """

        gr=parser.add_argument_group(title="Input graph "+suffix,
                                     description="""
                                     You can either read the input graph from file according to one of
                                     the formats, or generate it using one of the included constructions.""")

        class IntFloat(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                try:
                    n, p = positive_int(values[0]),float(values[1])
                    if p>1.0 or p<0: raise ValueError('p must be a float between 0 and 1')
                except ValueError as e:
                    raise argparse.ArgumentError(self,e.message)
                setattr(args, self.dest, (n,p))

        gr=gr.add_mutually_exclusive_group(required=required)

        gr.add_argument('--input'+suffix,'-i'+suffix,
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Read the graph from <input>. 
                        Setting '<input>' to '-' reads the graph from standard
                        input.  (default: -)
                        """)

        gr.add_argument('--gnp'+suffix,nargs=2,action=IntFloat,metavar=('n','p'),
                        help="random graph according to G(n,p) model (i.e. independent edges)")


        gr.add_argument('--gnm'+suffix,type=positive_int,nargs=2,action='store',metavar=('n','m'),
                        help="random graph according to G(n,m) model (i.e. m random edges)")

        gr.add_argument('--gnd'+suffix,type=positive_int,nargs=2,action='store',metavar=('n','d'),
                        help="random d-regular graph according to G(n,d) model (i.e. d random edges per vertex)")

        gr.add_argument('--grid'+suffix,type=positive_int,nargs='+',action='store',
                        metavar=('d1','d2'),
                        help="n-dimensional grid of dimension d1 x d2 x ... ")

        gr.add_argument('--torus'+suffix,type=positive_int,nargs='+',action='store',
                        metavar=('d1','d2'),
                        help="n-dimensional torus grid of dimensions d1 x d2 x ... x dn")

        gr.add_argument('--complete'+suffix,type=positive_int,action='store',metavar="<N>",
                        help="complete graph on N vertices")
        
        gr.add_argument('--empty'+suffix,type=positive_int,action='store',metavar="<N>",
                        help="empty graph on N vertices")

        gr=parser.add_argument_group("Modifications for input graph "+suffix)
        gr.add_argument('--plantclique'+suffix,type=positive_int,action='store',metavar="<k>",
                        help="choose k vertices at random and add all edges among them")

        gr.add_argument('--addedges'+suffix,type=positive_int,action='store',metavar="<k>",
                        help="add k NEW random edges to the graph (applied last)")

        gr=parser.add_argument_group("I/O options for graph "+suffix)
        gr.add_argument('--savegraph'+suffix,'-sg'+suffix,
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Save the graph to <graph_file>.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat'+suffix,'-gf'+suffix,
                        choices=graph_formats()['simple'],
                        default='autodetect',
                        help="Format of the graph file. (default: autodetect)")




    @staticmethod
    def obtain_graph(args,suffix=""):
        """Build a Graph according to command line arguments

        Arguments:
        - `args`: command line options
        """
        if getattr(args,'gnd'+suffix) is not None:

            n,d = getattr(args,'gnd'+suffix)
            if (n*d)%2 == 1:
                raise ValueError("n * d must be even")
            G=networkx.random_regular_graph(d,n)

        elif getattr(args,'gnp'+suffix) is not None:

            n,p = getattr(args,'gnp'+suffix)
            G=networkx.gnp_random_graph(n,p)

        elif getattr(args,'gnm'+suffix) is not None:

            n,m = getattr(args,'gnm'+suffix)
            G=networkx.gnm_random_graph(n,m)

        elif getattr(args,'grid'+suffix) is not None:

            G=networkx.grid_graph(getattr(args,'grid'+suffix))

        elif getattr(args,'torus'+suffix) is not None:
            
            G=networkx.grid_graph(getattr(args,'torus'+suffix),periodic=True)

        elif getattr(args,'complete'+suffix) is not None:

            G=networkx.complete_graph(getattr(args,'complete'+suffix))

        elif getattr(args,'empty'+suffix) is not None:

            G=networkx.empty_graph(getattr(args,'empty'+suffix))

        elif getattr(args,'graphformat'+suffix) is not None:

            try:
                print("INFO: reading simple graph {} from '{}'".format(suffix,getattr(args,"input"+suffix).name),
                      file=sys.stderr)
                G=readGraph(getattr(args,'input'+suffix),
                            "simple",
                            getattr(args,'graphformat'+suffix))
            except ValueError,e:
                print("ERROR ON '{}'. {}".format(
                    getattr(args,'input'+suffix).name,e),
                      file=sys.stderr)
                exit(-1)
        else:
            raise RuntimeError("Command line does not specify a graph")

        # Graph modifications
        if getattr(args,'plantclique'+suffix)>1:
            cliquesize = getattr(args,'plantclique'+suffix)
            if cliquesize > G.order() :
                raise ValueError("Clique cannot be larger than graph")

            clique=random.sample(G.nodes(),cliquesize)

            for v,w in combinations(clique,2):
                G.add_edge(v,w)

        if getattr(args,'addedges'+suffix)>0:
            k = getattr(args,'addedges'+suffix)
            G.add_edges_from(sample_missing_edges(G,k))
            if hasattr(G, 'name'):
                G.name = "{} with {} new random edges".format(G.name,k)

        # Output the graph is requested
        if getattr(args,'savegraph'+suffix) is not None:
            writeGraph(G,
                       getattr(args,'savegraph'+suffix),
                       'simple',
                       getattr(args,'graphformat'+suffix))

        return G


class BipartiteGraphHelper(GraphHelper):

    @staticmethod
    def setup_command_line(parser,suffix="",required=False):
        """Setup input options for reading bipartites on command lines

        Parameters
        ----------
        parser : ArgParse parser object
            it is populated with options for input graphs

        suffix: string, optional
            add a suffix to all input options. Useful if you need to input 
            multiple graphs in the same command line (default: empty)

        require : bool, optional
            enforce that at least one input specification is required. 
            If it is not the case the standard input is the default input. 
            Not a good idea if we read multiple graphs in input.
        """

        class IntIntFloat(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                try:
                    l,r,p = positive_int(values[0]),positive_int(values[1]),float(values[2])
                    if not 0.0 <= p <= 1.0:
                        raise ValueError('p must be a float between 0 and 1')
                except ValueError as e:
                    raise argparse.ArgumentError(self,e.message)
                setattr(args, self.dest, (l,r,p))

        class BipartiteRegular(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                try:
                    l,r,d = positive_int(values[0]),positive_int(values[1]),positive_int(values[2])
                    if d > r :
                        raise ValueError('In a regular bipartite graph, left degree d is at most r.')
                    if (d*l % r) != 0 :
                        raise ValueError('In a regular bipartite graph, r must divide d*l.')
                except ValueError as e:
                    raise argparse.ArgumentError(self,e.message)
                setattr(args, self.dest, (l,r,d))

        class BipartiteEdge(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                try:
                    l,r,m = positive_int(values[0]),positive_int(values[1]),positive_int(values[2])
                    if m > r*l :
                        raise ValueError('In a bipartite graph, #edges is at most l*r.')
                except ValueError as e:
                    raise argparse.ArgumentError(self,e.message)
                setattr(args, self.dest, (l,r,m))

        class BipartiteShift(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                try:

                    if len(values)<2:
                        raise ValueError("'bshift' requires two positive int parameters or more.")

                    
                    N,M,pattern= values[0],values[1],sorted(values[2:])

                    for i in range(len(pattern)-1):
                        if pattern[i] == pattern[i+1]:
                            raise ValueError("no repetitions is allowed in the edge pattern.")

                    if N<1 or M<1:
                        raise ValueError("matrix dimensions N and M must be positive.")

                    if any([ x < 1 or x > M for x in pattern]):
                        raise ValueError("in v(1),v(2)... we need 1 <= v(i) <= M.")
                    
                except ValueError as e:
                    raise argparse.ArgumentError(self,e.message)
                setattr(args, self.dest, (N,M,pattern))

        class BipartiteLeft(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                try:
                    l,r,d = positive_int(values[0]),positive_int(values[1]),positive_int(values[2])
                    if d > r :
                        raise ValueError('In a bipartite graph, left degree d is at most r.')
                except ValueError as e:
                    raise argparse.ArgumentError(self,e.message)
                setattr(args, self.dest, (l,r,d))

        gr=parser.add_argument_group("Bipartite graph structure "+suffix,
                                     description="""
                                     The structure of this CNF formula depends on a bipartite graph, which
                                     can be read from file (in one of the supported format), or generated
                                     using one of the included constructions.""")

        gr=gr.add_mutually_exclusive_group(required=False)


        gr.add_argument('--input'+suffix,'-i'+suffix,
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Read the graph from file. Setting '<input>' to '-' is
                        another way to read from standard input.  (default: -)
                        """)

                
        gr.add_argument('--bp'+suffix,nargs=3,action=IntIntFloat,metavar=('l','r','p'),
                        help="Random bipartite graph with independent edges")

        gr.add_argument('--bm'+suffix,type=positive_int,nargs=3,action=BipartiteEdge,metavar=('l','r','m'),
                        help="Bipartite graph with m random edges")

        gr.add_argument('--bd'+suffix,type=positive_int,nargs=3,action=BipartiteLeft,metavar=('l','r','d'),
                        help="Bipartite graph with d random edges per left vertex")

        gr.add_argument('--bregular'+suffix,nargs=3,action=BipartiteRegular,metavar=('l','r','d'),
                        help="Bipartite regular graph, with d random edges per left vertex.")

        gr.add_argument('--bshift'+suffix,type=positive_int,nargs='*',action=BipartiteShift,metavar=('N'),
                        help="Args <N> <M> <v1> <v2> ... NxM bipartite. Vertex i connexted to i+v1, i+v2,... (mod M)")

        gr.add_argument('--bcomplete'+suffix,type=positive_int,nargs=2,action='store',metavar=('l','r'),
                        help="Complete bipartite graph")


        gr=parser.add_argument_group("Modify the graph structure")
        
        gr.add_argument('--plantbiclique'+suffix,type=positive_int,nargs=2,action='store',metavar=('l','r'),
                        help="Plant a random (l,r)-bipartite clique")

        gr.add_argument('--addedges'+suffix,type=positive_int,action='store',metavar="<k>",
                        help="Add k NEW random edges to the graph (applied in the end)")

        gr=parser.add_argument_group("File I/O options",
                                     description=""" 
                                     Additional option regarding the input and output of the files
                                     containing the graph structure.
                                     """)
        gr.add_argument('--savegraph'+suffix,'-sg'+suffix,
                        type=argparse.FileType('wb',0),
                        metavar="<graph_file>",
                        default=None,
                        help="""Save the graph to <graph_file>. Setting '<graph_file>' to '-'sends
                        the graph to standard output. (default: -) """)
        gr.add_argument('--graphformat'+suffix,'-gf'+suffix,
                        choices=graph_formats()['bipartite'],
                        default='autodetect',
                        help="Format of the graph file. (default: autodetect)")


    @staticmethod
    def obtain_graph(args,suffix=""):
        """Build a Bipartite graph according to command line arguments

        Arguments:
        - `args`: command line options
        """

        if getattr(args,"bp"+suffix) is not None:

            l,r,p = getattr(args,"bp"+suffix)
            G=bipartite_random_graph(l,r,p)

        elif getattr(args,"bm"+suffix)  is not None:

            l,r,m = getattr(args,"bm"+suffix)
            G=bipartite_gnmk_random_graph(l,r,m)

        elif getattr(args,"bd"+suffix) is not None:

            l,r,d = getattr(args,"bd"+suffix)
            G=bipartite_random_left_regular(l,r,d)

        elif getattr(args,"bregular"+suffix)  is not None:

            l,r,d = getattr(args,"bregular"+suffix)
            G=bipartite_random_regular(l,r,d)

        elif getattr(args,"bshift"+suffix) is not None:

            N,M,pattern = getattr(args,"bshift"+suffix)
            G=bipartite_shift(N,M,pattern)
            
        elif getattr(args,"bcomplete"+suffix) is not None:
            
            l,r = getattr(args,"bcomplete"+suffix)
            G=complete_bipartite_graph(l,r)
            # Workaround: the bipartite labels are missing in old version of networkx
            for i in range(0,l):
                G.add_node(i,bipartite=0)
            for i in range(l,l+r):
                G.add_node(i,bipartite=1)
            
        elif getattr(args,"graphformat"+suffix) is not None:

            try:
                print("INFO: reading bipartite graph {} from '{}'".format(suffix,getattr(args,"input"+suffix).name),
                      file=sys.stderr)
                G=readGraph(getattr(args,"input"+suffix),
                            "bipartite",
                            getattr(args,"graphformat"+suffix))
            except ValueError,e:
                print("ERROR ON '{}'. {}".format(getattr(args,"input"+suffix).name,e),file=sys.stderr)
                exit(-1)
                            
        else:
            raise RuntimeError("Command line does not specify a bipartite graph")
            
        

        # Graph modifications
        if getattr(args,"plantbiclique"+suffix) is not None:
            l,r = getattr(args,"plantbiclique"+suffix)
            left,right = bipartite_sets(G)
            if l > len(left) or r > len(right) :
                raise ValueError("Clique cannot be larger than graph")

            left = random.sample(left, l)
            right = random.sample(right, r)

            for v,w in product(left,right):
                G.add_edge(v,w)

        if getattr(args,"addedges"+suffix) is not None:

            k = getattr(args,"addedges"+suffix)

            G.add_edges_from(sample_missing_edges(G,k))

            if hasattr(G, 'name'):
                G.name = "{} with {} new random edges".format(G.name,k)
            
            
        # Output the graph is requested
        if getattr(args,"savegraph"+suffix) is not None:
            writeGraph(G,
                       getattr(args,"savegraph"+suffix),
                       'bipartite',
                       getattr(args,"graphformat"+suffix))

        return G
