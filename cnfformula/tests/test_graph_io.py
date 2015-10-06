#!/usr/bin/env python

import unittest

import cnfformula
from cnfformula.graphs import readGraph

from StringIO import StringIO as sio
import networkx as nx

from . import example_filename

dot_path2 = 'graph G { 0 -- 1 -- 2}'
gml_path2 = """
        graph [
           node [
             id 0
             label 0
           ]
           node [
             id 1
             label 1
           ]
           node [
             id 2
             label 2
           ]
           edge [
             source 0
             target 1
           ]
           edge [
             source 1
             target 2
           ]
         ]"""

dimacs_path2 ="p edge 3 2\ne 1 2\ne 2 3\n"



class TestGraphIO(unittest.TestCase) :

    def test_low_level_pydot_read_path2(self) :

        try:
            import pydot
        except ImportError:
            self.skipTest("PyDot2 not installed. Can't test DOT I/O")

        G = nx.Graph(nx.read_dot(sio(dot_path2)))

    def test_low_level_gml_read_path2(self) :

        G = nx.read_gml(sio(gml_path2))

        self.assertEqual(G.order(), 3)
        self.assertEqual(len(G.edges()), 2)
        self.assertTrue(G.has_edge(0, 1))
        self.assertTrue(G.has_edge(1, 2))
        self.assertFalse(G.has_edge(0, 2))

    def test_low_level_dimacs_read_path2(self) :

        G = cnfformula.graphs._read_graph_dimacs_format(sio(dimacs_path2))

        self.assertEqual(G.order(), 3)
        self.assertEqual(len(G.edges()), 2)
        self.assertTrue(G.has_edge(1, 2))
        self.assertTrue(G.has_edge(2, 3))
        self.assertFalse(G.has_edge(1, 3))


    def test_readGraph_dot_path2(self) :

        try:
            import pydot
        except ImportError:
            self.skipTest("PyDot2 not installed. Can't test DOT I/O")

        self.assertRaises(ValueError, readGraph, sio(dot_path2), graph_type='simple')
        G = readGraph(sio(dot_path2), graph_type='simple', file_format = 'dot')
        self.assertEqual(G.order(), 3)
        self.assertEqual(len(G.edges()), 2)

    def test_readGraph_gml_path2(self) :

        self.assertRaises(ValueError, readGraph, sio(gml_path2), graph_type='simple')
        G = readGraph(sio(gml_path2), graph_type='simple', file_format = 'gml')
        self.assertEqual(G.order(), 3)
        self.assertEqual(len(G.edges()), 2)


    def test_readGraph_dimacs_path2(self) :

        self.assertRaises(ValueError, readGraph, sio(dimacs_path2), graph_type='simple')
        G = readGraph(sio(dimacs_path2), graph_type='simple', file_format = 'dimacs')
        self.assertEqual(G.order(), 3)
        self.assertEqual(len(G.edges()), 2)

    def test_readGraph_dot_path2_file(self) :

        try:
            import pydot
        except ImportError:
            self.skipTest("PyDot2 not installed. Can't test DOT I/O")

        with open(example_filename('path2.dot'),'r') as ifile:

            # Parsing should fail here
            self.assertRaises(ValueError, readGraph, ifile, graph_type='simple', file_format='gml')

            ifile.seek(0)
            
            # Parser should guess that it is a dot file
            G = readGraph(ifile, graph_type='simple')
            self.assertEqual(G.order(), 3)
            self.assertEqual(len(G.edges()), 2)
