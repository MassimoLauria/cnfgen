import cnfformula.utils.cnfshuffle as cnfshuffle

from . import TestCNFBase
from test_cnfformula import TestCNF
from . import shufflereference

import cnfformula

import random
import StringIO

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
            self.fail(e)
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
