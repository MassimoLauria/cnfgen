#!/usr/bin/env python


import cnfformula
import cnfformula.utils as cnfutils

import cnfformula.cnfgen as cnfgen
import cnfformula.utils.cnfshuffle as cnfshuffle
import cnfformula.utils.kthgraph2dimacs as kthgraph2dimacs

from . import shufflereference
from . import TestCNFBase

import unittest
import networkx as nx
import StringIO
import random
import itertools

class TestCNF(TestCNFBase) :

    @staticmethod
    def cnf_from_variables_and_clauses(variables, clauses) :
        cnf = cnfformula.CNF()
        for variable in variables :
            cnf.add_variable(variable)
        for clause in clauses :
            cnf.add_clause(clause)
        return cnf

    @staticmethod
    def sorted_cnf(clauses) :
        return TestCNF.cnf_from_variables_and_clauses(
            sorted(set(variable for polarity,variable in itertools.chain(*clauses))),
            clauses)

    @staticmethod
    def random_cnf(width, num_variables, num_clauses) :
        return TestCNF.cnf_from_variables_and_clauses(xrange(1,num_variables+1), [
                [(random.choice([True,False]),x+1)
                 for x in random.sample(xrange(num_variables),width)]
                for C in xrange(num_clauses)])
    
    def test_empty(self) :
        F=cnfformula.CNF()
        self.assertTrue(F._check_coherence())
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F.clauses()),[])

    def test_safe_clause_insetion(self):
        F=cnfformula.CNF()
        F.add_variable("S")
        F.add_variable("U")
        F.add_clause([(True,"S"),(False,"T")])
        self.assertTrue(len(list(F.variables())),2)
        F.add_clause([(True,"T"),(False,"U")],strict=True)
        self.assertTrue(len(list(F.variables())),3)
        self.assertRaises(ValueError, F.add_clause,
                          [(True,"T"),(False,"V")],strict=True)

        
class TestPebbling(TestCNFBase) :
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
        shuffle = cnfshuffle.cnfshuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        self.assertCnfEqual(cnf,shuffle)

    def test_variable_permutation(self) :
        cnf = cnfformula.CNF([[(True,'x'),(True,'y'),(False,'z')]])
        variable_permutation = ['y','z','x']
        clause_permutation = range(1)
        polarity_flip = [1]*3
        shuffle = cnfshuffle.cnfshuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        self.assertSequenceEqual(list(shuffle.variables()),variable_permutation)
        self.assertSequenceEqual(list(shuffle.clauses()),list(cnf.clauses()))

    def test_polarity_flip(self) :
        cnf = cnfformula.CNF([[(True,'x'),(True,'y'),(False,'z')]])
        variable_permutation = list(cnf.variables())
        clause_permutation = range(1)
        polarity_flip = [1,-1,-1]
        shuffle = cnfshuffle.cnfshuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        expected = cnfformula.CNF([[(True,'x'),(False,'y'),(True,'z')]])
        self.assertCnfEqual(expected,shuffle)

    def test_variable_and_polarity_flip(self) :
        cnf = cnfformula.CNF([[(True,'x'),(True,'y'),(False,'z')]])
        variable_permutation = ['y','z','x']
        clause_permutation = range(1)
        polarity_flip = [1,-1,-1]
        shuffle = cnfshuffle.cnfshuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        expected = cnfformula.CNF([[(False,'y'),(True,'z'),(True,'x')]])
        self.assertCnfEqual(expected,shuffle)

    def test_inverse(self) :
        cnf = self.random_cnf(4,10,100)

        # Generate random variable, clause and polarity permutations.
        variable_permutation = range(10)
        random.shuffle(variable_permutation)
        clause_permutation = range(100)
        random.shuffle(clause_permutation)
        polarity_flip = [random.choice([-1,1]) for x in xrange(10)]

        # variable_permutation has the permutation already applied.
        old_variables = list(cnf.variables())
        new_variables = [old_variables[sigma_i] for sigma_i in variable_permutation]

        # Shuffle
        shuffle = cnfshuffle.cnfshuffle(cnf, new_variables, clause_permutation, polarity_flip)
        
        # The inverse variable permutation is the original list, do nothing.
        # The inverse clause permutation is the group inverse permutation.
        i_clause_permutation = self.inverse_permutation(clause_permutation)
        # The polarity flip applies to new variables. So if we flipped
        # the i-th variable now we want to flip the sigma(i)-th
        # variable.
        i_polarity_flip = [polarity_flip[i] for i in variable_permutation]

        # Inverse shuffle.
        cnf2 = cnfshuffle.cnfshuffle(shuffle, old_variables, i_clause_permutation, i_polarity_flip)
        self.assertCnfEqual(cnf2,cnf)

    def test_deterministic(self) :
        cnf = self.random_cnf(4,10,100)
        random.seed(42)
        shuffle = cnfshuffle.cnfshuffle(cnf)
        random.seed(42)
        shuffle2 = cnfshuffle.cnfshuffle(cnf)
        self.assertCnfEqual(shuffle2,shuffle)

class TestDimacsReshuffler(TestCNF) :
    def test_backwards_compatible(self) :
        cnf = self.random_cnf(4,10,100)
        random.seed(44)
        shuffle = cnfshuffle.cnfshuffle(cnf)
        reference_output = shuffle.dimacs()+"\n"
        input = StringIO.StringIO(cnf.dimacs())
        dimacs_shuffle = StringIO.StringIO()
        random.seed(44)
        shufflereference.stableshuffle(input, dimacs_shuffle)
        self.assertMultiLineEqual(dimacs_shuffle.getvalue(), reference_output)

    def test_cmdline_reshuffler(self) :
        cnf = self.random_cnf(4,10,3)
        random.seed('45')
        shuffle = cnfshuffle.cnfshuffle(cnf)
        reference_output = shuffle.dimacs()
        input = StringIO.StringIO(cnf.dimacs())
        dimacs_shuffle = StringIO.StringIO()
        argv=['cnfshuffle', '--input', '-', '--output', '-', '--seed', '45']
        try:
            import sys
            sys.stdin = input
            sys.stdout = dimacs_shuffle
            cnfshuffle.command_line_utility(argv)
        except Exception as e:
            print e
            self.fail()
        finally:
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stdout__
        self.assertMultiLineEqual(dimacs_shuffle.getvalue(), reference_output)      

    def equivalence_check_helper(self, cnf, variable_permutation, clause_permutation, polarity_flip) :
        variables = list(cnf.variables())
        massimos_fancy_input = [variables[p] for p in variable_permutation]
        random.seed(43)
        shuffle = cnfshuffle.cnfshuffle(cnf, massimos_fancy_input, clause_permutation, polarity_flip)
        reference_output = shuffle.dimacs()+"\n"
        input = StringIO.StringIO(cnf.dimacs())
        dimacs_shuffle = StringIO.StringIO()
        random.seed(43)
        shufflereference.stableshuffle(input, dimacs_shuffle, massimos_fancy_input, clause_permutation, polarity_flip)
        self.assertMultiLineEqual(dimacs_shuffle.getvalue(), reference_output)

    def test_identity_equivalence(self) :
        cnf = self.random_cnf(2,3,2)
        variable_permutation = range(3)
        clause_permutation = range(2)
        polarity_flip = [1]*3
        self.equivalence_check_helper(cnf, variable_permutation, clause_permutation, polarity_flip)

    def test_random_equivalence_small(self) :
        cnf = self.random_cnf(4,10,10)
        variable_permutation = range(10)
        random.shuffle(variable_permutation)
        clause_permutation = range(10)
        random.shuffle(clause_permutation)
        polarity_flip = [random.choice([-1,1]) for x in xrange(10)]
        self.equivalence_check_helper(cnf, variable_permutation, clause_permutation, polarity_flip)

    def test_random_equivalence(self) :
        cnf = self.random_cnf(4,10,100)
        variable_permutation = range(10)
        random.shuffle(variable_permutation)
        clause_permutation = range(100)
        random.shuffle(clause_permutation)
        polarity_flip = [random.choice([-1,1]) for x in xrange(10)]
        self.equivalence_check_helper(cnf, variable_permutation, clause_permutation, polarity_flip)

class TestSubstitution(TestCNFBase) :
    def test_or(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'or', 3)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^0')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2'),(False,'{y}^2')],
                    ]))
        lift2 = cnfformula.TransformFormula(cnf, 'or', 3)
        self.assertCnfEqual(lift,lift2)

    def test_xor(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'xor', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))
        lift2 = cnfformula.TransformFormula(cnf, 'xor', 2)
        self.assertCnfEqual(lift,lift2)

    def test_majority(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'maj', 3)
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
        lift2 = cnfformula.TransformFormula(cnf, 'maj', 3)
        self.assertCnfEqual(lift,lift2)
        
    def test_equality(self) :
        cnf = cnfformula.CNF([[(False,'x'),(True,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'eq', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(True,'{y}^1')],
                    ]))
        lift2 = cnfformula.TransformFormula(cnf, 'eq', 2)
        self.assertCnfEqual(lift,lift2)

    def test_inequality(self) :
        cnf = cnfformula.CNF([[(False,'x'),(True,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'neq', 2)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(False,'{x}^1'),(True,'{y}^0'),(True,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(True,'{y}^1')],
                    [(True,'{x}^0'),(False,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                ]))

    def test_inequality_pos_clause(self) :
        cnf = cnfformula.CNF([[(True,'x')]])
        lift = cnfformula.TransformFormula(cnf, 'neq', 3)
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(True,'{x}^0'),(True,'{x}^1'),(True,'{x}^2')],
                    [(False,'{x}^0'),(False,'{x}^1'),(False,'{x}^2')]
                ]))

    def test_eq_vs_neq(self) :
        cnf = cnfformula.CNF([
                [(False,'x'),(True,'y')],
                [(True,'z'),(True,'t')],
                [(False,'u'),(False,'v')]
                ])
        cnfneg = cnfformula.CNF([
                [(True,'x'),(False,'y')],
                [(False,'z'),(False,'t')],
                [(True,'u'),(True,'v')]
                ])
        lifteq = cnfformula.TransformFormula(cnf, 'eq', 4)
        liftneq = cnfformula.TransformFormula(cnfneg, 'neq', 4)
        self.assertCnfEqual(lifteq, liftneq)

    def test_if_then_else(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'ite')
        self.assertCnfEqual(lift,cnfformula.CNF([
                    [(False,'{x}^0'),(True,'{x}^1'),(False,'{y}^0'),(False,'{y}^1')],
                    [(False,'{x}^0'),(True,'{x}^1'),(True,'{y}^0'),(False,'{y}^2')],
                    [(True,'{x}^0'),(True,'{x}^2'),(False,'{y}^0'),(False,'{y}^1')],
                    [(True,'{x}^0'),(True,'{x}^2'),(True,'{y}^0'),(False,'{y}^2')],
        ]))
        lift2 = cnfformula.TransformFormula(cnf, 'ite', 42)
        self.assertCnfEqual(lift,lift2)

    def test_exactly_one(self) :
        cnf = cnfformula.CNF([[(True,'x'),(False,'y')]])
        lift = cnfformula.TransformFormula(cnf, 'one', 2)

        lift2 = cnfformula.TransformFormula(cnf, 'one', 2)
        self.assertCnfEqual(lift,lift2)

class TestKth2Dimacs(TestCNFBase) :
    def identity_check_helper(self, input, liftname, liftrank) :
        G = cnfgen.readDigraph(input,'kth')
        input.seek(0)
        peb = cnfgen.PebblingFormula(G)
        lift = cnfformula.TransformFormula(peb, liftname, liftrank)
        reference_output = lift.dimacs(export_header=False)+"\n"
        
        kthgraph2dimacs_output=StringIO.StringIO()
        kthgraph2dimacs.kthgraph2dimacs(input, liftname, liftrank, kthgraph2dimacs_output, header=True)
        self.assertMultiLineEqual(kthgraph2dimacs_output.getvalue(), reference_output)

    def test_unit_graph(self) :
        input = StringIO.StringIO("1\n1 :\n")
        self.identity_check_helper(input, 'none', 0)

    def test_small_line(self) :
        input = StringIO.StringIO("3\n1 :\n2 : 1\n3 : 2\n")
        self.identity_check_helper(input, 'none', 0)

    def test_small_pyramid(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        self.identity_check_helper(input, 'none', 0)        
        
    def test_substitution(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        self.identity_check_helper(input, 'or', 2)

class TestRandomCNF(TestCNFBase) :
    def test_empty_cnf(self) :
        F = cnfformula.families.RandomKCNF(0,0,0)
        self.assertListEqual(list(F.variables()),[])
        self.assertListEqual(list(F.clauses()),[])

    def test_empty_cnf_with_vars(self) :
        F = cnfformula.families.RandomKCNF(0,10,0)
        self.assertListEqual(list(F.variables()),range(1,11))
        self.assertListEqual(list(F.clauses()),[])

    def test_random_cnf(self) :
        F = cnfformula.families.RandomKCNF(3,10,50)
        self.assertListEqual(list(F.variables()),range(1,11))
        self.assertEqual(len(F),50)
        self.assertEqual(len(set(frozenset(x) for x in F.clauses())),50)
        
if __name__ == '__main__':
    unittest.main()
