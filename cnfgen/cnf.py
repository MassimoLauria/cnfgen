#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Build and manipulate CNF formulas

The module `contains facilities to generate cnf formulas, in
order to be printed in DIMACS or LaTeX formats. Such formulas are
ready to be fed to sat solvers.

The module implements the `CNF` object, which is the main entry point
to the `cnfgen` library.

Copyright (C) 2012-2021  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from itertools import combinations
from itertools import product, islice
from math import ceil, log

from cnfgen.basecnf import BaseCNF
from cnfgen.cnfio import CNFio
from cnfgen.linear import CNFLinear
from cnfgen.variables import VariablesManager


class CNF(VariablesManager, CNFio, CNFLinear):
    """Propositional formulas in conjunctive normal form.

    A CNF  formula is a  sequence of  clauses, which are  sequences of
    literals. Each literal is either a variable or its negation.

    Use ``add_clause`` to add new clauses to CNF. Clauses will be added
    multiple times in case of multiple insertion of the same clauses.

    For documentation purpose it is possible use have an additional
    comment header at the top of the formula, which will be
    *optionally* exported to LaTeX or dimacs.

    Implementation:  for efficiency reason clauses and variable can
    only be added, and not deleted. Furthermore order matters in
    the representation.

    Examples
    --------
    >>> c=CNF([[1, 2, -3], [-2, 4]])
    >>> print( c.to_dimacs(),end='')
    p cnf 4 2
    1 2 -3 0
    -2 4 0
    >>> c.add_clause([-3, 4, -5])
    >>> print( c.to_dimacs(),end='')
    p cnf 5 3
    1 2 -3 0
    -2 4 0
    -3 4 -5 0
    >>> print(c[1])
    [-2, 4]
    """

    def __init__(self, clauses=None, description=None):
        """Propositional formulas in conjunctive normal form.

        Parameters
        ----------
        clauses : ordered list of clauses
            a clause with k literals list containing k pairs, each
            representing a literal (see `add_clause`). First element
            is the polarity and the second is the variable, which must
            be an hashable object.

            E.g. (not x3) or x4 or (not x2) is encoded as [(False,"x3"),(True,"x4"),False,"x2")]

        description: string, optional
            a description of the formula
        """
        VariablesManager.__init__(
            self, clauses=clauses, description=description)



    def new_mapping(self, *args, labelfmt="f({})={}"):
        """Build the CNF representation of a mapping between two sets.

        Parameters
        ----------

        """

        def __init__(self, startid, B, **kwargs):
            r"""Generator for the clauses of a mapping between to sets

            This generates of the constraints on variables :math:`v(i,j)`
            where :math:`i \in D` and :math:`j in R`, so that they
            represent a mapping (or a relation) between the two sets,
            expressed in unary (i.e. :math:`v(i,j)` expresses whether
            :math:`i` is mapped to :math:`j` or not).

            Parameters
            ----------
            B : BaseBipartiteGraph
                the domain of the mapping

            R : int
                the range of the mapping

            sparsity_pattern : bipartite_graph, optional
                each element of the domain is allowed to be mapped
                only into certain range elements. The graph represents
                which range elements are compatible with a specific
                domain element.

            var_name: function, optional
                given :math:`i` and :math`j` the function must produce the
                name of variable :math`v(i,j)`

            complete: bool, optional
                every element of :math:`D` must have an image (default: true)

            functional: bool, optional
                every element of :math:`D` must have at most one image (default: false)

            surjective: bool, optional
                every element of :math:`R` must have a pre-image (default: false)

            injective: bool, optional
                every element of :math:`R` must have at most one pre-image (default: false)

            nondecreasing: bool, optional
                the mapping is going to be non decresing, with respect to
                the order of domain and range (default: false)

            """
            self.B = B

            # optional parameters of the mapping
            self.Complete = kwargs.pop('complete', True)
            self.Functional = kwargs.pop('functional', False)
            self.Surjective = kwargs.pop('surjective', False)
            self.Injective = kwargs.pop('injective', False)

            self.NonDecreasing = kwargs.pop('nondecreasing', False)

            # variable name scheme
            self.VG = BipartiteEdgesVariables(startid, B)

        def variables(self):
            return self.VG

        def clauses(self):

            U, V = self.B.parts()

            m = self.VG

            # Completeness axioms
            if self.Complete:
                for u in U:
                    yield list(m(u, None))

            # Surjectivity axioms
            if self.Surjective:
                for v in V:
                    yield list(m(None, v))

            # Injectivity axioms
            if self.Injective:
                for v in V:
                    L = self.B.left_neighbors(v)
                    for u1, u2 in combinations(L, 2):
                        yield [-m(u1, v), -m(u2, v)]

            # Functionality axioms
            if self.Functional:
                for u in U:
                    R = self.B.right_neighbors(u)
                    for v1, v2 in combinations(R, 2):
                        yield [-m(u, v1), -m(u, v2)]

            # Mapping is monotone non-decreasing
            if self.NonDecreasing:
                for (u1, u2) in combinations(U, 2):
                    for (v1, v2) in product(self.B.right_neighbors(u1), self.B.right_neighbors(u2)):
                        if v1 > v2:
                            yield [-m(u1, v1), -m(u1, v2)]

    class binary_mapping(object):
        """Binary CNF representation of a mapping between two sets."""

        Domain = None
        Range = None
        Bits = None

        Injective = False
        NonDecreasing = False

        @staticmethod
        def var_name(i, b):
            return "Y_{{{0},{1}}}".format(i, b)

        def variables(self):
            for v, b in product(self.Domain, range(0, self.Bits)):
                yield self.var_name(v, b)

        def __init__(self, D, R, **kwargs):
            r"""Generator for the clauses of a binary mapping between D and :math:`R`

            This generates of the constraints on variables
            :math:`v(i,0)...v(i,k-1)` where :math:`i \in D` and
            :math:`v(i,0)...v(i,k-1)` is a binary of :math:`k` bits, so
            that the first :math:`|R|` string in :math:`{0,1}^k` (in
            lexicographic order) encode the elements of :math:`R`.

            Parameters
            ----------
            D : iterable
                the domain of the mapping

            R : iterable
                the length of the bit strings

            var_name: function, optional
                given :math:`i` and :math`b` the function must produce the
                name of variable :math`v(i,b)`

            injective: bool, optional
                every bitstring must have at most one pre-image (default: false)

            nondecreasing: bool, optional
                the mapping must be non decreasing (default: false)

            """
            self.Domain = list(D)
            self.Range = list(R)
            self.Bits = int(ceil(log(len(R), 2)))

            # optional parameters of the mapping
            self.Injective = kwargs.pop('injective', False)
            self.NonDecreasing = kwargs.pop('nondecreasing', False)
            # variable name scheme
            self.var_name = kwargs.pop('var_name', self.var_name)

            if kwargs:
                raise TypeError('Unexpected **kwargs: %r' % kwargs)

            self.ImageToBits = {}
            self.BitsToImage = {}

            for i, bs in islice(enumerate(product([0, 1], repeat=self.Bits)),
                                len(self.Range)):

                self.ImageToBits[self.Range[i]] = bs
                self.BitsToImage[bs] = self.Range[i]

        def image_to_bitstring(self, im):
            return self.ImageToBits[im]

        def bitstring_to_image(self, bs):
            return self.BitsToImage[bs]

        def forbid_bitstring(self, i, bs):
            """Generates a clause that exclude 'i -> bs' mapping """
            return [(bs[b] == 0, self.var_name(i, self.Bits - 1 - b))
                    for b in range(self.Bits)]

        def forbid_image(self, i, j):
            """Generates a clause that exclude 'i -> j' mapping """
            return self.forbid_bitstring(i, self.ImageToBits[j])

        def clauses(self):

            # Avoid strings that do not correspond to elements from the range
            for i, bs in product(
                    self.Domain,
                    islice(product([0, 1], repeat=self.Bits), len(self.Range),
                           None)):
                yield self.forbid_bitstring(i, bs)

            # Injectivity
            if self.Injective:
                for j in self.Range:
                    for i1, i2 in combinations(self.Domain, 2):
                        yield self.forbid_image(i1, j) + self.forbid_image(
                            i2, j)

            # Enforce Non Decreasing Mapping
            if self.NonDecreasing:
                pairs_of_maps = product(combinations(self.Domain, 2),
                                        combinations(self.Range, 2))

                for (i1, i2), (j1, j2) in pairs_of_maps:
                    yield self.forbid_image(i1, j2) + self.forbid_image(i2, j1)
