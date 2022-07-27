from cnfgen.graphs import supported_graph_formats

simple_graph_doc = """
            HOW TO SPECIFY A SIMPLE UNDIRECTED GRAPH

A graph argument on the command line is one among
  <filename>
  <fileformat> <filename>
  <construction> <arg1> <arg2> ...

examples:
 {0} ... graphfile.dot              --- graph from DOT file
 {0} ... graphfile.gml              --- graph from GML file
 {0} ... gnp 10 .5                  --- random G(n,p) graph
 {0} ... gnm 10 40 addedges 4       --- random G(n,m) graph + 4 random edges
 {0} ... grid 4 3 5 plantclique 5   --- 4x3x5 3-dimensional grid + 5-clique
 {0} ... dot -                      --- graph in DOT format from <stdin>

                  ---- Graph from a file ----
 {0} ... <filename>
 {0} ... <fileformat> <filename>

where <fileformat> is one among {formats} and
is required only when it does not match the extension of <filename>.

                 ---- Graph constructions ----

  {0} ... gnp N p               --- N vertices, p-biased independent edges
  {0} ... gnp N p t             --- t-partite with t*N vertices, p-biased edges between parts
  {0} ... gnm N m               --- N vertices, m edges at random
  {0} ... gnd N d               --- Random d-regular graph of order N
  {0} ... grid  d1 d2 d3 ...    --- d1 x d2 x d3 x ... grid graph
  {0} ... torus d1 d2 d3 ...    --- d1 x d2 x d3 x ... torus graph
  {0} ... complete N            --- complete graph of order N
  {0} ... complete N t          --- complete t-partite graph with t*N vertices
  {0} ... empty N               --- empty graph of order N

                 ---- Graph modifications ----
It is possible to enhance a graph contruction by appending one or more
of the following options to the graph specifications.

  plantclique k            --- add a randomly chosen k-clique
  addedges    m            --- add m new edges at random
  splitedges  k            --- randomly split k edges putting a vertex in between

                  ---- Saving the graph ----
For reproducibility it is possible the graph using the option

  save <filename>
  save <fileformat> <filename>

where <fileformat> is one among {formats} and
is required only when it does not match the extension of <filename>.
"""

bipartite_graph_doc = """
            HOW TO SPECIFY A BIPARTITE GRAPH

A graph argument on the command line is one among
  <filename>
  <fileformat> <filename>
  <construction> <arg1> <arg2> ...

examples:
  {0} ... bipartite.dot               --- graph from DOT file
  {0} ... bipartite.matrix            --- graph from matrix file
  {0} ... gnp 10 .5                   --- random G(n,p) graph
  {0} ... glrd 15 10 4 addedges 4     --- random 4-regular 15,10-bipartite + 4 edges
  {0} ... empty 20 20 plantbiclique 5 --- 20,20-bipartite with a random 5-clique
  {0} ... dot -                       --- graph in DOT format from <stdin>

                  ---- Graph from a file ----
  {0} ... <filename>
  {0} ... <fileformat> <filename>

where <fileformat> is one among {formats} and
is required only when it does not match the extension of <filename>.

                 ---- Graph constructions ----
       (L,R)-bipartite with L left vertices, R right vertices

  {0} ... glrp L R p            --- p-biased independent edges
  {0} ... glrm L R m            --- m edges at random
  {0} ... glrd L R d            --- d edges at random per left vertex
  {0} ... regular L R d         --- Regular bipartite. Degree d on the left
  {0} ... shift L R v1 v2 ...   --- Shift graph graph: left vertex i connected to x+v1, x+v2,...
  {0} ... complete L R          --- complete bipartite
  {0} ... empty L R             --- empty bipartite

                 ---- Graph modifications ----
It is possible to modify the previous contruction by appending one or
more of the following options to the graph specifications.

  plantbiclique A B        --- add a random biclique of size (A,B)
  addedges      m          --- add m new edges at random

                  ---- Saving the graph ----
For reproducibility it is possible the graph using the option

  save <filename>
  save <fileformat> <filename>

where <fileformat> is one among {formats} and
is required only when it does not match the extension of <filename>.
"""

dag_graph_doc = """
      HOW TO SPECIFY A DIRECTED ACYCLIC GRAPH

A graph argument on the command line is one among
  <filename>
  <fileformat> <filename>
  <construction> <arg1> <arg2> ...

examples:
  {0} ... graphfile.kthlist   --- graph from kthlist file
  {0} ... graphfile.gml       --- graph from GML file
  {0} ... tree 10             --- a complete rooted tree of height 5
  {0} ... dot -               --- graph in DOT format from <stdin>

                  ---- Graph from a file ----
  {0} ... <filename>
  {0} ... <fileformat> <filename>

where <fileformat> is one among {formats} and
is required only when it does not match the extension of <filename>.

                 ---- Graph constructions ----
  {0} ... tree h         --- complete rooted tree of height h
  {0} ... pyramid h      --- pyramid graph of height h
  {0} ... path L         --- path of length L (i.e. L+1 vertices)

                  ---- Saving the graph ----
For reproducibility it is possible the graph using the option

  save <filename>
  save <fileformat> <filename>

where <fileformat> is one among {formats} and
is required only when it does not match the extension of <filename>.
"""


def make_graph_doc(graphtype, progname):
    formats = supported_graph_formats()[graphtype]
    if graphtype == 'simple':
        return simple_graph_doc.format(progname,
                                       formats=str(formats)[1:-1])
    elif graphtype == 'bipartite':
        return bipartite_graph_doc.format(progname,
                                          formats=str(formats)[1:-1])
    elif graphtype == 'dag':
        return dag_graph_doc.format(progname,
                                    formats=str(formats)[1:-1])
    return ""
