#!/usr/bin/env python
import cnfgen
import reshuffle

import unittest
import networkx as nx
import StringIO
import random

class TestCNF(unittest.TestCase) :
    def assertCnfEqual(self,cnf1,cnf2) :
        self.assertSetEqual(set(cnf1.variables()),set(cnf2.variables()))
        self.assertSetSetEqual(cnf1.clauses(),cnf2.clauses())

    def assertSetSetEqual(self,list1,list2) :
        set1=set(frozenset(x) for x in list1)
        set2=set(frozenset(x) for x in list2)
        self.assertSetEqual(set1,set2)

    @staticmethod
    def randomCnf(width, num_variables, num_clauses) :
        return cnfgen.CNF([
                [(random.choice([True,False]),x+1)
                 for x in random.sample(xrange(num_variables),width)]
                for C in xrange(num_clauses)])
    
    def test_empty(self) :
        F=cnfgen.CNF()
        self.assertTrue(F._check_coherence())
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F.clauses()),[])

class TestPebbling(TestCNF) :
    def test_null_graph(self) :
        G=nx.DiGraph()
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertCnfEqual(peb,cnfgen.CNF())

    def test_single_vertex(self) :
        G=nx.DiGraph()
        G.add_node('x')
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertSetEqual(set(peb.variables()),set(['x']))
        self.assertSetSetEqual(list(peb.clauses()),[[(True,'x')],[(False,'x')]])

    def test_path(self) :
        G=nx.path_graph(10,nx.DiGraph())
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        clauses = \
            [[(True,0)]] + \
            [[(False,i-1),(True,i)] for i in xrange(1,10)] + \
            [[(False,9)]]
        self.assertListEqual(list(peb.variables()),range(10))
        self.assertSetSetEqual(peb.clauses(),clauses)

    def test_pyramid(self) :
        G=nx.DiGraph()
        G.add_node(10)
        for i in xrange(0,10) :
            G.add_node(i)
            G.add_edge(i,10)
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        clauses = \
            [[(True,i)] for i in xrange(10)] + \
            [[(False,i) for i in xrange(10)] + [(True,10)]] + \
            [[(False,10)]]
        self.assertListEqual(list(peb.variables()),range(11))
        self.assertSetSetEqual(peb.clauses(),clauses)
        
    def test_cycle(self) :
        G=nx.cycle_graph(10,nx.DiGraph())
        with self.assertRaises(RuntimeError) :
            peb = cnfgen.PebblingFormula(G)

class TestDimacsParser(TestCNF) :
    def test_empty_file(self) :
        dimacs = StringIO.StringIO()
        with self.assertRaises(ValueError) :
            reshuffle.read_dimacs_file(dimacs)

    def test_empty_cnf(self) :
        dimacs = StringIO.StringIO("p cnf 0 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF())

    def test_comment_only_file(self) :
        dimacs = StringIO.StringIO("c Hej!\n")
        with self.assertRaises(ValueError) :
            reshuffle.read_dimacs_file(dimacs)

    def test_invalid_file(self) :
        dimacs = StringIO.StringIO("Hej!\n")
        with self.assertRaises(ValueError) :
            reshuffle.read_dimacs_file(dimacs)

    def test_commented_empty_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 0 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF())

    def test_one_clause_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 2 1\n1 -2 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF([[(True, 1),(False, 2)]]))

    def test_one_var_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 1 2\n1 0\n-1 0\n")
        cnf = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf,cnfgen.CNF([[(True, 1)],[(False, 1)]]))
    
    def test_inverse(self) :
        cnf = self.randomCnf(4,10,100)
        dimacs = StringIO.StringIO(cnf.dimacs())
        cnf2 = reshuffle.read_dimacs_file(dimacs)
        self.assertCnfEqual(cnf2,cnf)

class TestReshuffler(TestCNF) :
    @staticmethod
    def inverse_permutation(permutation, base=0) :
        inverse = [0]*len(permutation)
        for i,p in enumerate(permutation) :
            inverse[p-base] = i+base
        return inverse

    def test_identity(self) :
        cnf = self.randomCnf(4,10,100)
        variable_permutation = range(1,11)
        clause_permutation = range(100)
        polarity_flip = [1]*10
        shuffle = reshuffle.reshuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        self.assertCnfEqual(cnf,shuffle)

    def test_inverse(self) :
        cnf = self.randomCnf(4,10,100)
        variable_permutation = range(10)
        random.shuffle(variable_permutation)
        clause_permutation = range(100)
        random.shuffle(clause_permutation)
        polarity_flip = [random.choice([-1,1]) for x in xrange(10)]
        variables = list(cnf.variables())
        massimos_fancy_input = [variables[variable_permutation[i]] for i in xrange(10)]
        shuffle = reshuffle.reshuffle(cnf, massimos_fancy_input, clause_permutation,polarity_flip)
        i_variable_permutation = self.inverse_permutation(variable_permutation)
        i_clause_permutation = self.inverse_permutation(clause_permutation)
        i_polarity_flip = [polarity_flip[i] for i in variable_permutation]
        cnf2 = reshuffle.reshuffle(shuffle, variables, i_clause_permutation, i_polarity_flip)
        self.assertCnfEqual(cnf2,cnf)

class TestSubstitution(TestCNF) :
    def test_or(self) :
        cnf = cnfgen.CNF([[(True,'x'),(False,'y')]])
        Lift = cnfgen.implemented_lifting['or'][1]
        lift = Lift(cnf,3)
        self.assertCnfEqual(lift,cnfgen.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^0')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^2')],
                    ]))

    def test_xor(self) :
        cnf = cnfgen.CNF([[(True,'x'),(False,'y')]])
        Lift = cnfgen.implemented_lifting['xor'][1]
        lift = Lift(cnf,2)
        self.assertCnfEqual(lift,cnfgen.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))

    def test_majority(self) :
        cnf = cnfgen.CNF([[(True,'x'),(False,'y')]])
        Lift = cnfgen.implemented_lifting['maj'][1]
        lift = Lift(cnf,3)
        self.assertCnfEqual(lift,cnfgen.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^2'),(True,'{x}^0'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^1'),(False,'{y}^2')],
                    [(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^1'),(False,'{y}^2')],
                    [(True,'{x}^2'),(True,'{x}^0'),(False,'{y}^1'),(False,'{y}^2')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^2'),(False,'{y}^0')],
                    [(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^2'),(False,'{y}^0')],
                    [(True,'{x}^2'),(True,'{x}^0'),(False,'{y}^2'),(False,'{y}^0')],
                    ]))
        
    def test_equality(self) :
        cnf = cnfgen.CNF([[(False,'x'),(True,'y')]])
        Lift = cnfgen.implemented_lifting['eq'][1]
        lift = Lift(cnf,2)
        self.assertCnfEqual(lift,cnfgen.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))

    def test_if_then_else(self) :
        cnf = cnfgen.CNF([[(True,'x'),(False,'y')]])
        Lift = cnfgen.implemented_lifting['ite'][1]
        lift = Lift(cnf)
        self.assertCnfEqual(lift,cnfgen.CNF([
                    [(False,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^2')],
                    [(True,'{x}^0'),(True,'{x}^2'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^2'),(True,'{y}^0'),(False,'{y}^2')],
        ]))

    def test_exactly_one(self) :
        cnf = cnfgen.CNF([[(True,'x'),(False,'y')]])
        Lift = cnfgen.implemented_lifting['e1'][1]
        lift = Lift(cnf,2)

if __name__ == '__main__':
    unittest.main()
