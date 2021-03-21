Graph based formulas
====================

The  most  interesting  benchmark  formulas have  a  graph  structure.
See the following  example, where :py:func:`cnfgen.TseitinFormula`
is realized over a star graph with five arms.


   >>> import cnfgen
   >>> from pprint import pprint
   >>> G = cnfgen.Graph.star_graph(5)
   >>> list(G.edges())
   [(1, 6), (2, 6), (3, 6), (4, 6), (5, 6)]
   >>> F = cnfgen.TseitinFormula(G,charges=[0,1,0,0,1,0])
   >>> pprint(F.solve())
   (True, [-1, 2, -3, -4, 5])

Tseitin formulas can  be really hard for if the  graph has large `edge
expansion <https://en.wikipedia.org/wiki/Expander_graph>`_. Indeed the
unsatisfiable  version of  this formula  requires exponential  running
time in any resolution based SAT solver [1]_.
     
In  the  previous example  the  structure  of  the  CNF was  a  simple
undirected graph, but in ``CNFgen`` we have formulas built around four
different types of graphs.

+---------------+------------------------+-------------------------------------------------+
| ``simple``    | simple graph           | default graph                                   |
+---------------+------------------------+-------------------------------------------------+
| ``bipartite`` | bipartite graph        | vertices split in two inpedendent sets          |
+---------------+------------------------+-------------------------------------------------+
| ``digraph``   | directed graph         | each edge has an orientation                    |
+---------------+------------------------+-------------------------------------------------+
| ``dag``       | directed acyclic graph | no cycles, edges induce a partial ordering      |
+---------------+------------------------+-------------------------------------------------+

Internally,  vertices  of  these  graphs  are  identified  as  integer
starting from 1.  Edges are pairs of integers and  in general the data
structure  is such  that edge  lists  and neighborhoods  are given  in
a sorted fashion.
- :py:class:`cnfgen.Graph` to represent undirected graphs ``simple``.
- :py:class:`cnfgen.DirectedGraph`:   to   represent  directed  graphs
  ``digraph``  and  ``dag``  (directed   acyclic  graphs).  A  DAG  is
  a `DirectedGraph` where all edges go from vertices with loweer id to
  vertices  with higher  id. Therefore  the ids  of the  vertices must
  represent a topological  order of the DAG. In  particular a directed
  graph  maybe acyclic  but yet  not considered  a dag  in ``CNFgen``.
  The method :py:method:`cnfgen.DirectedGraph.is_dag`  checks that the
  directed graph is indeed a DAG according to this standard.
- :py:class:`cnfgen.BipartiteGraph` represents  graph of ``bipartite``
  type. The vertices are divided in two parts (left and right) and the
  vertices in each part are enumerated  from 1. For example in a graph
  with 10 vertices on the left side  and 4 vertices on the right side,
  the edge  ``(6,3)`` connects  vertex ``6`` on  the left  with vertex
  ``4`` on  the right. Similarly  edge ``(2,2)`` connects vertex  2 on
  the left to vertex 2 on the right.



Directed Acyclic Graphs
--------------------------------------------

In     ``CNFgen``     a    DAG     is     an     object    of     type
:py:class:`cnfgen.DirectedGraph`  which  furthermore passes  the  test
:py:func:`cnfgen.DirectedGraph.is_dag`.  We stress  that the  vertices
numeric id must induce a topological order for the graph to be a dag.

   >>> from cnfgen import DirectedGraph
   >>> G = DirectedGraph(3)
   >>> G.add_edges_from([(1,2),(2,3),(3,1)])
   >>> G.is_dag()
   False
   >>> H = DirectedGraph(4)
   >>> H.add_edges_from([(1,2),(2,3),(3,4)])
   >>> H.is_dag()
   True
   >>> Z = DirectedGraph(4)
   >>> Z.add_edges_from([(1,2),(3,2)])
   >>> Z.is_dag()
   False

Bipartite Graphs
----------------   

We represent bipartite graphs using :py:class:`cnfgen.BipartiteGraph`.

   >>> B = cnfgen.graphs.BipartiteGraph(2,3)
   >>> B.left_order()
   2
   >>> B.right_order()
   3
   >>> B.order()
   5
   >>> B.add_edges_from([(1,2),(2,1),(2,3)])
   >>> B.number_of_edges()
   3
   >>> F = cnfgen.GraphPigeonholePrinciple(B)
   >>> sorted(F.all_variable_labels())
   ['p_{1,2}', 'p_{2,1}', 'p_{2,3}']
   
Graph I/O
---------

Furthermore ``CNFgen``  allows graphs  I/O on  files, in  few formats.
The function :py:func:`cnfgen.supported_graph_formats` lists the file
formats available for each graph type.

   >>> from cnfgen import supported_graph_formats
   >>> from pprint import pprint
   >>> pprint(supported_graph_formats())
   {'bipartite': ['kthlist', 'gml', 'dot', 'matrix'],
    'dag': ['kthlist', 'gml', 'dot', 'dimacs'],
    'digraph': ['kthlist', 'gml', 'dot', 'dimacs'],
    'simple': ['kthlist', 'gml', 'dot', 'dimacs']}

The  ``dot`` and  ``gml`` formats  are read  using NetworkX_  library,
which is a powerful library  for graph manipulation. The support
for the other formats is natively implemented.

The ``dot``  format is is from  Graphviz_ and it is  available only if
the  optional ``pydot``  python package  is installed  in the  system.
The Graph  Modelling Language  (GML_) ``gml``  is a  modern industrial
standard in graph representation. The DIMACS_ (``dimacs``) format [2]_
is used sometimes  for programming competitions or  in the theoretical
computer science  community. For  more informations  about ``kthlist``
and ``matrix`` formats you can refer to the `User Documentation`_.

To    facilitate   graph    I/O    ``CNFgen``    has   to    functions
:py:func:`cnfgen.graphs.readGraph`                                 and
:py:func:`cnfgen.graphs.writeGraph`.

Both  ``readGraph`` and  ``writeGraph`` operate  either on  filenames,
encoded as `str`, or on file-like objects such as

   + standard file objects (including :py:obj:`sys.stdin` and :py:obj:`sys.stdout`);
   + string buffers of type :py:class:`io.StringIO`;
   + in-memory text streams that inherit from :py:class:`io.TextIOBase`.
     
   >>> import sys
   >>> from io import BytesIO
   >>> import networkx as nx
   >>> from cnfgen import readGraph, writeGraph, BipartiteGraph

   >>> G = BipartiteGraph(3,3,name='a bipartite graph')
   >>> G.add_edges_from([[1,1],[1,2],[2,3]])
   >>> G.number_of_edges()
   3
   >>> writeGraph(G,sys.stdout,graph_type='bipartite',file_format='gml')
   graph [
     name "a bipartite graph"
     node [
       id 0
       label "1"
       bipartite 0
     ]
     node [
       id 1
       label "2"
       bipartite 0
     ]
     node [
       id 2
       label "3"
       bipartite 0
     ]
     node [
       id 3
       label "4"
       bipartite 1
     ]
     node [
       id 4
       label "5"
       bipartite 1
     ]
     node [
       id 5
       label "6"
       bipartite 1
     ]
     edge [
       source 0
       target 3
     ]
     edge [
       source 0
       target 4
     ]
     edge [
       source 1
       target 5
     ]
   ]
   <BLANKLINE>
   >>> from io import StringIO
   >>> textbuffer = StringIO("graph X { 1 -- 2 -- 3 }")
   >>> G = readGraph(textbuffer, graph_type='simple', file_format='dot')
   >>> E = G.edges()
   >>> (1, 2) in E
   True
   >>> (2, 3) in E
   True
   >>> (1, 3) in E
   False
   
There are  several advantages with  using those functions,  instead of
the reader/writer  implemented ``NextowrkX``. First of  all the reader
always  verifies that  when reading  a graph  of a  certain type,  the
actual input  actually matches the type.  For example if the  graph is
supposed  to  be  a DAG,  then  :py:func:`cnfgen.graphs.readGraph`
would check that.

   >>> buffer = StringIO('digraph A { 1 -- 2 -- 3 -- 1}')
   >>> readGraph(buffer,graph_type='dag',file_format='dot')
   Traceback (most recent call last):
   ...
   ValueError: [Input error] Graph must be explicitly acyclic ...

When the  file object has an  associated file name, it  is possible to
omit the ``file_format`` argument. In this latter case the appropriate
choice of format  will be guessed by the file  extension.

   >>> with open(tmpdir+"example_dag1.dot","w") as f:
   ...     print("digraph A {1->2->3}",file=f)
   >>> G = readGraph(tmpdir+"example_dag1.dot",graph_type='dag')
   >>> list(G.edges())
   [(1, 2), (2, 3)]

is equivalent to
   
   >>> with open(tmpdir+"example_dag2.gml","w") as f:
   ...     print("digraph A {1->2->3}",file=f)
   >>> G = readGraph(tmpdir+"example_dag2.gml",graph_type='dag',file_format='dot')
   >>> list(G.edges())
   [(1, 2), (2, 3)]

Instead, if we omit the format and the file extension is misleading we
would get and error.
   
   >>> with open(tmpdir+"example_dag3.gml","w") as f:
   ...     print("digraph A {1->2->3}",file=f)
   >>> G = readGraph(tmpdir+"example_dag3.gml",graph_type='dag')
   Traceback (most recent call last):
   ...
   ValueError: [Parse error in GML input] ...

This is an example of GML file.
   
   >>> gml_text ="""graph [
   ...               node [
   ...                 id 1
   ...                 label "a"
   ...               ]
   ...               node [
   ...                 id 2
   ...                 label "b"
   ...               ]
   ...               edge [
   ...                 source 1
   ...                 target 2
   ...               ]
   ...             ]"""
   >>> with open(tmpdir+"example_ascii.gml","w",encoding='ascii') as f:
   ...     print(gml_text,file=f)
   >>> G = readGraph(tmpdir+"example_ascii.gml",graph_type='simple')
   >>> (1,2) in G.edges()
   True

Recall that GML files are supposed to be ASCII encoded. 

   >>> gml_text2="""graph [
   ...               node [
   ...                 id 0
   ...                 label "à"
   ...               ]
   ...               node [
   ...                 id 1
   ...                 label "è"
   ...               ]
   ...               edge [
   ...                 source 0
   ...                 target 1
   ...               ]
   ...             ]"""

   >>> with open(tmpdir+"example_utf8.gml","w",encoding='utf-8') as f:
   ...     print(gml_text2,file=f)
   >>> G = readGraph(tmpdir+"example_utf8.gml",graph_type='dag')
   Traceback (most recent call last):
   ...
   ValueError: [Non-ascii chars in GML file] ...

Graph generators
----------------
.. note::

   See  the documentation  of the  module :py:mod:`cnfgen.graphs`
   for more information about the ``CNFgen`` support code for graphs.


.. _`User Documentation`: http://massimolauria.net/cnfgen/graphformats.html
.. _cnfgengraph: http://massimolauria.net/cnfgen/graphformats.html
.. _DIMACS: http://prolland.free.fr/works/research/dsat/dimacs.html
.. _GML: http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html
.. _Graphviz: http://www.graphviz.org/content/dot-language
.. _NetworkX: https://networkx.github.io/


   
References
----------

.. [1] A.  Urquhart. `Hard  examples for  resolution`. Journal  of the
       ACM (1987) http://dx.doi.org/10.1145/48014.48016

.. [2] Beware. Here we are talking about the DIMACS format for graphs, not the
       DIMACS file format for CNF formulas.

.. [3] This convention is describe in 
       http://networkx.readthedocs.org/en/latest/reference/algorithms.bipartite.html

