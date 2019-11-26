from cnfformula.utils import cnfshuffle
from cnfformula.transformations.shuffle import Shuffle

from . import TestCNFBase
from .test_cnfformula import TestCNF

from . import shufflereference

import cnfformula

import random
import io

class TestDimacsReshuffler(TestCNF) :
    def test_backwards_compatible(self) :
        cnf = self.random_cnf(4,10,100)
        random.seed(44)
        shuffle = Shuffle(cnf)
        reference_output = shuffle.dimacs()+"\n"
        input = io.StringIO(cnf.dimacs())
        dimacs_shuffle = io.StringIO()
        random.seed(44)
        shufflereference.stableshuffle(input, dimacs_shuffle)
        self.assertMultiLineEqual(dimacs_shuffle.getvalue(), reference_output)

    def test_cmdline_reshuffler(self) :
        cnf = self.random_cnf(4,10,3)
        random.seed('45')
        shuffle = Shuffle(cnf)
        reference_output = shuffle.dimacs()
        input = io.StringIO(cnf.dimacs())
        dimacs_shuffle = io.StringIO()
        argv=['cnfshuffle', '--input', '-', '--output', '-', '--seed', '45']
        try:
            import sys
            sys.stdin = input
            sys.stdout = dimacs_shuffle
            cnfshuffle(argv)
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
        shuffle = Shuffle(cnf, massimos_fancy_input, clause_permutation, polarity_flip)
        reference_output = shuffle.dimacs()+"\n"
        input = io.StringIO(cnf.dimacs())
        dimacs_shuffle = io.StringIO()
        random.seed(43)
        shufflereference.stableshuffle(input, dimacs_shuffle, massimos_fancy_input, clause_permutation, polarity_flip)
        self.assertMultiLineEqual(dimacs_shuffle.getvalue(), reference_output)

    def test_identity_equivalence(self) :
        cnf = self.random_cnf(2,3,2)
        variable_permutation = list(range(3))
        clause_permutation = list(range(2))
        polarity_flip = [1]*3
        self.equivalence_check_helper(cnf, variable_permutation, clause_permutation, polarity_flip)

    def test_random_equivalence_small(self) :
        cnf = self.random_cnf(4,10,10)
        variable_permutation = list(range(10))
        random.shuffle(variable_permutation)
        clause_permutation = list(range(10))
        random.shuffle(clause_permutation)
        polarity_flip = [random.choice([-1,1]) for x in range(10)]
        self.equivalence_check_helper(cnf, variable_permutation, clause_permutation, polarity_flip)

    def test_random_equivalence(self) :
        cnf = self.random_cnf(4,10,100)
        variable_permutation = list(range(10))
        random.shuffle(variable_permutation)
        clause_permutation = list(range(100))
        random.shuffle(clause_permutation)
        polarity_flip = [random.choice([-1,1]) for x in range(10)]
        self.equivalence_check_helper(cnf, variable_permutation, clause_permutation, polarity_flip)
