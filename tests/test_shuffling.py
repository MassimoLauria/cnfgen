from cnfformula import RandomKCNF
from cnfformula.transformations.shuffle import Shuffle

from . import TestCNFBase

import cnfformula
import unittest
import random
import io

class TestShuffleTransformation(TestCNFBase) :

    @staticmethod
    def inverse_permutation(permutation, base=0) :
        inverse = [0]*len(permutation)
        for i,p in enumerate(permutation) :
            inverse[p-base] = i+base
        return inverse

    def test_identity(self) :
        cnf = RandomKCNF(4,10,100)

        variable_permutation = list(cnf.variables())
        clause_permutation = list(range(100))
        polarity_flip = [1]*10
        
        shuffle = Shuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        self.assertCnfEqual(cnf,shuffle)

    def test_variable_permutation(self) :
        cnf = cnfformula.CNF([[(True,'x'),(True,'y'),(False,'z')]])
        variable_permutation = ['y','z','x']
        clause_permutation = list(range(1))
        polarity_flip = [1]*3
        shuffle = Shuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        self.assertSequenceEqual(list(shuffle.variables()),variable_permutation)
        self.assertSequenceEqual(list(shuffle.clauses()),list(cnf.clauses()))

    def test_polarity_flip(self) :
        cnf = cnfformula.CNF([[(True,'x'),(True,'y'),(False,'z')]])
        variable_permutation = list(cnf.variables())
        clause_permutation = list(range(1))
        polarity_flip = [1,-1,-1]
        shuffle = Shuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        expected = cnfformula.CNF([[(True,'x'),(False,'y'),(True,'z')]])
        self.assertCnfEqual(expected,shuffle)

    def test_variable_and_polarity_flip(self) :
        cnf = cnfformula.CNF([[(True,'x'),(True,'y'),(False,'z')]])
        variable_permutation = ['y','z','x']
        clause_permutation = list(range(1))
        polarity_flip = [1,-1,-1]
        shuffle = Shuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        expected = cnfformula.CNF([[(False,'y'),(True,'z'),(True,'x')]])
        self.assertCnfEqual(expected,shuffle)

    @unittest.skip("Broken test to be fixed")
    def test_inverse(self) :
        cnf = RandomKCNF(4,10,100)

        # Generate random variable, clause and polarity permutations.
        # but keep the indices for the variables, since they are strings.
        variable_permutation = list(enumerate(cnf.variables()))
        random.shuffle(variable_permutation)

        clause_permutation = list(range(100))
        random.shuffle(clause_permutation)

        polarity_flip = [random.choice([-1,1]) for x in range(10)]

        # variable_permutation has the permutation already applied.
        old_variables = list(cnf.variables())
        new_variables = [old_variables[sigma_i] for sigma_i,v in variable_permutation]

        # Shuffle
        shuffle = Shuffle(cnf, new_variables, clause_permutation, polarity_flip)
        
        # The inverse variable permutation is the original list, do nothing.
        # The inverse clause permutation is the group inverse permutation.
        i_clause_permutation = self.inverse_permutation(clause_permutation)
        # The polarity flip applies to new variables. So if we flipped
        # the i-th variable now we want to flip the sigma(i)-th
        # variable.
        i_polarity_flip = [polarity_flip[i] for i in variable_permutation]

        # Inverse shuffle.
        cnf2 = Shuffle(shuffle, old_variables, i_clause_permutation, i_polarity_flip)
        self.assertCnfEqual(cnf2,cnf)

    def test_deterministic(self) :
        cnf = RandomKCNF(4,10,100)
        random.seed(42)
        shuffle = Shuffle(cnf)
        random.seed(42)
        shuffle2 = Shuffle(cnf)
        self.assertCnfEqual(shuffle2,shuffle)

