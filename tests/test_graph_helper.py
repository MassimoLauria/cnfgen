import networkx as nx

def complete_bipartite_graph_proper(n,m):
    g = nx.complete_bipartite_graph(n,m)
    values = {k:v for (k,v) in enumerate([0]*n + [1]*m)}
    nx.set_node_attributes(g, 'bipartite', values)
    return g
