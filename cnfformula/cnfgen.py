#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import os

from . import CNF
from . import TransformFormula,available_transform

from .graphs import supported_formats as graph_formats
from .graphs import readDigraph,readGraph,writeGraph
from .graphs import bipartite_random_left_regular,bipartite_random_regular
from .graphs import has_bipartition


from .families import *


__docstring__ =\
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git


Create you own CNFs:

>>> c=CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], \
          [(False,"x2"),(True,"x4")] ])
>>> print( c.dimacs(False) )
p cnf 4 2
1 2 -3 0
-2 4 0

You can add clauses later in the process:

>>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
>>> print( c.dimacs(add_header=False))
p cnf 5 3
1 2 -3 0
-2 4 0
-3 4 -5 0

"""

import sys

from itertools import combinations

# Python 2.6 does not have argparse library
try:
    import argparse
except ImportError:
    print("Sorry: %s requires `argparse` library, which is missing.\n"%argv[0],file=sys.stderr)
    print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
    print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
    print(" * http://code.google.com/p/argparse",file=sys.stderr)
    print("",file=sys.stderr)
    exit(-1)

import random

try:
    import networkx
    import networkx.algorithms
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",file=sys.stderr)
    exit(-1)

#################################################################
#          Command line tool follows
#################################################################


class HelpTransformAction(argparse.Action):
    def __init__(self, **kwargs):
        super(HelpTransformAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        print("""
        Formula transformations available
        """)
        for k,entry in available_transform().iteritems():
            print("{}\t:  {}".format(k,entry[0]))
        print("\n")
        sys.exit(0)

###
### Command line helpers
###

class _CMDLineHelper(object):
    """Base Command Line helper

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def setup_command_line(parser):
        """Add command line options for this family of formulas
        """
        pass

    @staticmethod
    def additional_options_check(args):
        pass


class _GeneralCommandLine(_CMDLineHelper):
    """Command Line helper for the general commands

    For every formula family there should be a subclass.
    """

    @staticmethod
    def setup_command_line(parser):
        """Setup general command line options

        Arguments:
        - `parser`: parser to fill with options
        """
        parser.add_argument('--output','-o',
                            type=argparse.FileType('wb',0),
                            metavar="<output>",
                            default='-',
                            help="""Save the formula to <output>. Setting '<output>' to '-' sends the
                            formula to standard output. (default: -)
                            """)
        parser.add_argument('--output-format','-of',
                            choices=['latex','dimacs'],
                            default='dimacs',
                            help="""
                            Output format of the formulas. 'latex' is
                            convenient to insert formulas into papers, and
                            'dimacs' is the format used by sat solvers.
                            (default: dimacs)
                            """)

        parser.add_argument('--seed','-S',
                            metavar="<seed>",
                            default=None,
                            type=str,
                            action='store',
                            help="""Seed for any random process in the
                            program. (default: current time)
                            """)
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--verbose', '-v',action='store_true',default=True,
                       help="""Output formula header and comments.""")
        g.add_argument('--quiet', '-q',action='store_false',dest='verbose',
                       help="""Output just the formula with no header.""")
        parser.add_argument('--Transform','-T',
                            metavar="<transformation method>",
                            choices=available_transform().keys(),
                            default='none',
                            help="""
                            Transform the CNF formula to make it harder.
                            See `--help-transform` for more information
                            """)
        parser.add_argument('--Tarity','-Ta',
                            metavar="<transformation arity>",
                            type=int,
                            default=None,
                            help="""
                            Hardness parameter for the transformation procedure.
                            See `--help-transform` for more informations
                            """)
        parser.add_argument('--help-transform',nargs=0,action=HelpTransformAction,help="""
                             Formula can be made harder applying some
                             so called "transformation procedures".
                             This gives information about the implemented transformation.
                             """)


### Graph readers/generators

class _GraphHelper(object):
    """Command Line helper for reading graphs
    """

    @staticmethod
    def obtain_graph(args):
        raise NotImplementedError("Graph Input helper must be subclassed")


class _DAGHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group(title="Input directed acyclic graph (DAG)",
                                     description="""
                                     You can either read the input DAG from file according to one of
                                     the formats, or generate it using one of the constructions included.""")

        gr=gr.add_mutually_exclusive_group(required=True)
       
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
                        default=graph_formats()['dag'][0],
                        help="""
                        Format of the DAG file. (default:  {})
                        """.format(graph_formats()['dag'][0]))

 
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
            X=[
                [('x_{{{},{}}}'.format(h,i),h,i) for i in range(args.pyramid-h+1)]
                for h in range(args.pyramid+1)
              ]

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

            D=readDigraph(args.input,args.graphformat)

        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(D,
                       args.savegraph,
                       args.graphformat,
                       graph_type='dag')

        return D


class _SimpleGraphHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser,suffix=""):
        """Setup input options for command lines
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

        gr=gr.add_mutually_exclusive_group(required=True)

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
                        default=graph_formats()['simple'][0],
                        help="""
                        Format of the graph file. (default:  {})
                        """.format(graph_formats()['simple'][0]))




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

            G=readGraph(getattr(args,'input'+suffix),
                        getattr(args,'graphformat'+suffix))
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
                       getattr(args,'graphformat'+suffix),
                       graph_type='simple')

        return G


class _BipartiteGraphHelper(_GraphHelper,_CMDLineHelper):

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

        gr=gr.add_mutually_exclusive_group(required=True)


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
                        default=graph_formats()['bipartite'][0],
                        help="""
                        Format of the graph file.  (default:  {})
                        """.format(graph_formats()['bipartite'][0]))


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

            G=readGraph(args.input,
                        args.graphformat)

            if not has_bipartition(G): 
                raise ValueError("Input Error: graph vertices miss the 'bipartite' 0,1 label.")
                    
        else:
            raise RuntimeError("Invalid graph specification on command line")
            
        # Ensure the bipartite labels
        from cnfformula import graphs
        graphs._bipartite_nx_workaroud(G)
        
        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(G,
                       args.savegraph,
                       args.graphformat,
                       graph_type='bipartite')

        return G

    
### Formula families

class _FormulaFamilyHelper(object):
    """Command Line helper for formula families

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def build_cnf(args):
        pass


class _EMPTY(_FormulaFamilyHelper,_CMDLineHelper):
    name='empty'
    description='empty CNF formula'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def build_cnf(args):
        """Build an empty CNF formula 

        Arguments:
        - `args`: command line options
        """
        return CNF()

class _EMPTY_CLAUSE(_FormulaFamilyHelper,_CMDLineHelper):
    name='emptyclause'
    description='one empty clause'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def build_cnf(args):
        """Build a CNF formula with an empty clause 

        Arguments:
        - `args`: command line options
        """
        return CNF([[]])
    
class _GPHP(_FormulaFamilyHelper,_CMDLineHelper):
    name='gphp'
    description='graph pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula over graphs

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--functional',action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',action='store_true',
                            help="every hole has a sitting pigeon")
        _BipartiteGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = _BipartiteGraphHelper.obtain_graph(args) 
        return GraphPigeonholePrinciple(G,
                                        functional=args.functional,
                                        onto=args.onto)

class _SSC(_FormulaFamilyHelper,_CMDLineHelper):
    name='subsetcard'
    description='subset cardinality formulas'

    @staticmethod
    def setup_command_line(parser):
        _BipartiteGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        B = _BipartiteGraphHelper.obtain_graph(args)
        return SubsetCardinalityFormula(B)

    
class _MARKSTROM(_FormulaFamilyHelper,_CMDLineHelper):
    name='markstrom'
    description='markstrom formulas'

    @staticmethod
    def setup_command_line(parser):
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        G = _SimpleGraphHelper.obtain_graph(args) 
        return MarkstromFormula(G)

    
class _PHP(_FormulaFamilyHelper,_CMDLineHelper):
    name='php'
    description='pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('pigeons',metavar='<pigeons>',type=int,help="Number of pigeons")
        parser.add_argument('holes',metavar='<holes>',type=int,help="Number of holes")
        parser.add_argument('--functional',action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',action='store_true',
                            help="every hole has a sitting pigeon")
        parser.set_defaults(func=_PHP.build_cnf)

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PigeonholePrinciple(args.pigeons,
                                   args.holes,
                                   functional=args.functional,
                                   onto=args.onto)


class _RAM(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for RamseyNumber formulas
    """
    name='ram'
    description='ramsey number principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('s',metavar='<s>',type=int,help="Forbidden independent set size")
        parser.add_argument('k',metavar='<k>',type=int,help="Forbidden independent clique")
        parser.add_argument('N',metavar='<N>',type=int,help="Graph size")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RamseyNumber(args.s, args.k, args.N)


class _OP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Ordering principle formulas
    """
    name='op'
    description='ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return OrderingPrinciple(args.N,args.total,args.smart,args.plant,args.knuth)


class _GOP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Graph Ordering principle formulas
    """
    name='gop'
    description='graph ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Graph ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return GraphOrderingPrinciple(G,args.total,args.smart,args.plant,args.knuth)


class _PARITY(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Matching Principle formulas
    """
    name='parity'
    description='parity principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Parity Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")

    @staticmethod
    def build_cnf(args):
        return ParityPrinciple(args.N)


class _PMATCH(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Perfect Matching Principle formulas
    """
    name='matching'
    description='perfect matching principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Perfect Matching Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        G=_SimpleGraphHelper.obtain_graph(args)
        return GraphMatchingPrinciple(G)


class _COUNT(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Counting Principle formulas
    """
    name='count'
    description='counting principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Counting Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('M',metavar='<M>',type=int,help="domain size")
        parser.add_argument('p',metavar='<p>',type=int,help="size of the parts")

    @staticmethod
    def build_cnf(args):
        """Build an Counting Principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CountingPrinciple(args.M,args.p)

    
class _KClique(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for k-clique formula
    """
    name='kclique'
    description='k clique formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k)])


class _KColor(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for k-color formula
    """
    name='kcolor'
    description='k-colorability formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-color formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="number of available colors")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-colorability formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return ColoringFormula(G,range(1,args.k+1))


class _GAuto(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Graph Automorphism formula
    """
    name='gauto'
    description='graph automorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph automorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return GraphAutomorphism(G)



class _GIso(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Graph Isomorphism formula
    """
    name='giso'
    description='graph isomorphism formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for graph isomorphism formula

        Arguments:
        - `parser`: parser to load with options.
        """
        _SimpleGraphHelper.setup_command_line(parser,"1")
        _SimpleGraphHelper.setup_command_line(parser,"2")


    @staticmethod
    def build_cnf(args):
        """Build a graph automorphism formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G1 =_SimpleGraphHelper.obtain_graph(args,"1")
        G2 =_SimpleGraphHelper.obtain_graph(args,"2")
        return GraphIsomorphism(G1,G2)


    
class _RAMLB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for ramsey graph formula
    """
    name='ramlb'
    description='unsat if G witnesses that r(k,s)>|V(G)| (i.e. G has not k-clique nor s-stable)'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for ramsey witness formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        parser.add_argument('s',metavar='<s>',type=int,action='store',help="size of the stable to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k),
                                  networkx.complete_graph(args.s)])



class _TSE(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Tseitin  formulas
    """
    name='tseitin'
    description='tseitin formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Tseitin formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--charge',metavar='<charge>',default='first',
                            choices=['first','random','randomodd','randomeven'],
                            help="""charge on the vertices.
                                    `first'  puts odd charge on first vertex;
                                    `random' puts a random charge on vertices;
                                    `randomodd' puts random odd  charge on vertices;
                                    `randomeven' puts random even charge on vertices.
                                     """)
        _SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)

        if G.order()<1:
            charge=None

        elif args.charge=='first':

            charge=[1]+[0]*(G.order()-1)

        else: # random vector
            charge=[random.randint(0,1) for i in xrange(G.order()-1)]

            parity=sum(charge) % 2

            if args.charge=='random':
                charge.append(random.randint(0,1))
            elif args.charge=='randomodd':
                charge.append(1-parity)
            elif args.charge=='randomeven':
                charge.append(parity)
            else:
                raise ValueError('Illegal charge specification on command line')

        return TseitinFormula(G,charge)


class _OR(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='or'
    description='a single disjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for single or of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build an disjunction

        Arguments:
        - `args`: command line options
        """
        clause = [ (True,"x_{}".format(i)) for i in range(args.P) ] + \
                 [ (False,"y_{}".format(i)) for i in range(args.N) ]
        return CNF([clause],
                   header="""Single clause with {} positive and {} negative literals""".format(args.P,args.N))


class _RANDOM(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for random formulas
    """
    name='kcnf'
    description='random k-CNF'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,help="clause width")
        parser.add_argument('n',metavar='<n>',type=int,help="number of variables")
        parser.add_argument('m',metavar='<m>',type=int,help="number of clauses")

    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        return RandomKCNF(args.k,args.n,args.m)


class _PEB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for pebbling formulas
    """
    name='peb'
    description='pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        _DAGHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D=_DAGHelper.obtain_graph(args)
        try:
            return PebblingFormula(D)
        except ValueError:
            print("\nError: input graph must be directed and acyclic.",file=sys.stderr)
            sys.exit(-1)

class _Stone(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for stone formulas
    """
    name='stone'
    description='stone formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for stone formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        _DAGHelper.setup_command_line(parser)
        parser.add_argument('s',metavar='<s>',type=int,help="number of stones")

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D=_DAGHelper.obtain_graph(args)
        try:
            return StoneFormula(D,args.s)
        except ValueError:
            print("\nError: Input graph must be a DAG, and a non negative # of stones.",file=sys.stderr)
            sys.exit(-1)
            

            
class _AND(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='and'
    description='a single conjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        clauses = [ [(True,"x_{}".format(i))] for i in range(args.P) ] + \
                  [ [(False,"y_{}".format(i))] for i in range(args.N) ]
        return CNF(clauses,
                   header="""Singleton clauses: {} positive and {} negative""".format(args.P,args.N))


###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv=sys.argv):

    # Commands and subcommand lines
    cmdline = _GeneralCommandLine
    subcommands=[_PHP,_GPHP,
                 _TSE,
                 _OP,_GOP,
                 _KClique,
                 _KColor,
                 _RANDOM,
                 _PARITY,_PMATCH,
                 _COUNT,
                 _PEB,
                 _Stone,
                 _GIso,_GAuto,
                 _RAM,_RAMLB,
                 _MARKSTROM,
                 _SSC,
                 _OR,_AND,_EMPTY,_EMPTY_CLAUSE]

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog=os.path.basename(argv[0]),
                                   epilog="""
    Each <formula type> has its own command line arguments and options.
    For more information type 'cnfgen <formula type> [--help | -h ]'
    """)
    cmdline.setup_command_line(parser)
    subparsers=parser.add_subparsers(title="Available formula types",metavar='<formula type>')

    # Setup of various formula command lines options
    for sc in subcommands:
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(subcommand=sc)

    # Process the options
    args=parser.parse_args(argv[1:])
    cmdline.additional_options_check(args)
    args.subcommand.additional_options_check(args)

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    # Generate the basic formula
    cnf=args.subcommand.build_cnf(args)

    # Apply a formula transformation
    tcnf=TransformFormula(cnf,args.Transform,args.Tarity)


    # Do we wnat comments or not

    if args.output_format == 'latex':
        output = tcnf.latex()

    elif args.output_format == 'dimacs':
        output = tcnf.dimacs(export_header=args.verbose)
    else:
        output = tcnf.dimacs(export_header=args.verbose)

    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
