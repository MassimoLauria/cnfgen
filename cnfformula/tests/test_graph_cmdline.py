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

class TestAddBiEdges(TestArgparse) :
    def setUp(self):
        self.graph_helper = cnfformula.cmdline.BipartiteGraphHelper()

    def test_already_complete(self):
        with self.assertRaises(ValueError):
            self.parse(["--bcomplete", "10", "9", "--addedges", "1"])

    def test_complete(self):
        G = self.parse(["--bp", "10", "9", "0", "--addedges", "90"])
        self.assertEqual(G.order(),19)
        self.assertEqual(G.size(),90)

    def test_add(self):
        G = self.parse(["--bm", "10", "9", "15", "--addedges", "10"])
        self.assertEqual(G.order(),19)
        self.assertEqual(G.size(),25)

class TestPlantBiClique(TestArgparse) :
    def setUp(self):
        self.graph_helper = cnfformula.cmdline.BipartiteGraphHelper()

    def test_too_large_left(self):
        with self.assertRaises(ValueError):
            self.parse(["--bcomplete", "10", "9", "--plantbiclique", "11", "9"])

    def test_too_large_right(self):
        with self.assertRaises(ValueError):
            self.parse(["--bcomplete", "10", "9", "--plantbiclique", "10", "10"])

    def test_already_complete(self):
        G = self.parse(["--bcomplete", "10", "9", "--plantbiclique", "5", "4"])
        self.assertEqual(G.order(),19)
        self.assertEqual(G.size(),90)

    def test_complete(self):
        G = self.parse(["--bp", "10", "9", "0", "--plantbiclique", "10", "9"])
        self.assertEqual(G.order(),19)
        self.assertEqual(G.size(),90)

    def test_add(self):
        G = self.parse(["--bm", "10", "9", "15", "--plantbiclique", "5", "4"])
        self.assertEqual(G.order(),19)
        self.assertGreaterEqual(G.size(),20)
        self.assertLessEqual(G.size(),35)

class TestSimple(TestArgparse) :
    def setUp(self):
        self.graph_helper = cnfformula.cmdline.SimpleGraphHelper()

    def test_gnp(self):
        G = self.parse(["--gnp", "10", "0.5"])
        self.assertEqual(G.order(),10)

    def test_gnm(self):
        G = self.parse(["--gnm", "10", "15"])
        self.assertEqual(G.order(),10)
        self.assertEqual(G.size(),15)
        
    def test_gnd(self):
        G = self.parse(["--gnd", "10", "3"])
        self.assertEqual(G.order(),10)
        self.assertEqual(G.size(),15)
        self.assertListEqual(G.degree().values(),[3]*10)

    def test_complete(self):
        G = self.parse(["--complete", "10"])
        self.assertEqual(G.order(),10)
        self.assertEqual(G.size(),45)
        self.assertListEqual(G.degree().values(),[9]*10)

    def test_grid(self):
        G = self.parse(["--grid", "8", "5"])
        self.assertEqual(G.order(),40)
        self.assertListEqual(sorted(G.degree().values()),[2]*4+[3]*18+[4]*(40-4-18))

    def test_torus(self):
        G = self.parse(["--torus", "8", "5"])
        self.assertEqual(G.order(),40)
        self.assertListEqual(G.degree().values(),[4]*40)

class TestAddEdges(TestArgparse) :
    def setUp(self):
        self.graph_helper = cnfformula.cmdline.SimpleGraphHelper()

    def test_already_complete(self):
        with self.assertRaises(ValueError):
            self.parse(["--complete", "10", "--addedges", "1"])

    def test_complete(self):
        G = self.parse(["--gnp", "10", "0", "--addedges", "45"])
        self.assertEqual(G.order(),10)
        self.assertEqual(G.size(),45)

    def test_add(self):
        G = self.parse(["--gnm", "10", "15", "--addedges", "10"])
        self.assertEqual(G.order(),10)
        self.assertEqual(G.size(),25)

class TestPlantClique(TestArgparse) :
    def setUp(self):
        self.graph_helper = cnfformula.cmdline.SimpleGraphHelper()

    def test_too_large(self):
        with self.assertRaises(ValueError):
            self.parse(["--complete", "10", "--plantclique", "11"])

    def test_already_complete(self):
        G = self.parse(["--complete", "10", "--plantclique", "5"])
        self.assertEqual(G.order(),10)
        self.assertEqual(G.size(),45)

    def test_complete(self):
        G = self.parse(["--gnp", "10", "0", "--plantclique", "10"])
        self.assertEqual(G.order(),10)
        self.assertEqual(G.size(),45)

    def test_add(self):
        G = self.parse(["--gnm", "10", "15", "--plantclique", "5"])
        self.assertEqual(G.order(),10)
        self.assertGreaterEqual(G.size(),20)
        self.assertLessEqual(G.size(),35)
