#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Components for command line interface

CNFgen has many command line entry points to its functionality, and
some of them expose the same functionality over and over. This module
contains useful common components.

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

from __future__ import print_function

import argparse

import networkx 
from .graphs import supported_formats as graph_formats
from .graphs import readGraph,writeGraph
from .graphs import bipartite_random_left_regular,bipartite_random_regular

import sys


__all__ = [ "is_formula_cmdhelper",
            "DirectedAcyclicGraphHelper", "SimpleGraphHelper", "BipartiteGraphHelper"]




def is_formula_cmdhelper(obj):
    """Test whether the object is a formula command line helper

    Any object that passes this test should be a suitable
    implementation of a CNFgen subcommand that generates
    a formula family.

    In particular the object must have four attributes
    
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
    obj : any
        the object to test

    Returns
    -------
    None

    """
    return \
        hasattr(obj,'build_cnf') and \
        hasattr(obj,'setup_command_line') and \
        hasattr(obj,'name') and \
        hasattr(obj,'description')


### Graph readers/generators

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
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group(title="Input directed acyclic graph (DAG)",
                                     description="""
                                     You can either read the input DAG from file according to one of
                                     the formats, or generate it using one of the constructions included.""")

        gr=gr.add_mutually_exclusive_group()
       
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Read the DAG from <input>. Setting '<input>' to '-' is another way
                        to read from standard input. (default: -) """)

        gr.add_argument('--tree',type=int,action='store',metavar="<height>",
                            help="rooted tree digraph")

        gr.add_argument('--pyramid',type=int,action='store',metavar="<height>",
                            help="pyramid digraph")

        gr=parser.add_argument_group("I/O options")

        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Save the DAG to <graph_file>.
                            Setting '<graph_file>' to '-' is
                            another way to send the DAG to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=graph_formats()['dag'],
                        default='autodetect',
                        help="Format of the DAG file. (default: autodetect)")

 
    @staticmethod
    def obtain_graph(args):
        """Produce a DAG from either input or library
        """
        if hasattr(args,'tree') and args.tree>0:

            D=networkx.DiGraph()
            D.ordered_vertices=[]
            # vertices
            vert=['v_{}'.format(i) for i in range(1,2*(2**args.tree))]
            for w in vert:
                D.add_node(w)
                D.ordered_vertices.append(w)
            # edges
            N=len(vert)-1
            for i in range(len(vert)//2):
                D.add_edge(vert[N-2*i-1],vert[N-i])
                D.add_edge(vert[N-2*i-2],vert[N-i])

        elif hasattr(args,'pyramid') and args.pyramid>0:

            D=networkx.DiGraph()
            D.name='Pyramid of height {}'.format(args.pyramid)
            D.ordered_vertices=[]

            # vertices
            X=[ [('x_{{{},{}}}'.format(h,i),h,i) for i in range(args.pyramid-h+1)] \
                for h in range(args.pyramid+1) ]

            for layer in X:
                for (name,h,i) in layer:
                    D.add_node(name,rank=(h,i))
                    D.ordered_vertices.append(name)

            # edges
            for h in range(1,len(X)):
                for i in range(len(X[h])):
                    D.add_edge(X[h-1][i][0]  ,X[h][i][0])
                    D.add_edge(X[h-1][i+1][0],X[h][i][0])

        elif args.graphformat:

            try:
                D=readGraph(args.input,"dag",args.graphformat)
            except ValueError,e:
                print("ERROR ON '{}'. {}".format(args.input.name,e),file=sys.stderr)
                exit(-1)
        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(D,
                       args.savegraph,
                       "dag",
                       args.graphformat)

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
                v=ValueError('n must be integer and p must be a float between 0 and 1')
                try:
                    n, p = int(values[0]),float(values[1])
                    if p>1.0 or p<0: raise ValueError('p must be a float between 0 and 1')
                except ValueError:
                    raise v
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


        gr.add_argument('--gnm'+suffix,type=int,nargs=2,action='store',metavar=('n','m'),
                            help="random graph according to G(n,m) model (i.e. m random edges)")

        gr.add_argument('--gnd'+suffix,type=int,nargs=2,action='store',metavar=('n','d'),
                            help="random d-regular graph according to G(n,d) model (i.e. d random edges per vertex)")

        gr.add_argument('--grid'+suffix,type=int,nargs='+',action='store',metavar=('d1','d2'),
                        help="n-dimensional grid of dimension d1 x d2 x ... ")

        gr.add_argument('--torus'+suffix,type=int,nargs='+',action='store',metavar=('d1','d2'),
                        help="n-dimensional torus grid of dimensions d1 x d2 x ... x dn")

        gr.add_argument('--complete'+suffix,type=int,action='store',metavar="<N>",
                            help="complete graph on N vertices")

        gr=parser.add_argument_group("Modifications for input graph "+suffix)
        gr.add_argument('--plantclique'+suffix,type=int,action='store',metavar="<k>",
                            help="choose k vertices at random and add all edges among them")

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
        if hasattr(args,'gnd'+suffix) and getattr(args,'gnd'+suffix):

            n,d = getattr(args,'gnd'+suffix)
            if (n*d)%2 == 1:
                raise ValueError("n * d must be even")
            G=networkx.random_regular_graph(d,n)

        elif hasattr(args,'gnp'+suffix) and getattr(args,'gnp'+suffix):

            n,p = getattr(args,'gnp'+suffix)
            G=networkx.gnp_random_graph(n,p)

        elif hasattr(args,'gnm'+suffix) and getattr(args,'gnm'+suffix):

            n,m = getattr(args,'gnm'+suffix)
            G=networkx.gnm_random_graph(n,m)

        elif hasattr(args,'grid'+suffix) and getattr(args,'grid'+suffix):

            G=networkx.grid_graph(getattr(args,'grid'+suffix))

        elif hasattr(args,'torus'+suffix) and getattr(args,'torus'+suffix):
            
            G=networkx.grid_graph(getattr(args,'torus'+suffix),periodic=True)

        elif hasattr(args,'complete'+suffix) and getattr(args,'complete'+suffix)>0:

            G=networkx.complete_graph(getattr(args,'complete'+suffix))

        elif getattr(args,'graphformat'+suffix):

            try:
                G=readGraph(getattr(args,'input'+suffix),
                            "simple",
                            getattr(args,'graphformat'+suffix))
            except ValueError,e:
                print("ERROR ON '{}'. {}".format(
                    getattr(args,'input'+suffix).name,e),
                    file=sys.stderr)
                exit(-1)
        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Graph modifications
        if hasattr(args,'plantclique'+suffix) and getattr(args,'plantclique'+suffix)>1:

            clique=random.sample(G.nodes(),getattr(args,'plantclique'+suffix))

            for v,w in combinations(clique,2):
                G.add_edge(v,w)

        # Output the graph is requested
        if hasattr(args,'savegraph'+suffix) and getattr(args,'savegraph'+suffix):
            writeGraph(G,
                       getattr(args,'savegraph'+suffix),
                       'simple',
                       getattr(args,'graphformat'+suffix))

        return G


class BipartiteGraphHelper(GraphHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group(title="Input bipartite graph",
                                     description="""
                                     You can either read the input bipartite graph from file according to one of
                                     the formats, or generate it using one of the included constructions.""")

        class IntIntFloat(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                l,r,p = int(values[0]),int(values[1]),float(values[2])
                if not isinstance(l,int):
                    raise ValueError('l must be an integer')
                if not isinstance(r,int):
                    raise ValueError('r must be an integer')
                if not (isinstance(p,float) and p<=1.0 and p>=0):
                    raise ValueError('p must be an float between 0 and 1')
                setattr(args, self.dest, (l,r,p))

        class BipartiteRegular(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                l,r,d = int(values[0]),int(values[1]),int(values[2])
                if not isinstance(l,int):
                    raise ValueError('l must be an integer')
                if not isinstance(r,int):
                    raise ValueError('r must be an integer')
                if not isinstance(d,int):
                    raise ValueError('d must be an integer')
                if (d*l % r) != 0 :
                    raise ValueError('In a regular bipartite graph, r must divide d*l.')
                setattr(args, self.dest, (l,r,d))

        gr=parser.add_argument_group("Read/Write the underlying bipartite graph")

        gr=gr.add_mutually_exclusive_group()


        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The graph is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)

                
        gr.add_argument('--bp',nargs=3,action=IntIntFloat,metavar=('l','r','p'),
                help="random bipartite graph according with independent edges)")


        gr.add_argument('--bm',type=int,nargs=3,action='store',metavar=('l','r','m'),
                help="random bipartite graph, with m random edges")

        gr.add_argument('--bd',type=int,nargs=3,action='store',metavar=('l','r','d'),
                help="random bipartite d-left-regular graph, with d random edges per left vertex)")

        gr.add_argument('--bregular',nargs=3,action=BipartiteRegular,metavar=('l','r','d'),
                help="random (l,r)-bipartite regular graph, with d edges per left vertex.")

        gr.add_argument('--bcomplete',type=int,nargs=2,action='store',metavar=('l','r'),
                help="complete bipartite graph")

        gr=parser.add_argument_group("I/O options")
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Save the graph to <graph_file>. Setting '<graph_file>' to '-'sends
                            the graph to standard output. (default: -) """)
        gr.add_argument('--graphformat','-gf',
                        choices=graph_formats()['bipartite'],
                        default='autodetect',
                        help="Format of the graph file. (default: autodetect)")


    @staticmethod
    def obtain_graph(args):
        """Build a Bipartite graph according to command line arguments

        Arguments:
        - `args`: command line options
        """
        if hasattr(args,'bp') and args.bp:

            l,r,p = args.bp
            G=networkx.bipartite_random_graph(l,r,p)

        elif hasattr(args,'bm') and args.bm:

            l,r,m = args.bm
            G=networkx.bipartite_gnmk_random_graph(l,r,m)

        elif hasattr(args,'bd') and args.bd:

            l,r,d = args.bd
            G=bipartite_random_left_regular(l,r,d)

        elif hasattr(args,'bregular') and args.bregular:

            l,r,d = args.bregular
            G=bipartite_random_regular(l,r,d)

        elif hasattr(args,'bcomplete') and args.bcomplete:
            
            l,r = args.bcomplete
            G=networkx.complete_bipartite_graph(l,r)

        elif getattr(args,'graphformat'):

            try:
                G=readGraph(args.input, "bipartite", args.graphformat)
            except ValueError,e:
                print("ERROR ON '{}'. {}".format(args.input.name,e),file=sys.stderr)
                exit(-1)
                            
        else:
            raise RuntimeError("Invalid graph specification on command line")
            
        # Ensure the bipartite labels
        from cnfformula import graphs
        graphs._bipartite_nx_workaroud(G)
        
        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(G,
                       args.savegraph,
                       'bipartite',
                       args.graphformat)

        return G
