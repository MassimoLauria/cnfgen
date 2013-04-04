#!/usr/bin/env python


import cnfformula
import cnfformula.utils as cnfutils

import cnfgen
import reshuffle
import kth2dimacs

import unittest
import networkx as nx
import StringIO
import random
import itertools

class TestCNF(unittest.TestCase) :
    def assertCnfEqual(self,cnf1,cnf2) :
        self.assertSetEqual(set(cnf1.variables()),set(cnf2.variables()))
        self.assertSetSetEqual(cnf1.clauses(),cnf2.clauses())

    def assertSetSetEqual(self,list1,list2) :
        set1=set(frozenset(x) for x in list1)
        set2=set(frozenset(x) for x in list2)
        self.assertSetEqual(set1,set2)

    @staticmethod
    def sorted_cnf(clauses) :
        cnf = cnfformula.CNF()
        variables = set(variable for polarity,variable in itertools.chain(*clauses));
        for variable in sorted(variables) :
            cnf.add_variable(variable)
        for clause in clauses :
            cnf.add_clause(clause)
        return cnf

    @staticmethod
    def random_cnf(width, num_variables, num_clauses) :
        return TestCNF.sorted_cnf([
                [(random.choice([True,False]),x+1)
                 for x in random.sample(xrange(num_variables),width)]
                for C in xrange(num_clauses)])
    
    def test_empty(self) :
        F=cnfformula.CNF()
        self.assertTrue(F._check_coherence())
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F.clauses()),[])

class TestPebbling(TestCNF) :
    def test_null_graph(self) :
        G=nx.DiGraph()
        peb = cnfgen.PebblingFormula(G)
        self.assertTrue(peb._check_coherence())
        self.assertCnfEqual(peb,cnfformula.CNF())

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
            cnfgen.PebblingFormula(G)

class TestDimacsParser(TestCNF) :
    def test_empty_file(self) :
        dimacs = StringIO.StringIO()
        with self.assertRaises(ValueError) :
            cnfutils.dimacs2cnf(dimacs)

    def test_empty_cnf(self) :
        dimacs = StringIO.StringIO("p cnf 0 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF())

    def test_comment_only_file(self) :
        dimacs = StringIO.StringIO("c Hej!\n")
        with self.assertRaises(ValueError) :
            cnfutils.dimacs2cnf(dimacs)

    def test_invalid_file(self) :
        dimacs = StringIO.StringIO("Hej!\n")
        with self.assertRaises(ValueError) :
            cnfutils.dimacs2cnf(dimacs)

    def test_commented_empty_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 0 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF())

    def test_one_clause_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 2 1\n1 -2 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF([[(True, 1),(False, 2)]]))

    def test_one_var_cnf(self) :
        dimacs = StringIO.StringIO("c Hej!\np cnf 1 2\n1 0\n-1 0\n")
        cnf = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf,cnfformula.CNF([[(True, 1)],[(False, 1)]]))
    
    def test_inverse(self) :
        cnf = TestCNF.sorted_cnf([[(True,2),(False,1)]])
        dimacs = StringIO.StringIO(cnf.dimacs())
        cnf2 = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf2,cnf)

    def test_inverse_random(self) :
        cnf = self.random_cnf(4,10,100)
        dimacs = StringIO.StringIO(cnf.dimacs())
        cnf2 = cnfutils.dimacs2cnf(dimacs)
        self.assertCnfEqual(cnf2,cnf)

class TestReshuffler(TestCNF) :
    @staticmethod
    def inverse_permutation(permutation, base=0) :
        inverse = [0]*len(permutation)
        for i,p in enumerate(permutation) :
            inverse[p-base] = i+base
        return inverse

    def test_identity(self) :
        cnf = self.random_cnf(4,10,100)
        variable_permutation = range(1,11)
        clause_permutation = range(100)
        polarity_flip = [1]*10
        shuffle = reshuffle.reshuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        self.assertCnfEqual(cnf,shuffle)

    def test_variable_permutation(self) :
        cnf = cnfformula.CNF([[(True,'x'),(True,'y'),(False,'z')]])
        variable_permutation = ['y','z','x']
        clause_permutation = range(1)
        polarity_flip = [1]*3
        shuffle = reshuffle.reshuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        self.assertSequenceEqual(list(shuffle.variables()),variable_permutation)
        self.assertSequenceEqual(list(shuffle.clauses()),list(cnf.clauses()))

    def test_inverse(self) :
        cnf = self.random_cnf(4,10,100)
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
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.LiftFormula(cnf, 'or', 3)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^0')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^2')],
                    ]))
        lift2 = cnfformula.LiftFormula(cnf, 'or', 3)
        self.assertCnfEqual(lift,lift2)

    def test_xor(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.LiftFormula(cnf, 'xor', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))
        lift2 = cnfformula.LiftFormula(cnf, 'xor', 2)
        self.assertCnfEqual(lift,lift2)

    def test_majority(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.LiftFormula(cnf, 'maj', 3)
        self.assertCnfEqual(lift,cnfformula.CNF([
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
        lift2 = cnfformula.LiftFormula(cnf, 'maj', 3)
        self.assertCnfEqual(lift,lift2)
        
    def test_equality(self) :
        cnf = cnfformula.CNF([[(False,'x'),(True,'y')]])
        lift = cnfformula.LiftFormula(cnf, 'eq', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))
        lift2 = cnfformula.LiftFormula(cnf, 'eq', 2)
        self.assertCnfEqual(lift,lift2)

    def test_if_then_else(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.LiftFormula(cnf, 'ite')
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(False,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^2')],
                    [(True,'{x}^0'),(True,'{x}^2'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^2'),(True,'{y}^0'),(False,'{y}^2')],
        ]))
        lift2 = cnfformula.LiftFormula(cnf, 'ite', 42)
        self.assertCnfEqual(lift,lift2)


    def test_exactly_one(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.LiftFormula(cnf, 'one', 2)

        lift2 = cnfformula.LiftFormula(cnf, 'one', 2)
        self.assertCnfEqual(lift,lift2)

class TestKth2Dimacs(TestCNF) :
    def identity_test_helper(self, input, liftname, liftrank) :
        input.seek(0)
        G = cnfgen.readDigraph(input,'kth')
        input.seek(0)
        peb = cnfgen.PebblingFormula(G)
        lift = cnfgen.LiftFormula(peb, liftname, liftrank)
        reference_output = lift.dimacs(add_header=False, add_comments=False)+"\n"
        
        kth2dimacs_output=StringIO.StringIO()
        kth2dimacs.kth2dimacs(input, liftname, liftrank, kth2dimacs_output, header=True, comments=False)
        self.assertMultiLineEqual(kth2dimacs_output.getvalue(), reference_output)

    def test_unit_graph(self) :
        input = StringIO.StringIO("1\n1 :\n")
        self.identity_test_helper(input, 'none', 0)

    def test_small_line(self) :
        input = StringIO.StringIO("3\n1 :\n2 : 1\n3 : 2\n")
        self.identity_test_helper(input, 'none', 0)

    def test_small_pyramid(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        self.identity_test_helper(input, 'none', 0)        
        
    def test_substitution(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        self.identity_test_helper(input, 'or', 2)


class TestNoise(TestCNF) :
    def test_noise(self) :
        input = StringIO.StringIO()
        print >>input, "60"
        print >>input, "1 : "
        for i in xrange(1,60) :print >>input, i+1, ":", i
        output = StringIO.StringIO()
        output_noise = StringIO.StringIO()
        input.seek(0) 
        kth2dimacs.kth2dimacs(input, 'or', 3, output, header=True, comments=False)
        output=output.getvalue()
        output_clauses='\n'.join(output.split('\n')[1:])
        input.seek(0)
        kth2dimacs.kth2dimacs(input, 'or', 3, output_noise, header=True, comments=False, noise=2)
        output_noise=output_noise.getvalue()
        output_noise_clauses='\n'.join(output_noise.split('\n')[1:])
        assert(output_noise_clauses.startswith(output_clauses))
        noise=output_noise_clauses[len(output_clauses):]
        variables = sorted(abs(int(v)) for v in noise.split())
        self.assertListEqual([0]*(60*3/2) + range(1,60*3+1), variables)

if __name__ == '__main__':
    unittest.main()
