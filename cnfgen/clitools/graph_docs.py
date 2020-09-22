from cnfgen.graphs import supported_formats

simple_graph_doc = """
an undirected simple graph, either
  - read from file; or
  - generated according to a construction.

examples:
 {prefix} graphfile.dot              --- graph from DOT file
 {prefix} graphfile.gml              --- graph from GML file
 {prefix} gnp 10 .5                  --- random G(n,p) graph
 {prefix} gnm 10 40 addedges 4       --- random G(n,m) graph + 4 random edges
 {prefix} grid 4 3 5 plantclique 5   --- 4x3x5 3-dimensional grid + 5-clique
 {prefix} dot -                      --- graph in DOT format from <stdin>

---- Graph from a file ----
 {prefix} <filename>
 {prefix} <format> <filename>        --- format one of {formats}

Specifying the graph format is required only when it cannot be
inferred from the filename extension, or does not match it.

---- Graph distribution/constructions ----
  {prefix} gnp N p               --- N vertices, p-biased independent edges
  {prefix} gnm N m               --- N vertices, M edges at random
  {prefix} gnd N d               --- Random d-regular graph of order N
  {prefix} grid  d1 d2 d3 ...    --- d1 x d2 x d3 x ... grid graph
  {prefix} torus d1 d2 d3 ...    --- d1 x d2 x d3 x ... torus graph
  {prefix} complete N            --- complete graph of order N
  {prefix} empty N               --- empty graph of order N

---- Graph modifications ----
It is possible to modify the previous contruction by appending one or
more of the following options to the graph specifications.

   plantclique k    --- add a randomly chosen k-clique
   addedges    m    --- add m new edges at random

---- Saving the graph ----
For reproducibility it is possible the graph using the option

   save <filename>
   save <format> <filename>   ---- format is one of {formats}

where <format> is only required when cannot be inferred by the
filename extension.
"""

bipartite_graph_doc = """
an bipartite graph, either
  - read from file; or
  - generated according to a construction.

examples:
 {prefix} bipartite.dot               --- graph from DOT file
 {prefix} bipartite.matrix            --- graph from matrix file
 {prefix} gnp 10 .5                   --- random G(n,p) graph
 {prefix} glrd 15 10 4 addedges 4     --- random 4-regular 15,10-bipartite + 4 random edges
 {prefix} empty 20 20 plantbiclique 5 --- 20,20-bipartite with a random 5-clique
 {prefix} dot -                       --- graph in DOT format from <stdin>

---- Graph from a file ----
 {prefix} <filename>
 {prefix} <format> <filename>        --- format is one of {formats}

Specifying the graph format is required only when it cannot be
inferred from the filename extension, or does not match it.

---- Graph distribution/constructions ----
(L,R)-bipartite with L left vertices, R right vertices
  {prefix} glrp L R p            --- p-biased independent edges
  {prefix} glrm L R m            --- m edges at random
  {prefix} glrd L R d            --- d edges at random per left vertex
  {prefix} regular L R d         --- Regular bipartite. Degree d on the left
  {prefix} shift L R v1 v2 ...   --- Shift graph graph: left vertex i connected to x+v1, x+v2,...
  {prefix} complete L R          --- complete bipartite
  {prefix} empty L R             --- empty bipartite

---- Graph modifications ----
It is possible to modify the previous contruction by appending one or
more of the following options to the graph specifications.

   plantbiclique A B  --- add a random biclique of size (A,B)
   addedges      m    --- add m new edges at random

---- Saving the graph ----
For reproducibility it is possible the graph using the option

   save <filename>
   save <format> <filename>   ---- format is one of {formats}

where <format> is only required when cannot be inferred by the
filename extension.
"""

dag_graph_doc = """
an directed acyclic graph, either
  - read from file; or
  - generated according to a construction.

examples:
 {prefix} graphfile.kthlist   --- graph from kthlist file
 {prefix} graphfile.gml       --- graph from GML file
 {prefix} tree 10             --- a complete rooted tree of height 5
 {prefix} dot -               --- graph in DOT format from <stdin>

---- Graph from a file ----
 {prefix} <filename>
 {prefix} <format> <filename>        --- format one of {formats}

Specifying the graph format is required only when it cannot be
inferred from the filename extension, or does not match it.

---- Graph constructions ----
  {prefix} tree h         --- complete rooted tree of height h
  {prefix} pyramid h      --- pyramid graph of height h
  {prefix} path L         --- path of length L (i.e. L+1 vertices)

---- Saving the graph ----
For reproducibility it is possible the graph using the option

   save <filename>
   save <format> <filename>   ---- format one of {formats}

where <format> is only required when cannot be inferred by the
filename extension.
"""


def make_graph_doc(graphtype, cliprefix):
    formats = supported_formats()[graphtype]
    if graphtype == 'simple':
        return simple_graph_doc.format(prefix=cliprefix,
                                       formats=str(formats)[1:-1])
    elif graphtype == 'bipartite':
        return bipartite_graph_doc.format(prefix=cliprefix,
                                          formats=str(formats)[1:-1])
    elif graphtype == 'dag':
        return dag_graph_doc.format(prefix=cliprefix,
                                    formats=str(formats)[1:-1])
    return ""
