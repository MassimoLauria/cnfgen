from cnfgen.graphs import supported_formats

simple_graph_doc = """
a simple graph can be
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
 {prefix} <format> <filename>        --- format in {{{formats}}}

Specifying the graph format is required only when it cannot be
inferred from the filename extension, or does not match it.

---- Graph distribution/constructions ----
  {prefix} gnp N p               --- N vertices, p-biased independent edges
  {prefix} gnm N M               --- N vertices, M edges at random
  {prefix} gnd N d               --- Random d-regular graph of order N
  {prefix} grid  N1 N2 N3 ...    --- N1 x N2 x N3 x ... grid graph
  {prefix} torus N1 N2 N3 ...    --- N1 x N2 x N3 x ... torus graph
  {prefix} complete N            --- complete graph of order N
  {prefix} empty N               --- empty graph of order N

---- Graph modifications ----
It is possible to modify the previous contruction by appending one or
more of the following options to the graph specifications.

   plantclique N    --- add a random clique of size N
   addedges    N    --- add N new edges at random

---- Saving the graph ----
For reproducibility it is possible the graph using the option

   save <filename>
   save <format> <filename>   ---- format in {{{formats}}}

where <format> is only required when cannot be inferred by the
filename extension.
"""


def make_graph_doc(graphtype, cliprefix):
    formats = supported_formats()[graphtype]
    if graphtype == 'simple':
        return simple_graph_doc.format(prefix=cliprefix,
                                       formats=str(formats)[1:-1])
    return ""
