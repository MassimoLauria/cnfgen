import argparse

import unittest

import cnfformula.cmdline
from cnfformula.graphs import bipartite_sets

class TestArgparse(unittest.TestCase) :
    def parse(self, args):
        parser = argparse.ArgumentParser()
        self.graph_helper.setup_command_line(parser)
        args = parser.parse_args(args)
        return self.graph_helper.obtain_graph(args)

class TestBipartite(TestArgparse) :
    def setUp(self):
        self.graph_helper = cnfformula.cmdline.BipartiteGraphHelper()

    def test_bp(self):
        G = self.parse(["--bp", "10", "9", "0.5"])
        self.assertEqual(G.order(),19)
        left, right = bipartite_sets(G)
        self.assertEqual(len(left),10)
        self.assertEqual(len(right),9)

    def test_bm(self):
        G = self.parse(["--bm", "10", "9", "15"])
        self.assertEqual(G.order(),19)
        self.assertEqual(G.size(),15)
        left, right = bipartite_sets(G)
        self.assertEqual(len(left),10)
        self.assertEqual(len(right),9)
        
    def test_bd(self):
        G = self.parse(["--bd", "10", "9", "3"])
        self.assertEqual(G.order(),19)
        self.assertEqual(G.size(),30)
        left, right = bipartite_sets(G)
        self.assertEqual(len(left),10)
        self.assertEqual(len(right),9)
        for v in left:
            self.assertEqual(G.degree(v),3)

    def test_bregular(self):
        G = self.parse(["--bregular", "10", "8", "4"])
        self.assertEqual(G.order(),18)
        self.assertEqual(G.size(),40)
        left, right = bipartite_sets(G)
        self.assertEqual(len(left),10)
        self.assertEqual(len(right),8)
        for v in left:
            self.assertEqual(G.degree(v),4)
        for v in right:
            self.assertEqual(G.degree(v),5)

    def test_bcomplete(self):
        G = self.parse(["--bcomplete", "10", "9"])
        self.assertEqual(G.order(),19)
        self.assertEqual(G.size(),90)
        left, right = bipartite_sets(G)
        self.assertEqual(len(left),10)
        self.assertEqual(len(right),9)
        for v in left:
            self.assertEqual(G.degree(v),9)
        for v in right:
            self.assertEqual(G.degree(v),10)

