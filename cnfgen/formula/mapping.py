#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""CNF encoding of mapping

The module defines functionality to conviniently represent mapping,
- in unary encoding
- in binary encoding
- in sparse unary encoding

The module implements the :py:class:`CNFMapping` object, which is
supposed to be inherited from the :py:class:`VariablesManager` object.

Copyright (C) 2019-2021  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from math import ceil, log
from itertools import combinations, product, islice

from cnfgen.graphs import BipartiteGraph, CompleteBipartiteGraph
from cnfgen.formula.variables import BipartiteEdgesVariables, BaseVariableGroup
from cnfgen.formula.variables import VariablesManager


class UnaryMappingVariables(BipartiteEdgesVariables):
    """A group of variables representing a mapping

    The mapping is represented in unary, where variables
    :math:`f_{i,j}` represent atoms :math:`f(i)=j`.

    Assuming :math:`i \\in D` and :math:`j \\in R`, to all pairs
    :math:`D \\times R` are necessarily available. The ones that are
    possible are specified by a bipartite graph :math:`G=(D,R,E)`.

    """
    def __init__(self, formula, G, labelfmt):
        BipartiteEdgesVariables.__init__(self, formula, G, labelfmt=labelfmt)

    def domain(self, v=None):
        """The domain of the mapping

        If `v` is None it returns the domain of the mapping.
        Otherwise it returns the sequence of elements which is
        possible to map to `v`."""
        if v is None:
            U, _ = self.G.parts()
            return U
        return self.G.left_neighbors(v)

    def range(self, u=None):
        """The range of the mapping

        If `u` is None it returns the range of the mapping.
        Otherwise it returns the sequence of all elements to which `u`
        can be mapped."""
        if u is None:
            _, V = self.G.parts()
            return V
        return self.G.right_neighbors(u)


class BinaryMappingVariables(BaseVariableGroup):
    """A group of variables representing a mapping to bitstrings

    Given a domain :math:`[n]` and a range :math:`[m]`, this group
    of variables represent a mapping.

    Variables are :math:`v(i,k-1)...v(i,0)` for :math:`i \\in D`.
    Each :math:`v(i,k-1)...v(i,0)` is a string of :math:`k` bits, and
    represents the image of :math:`i \\in [m]`. The value :math:`k` is
    set so that
    """
    def __init__(self, formula, n, m, labelfmt='v({},{})'):
        """Group of variables represeting the mapping

        Variables representing the mapping from `n` elements to
        `m` elements, represented as strings of bits.

        Notice that domain is indexed from 1, the range is indexed (in
        binary) from zero.

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        n : int
            size of the domain ( must be > 0)
        m : int
            size of the range ( must be > 0)
        labelfmt: str
            format string for the variable labels

        Examples
        --------
        >>> F = CNFMapping()
        >>> f = BinaryMappingVariables(F,4,6,labelfmt='f({},{})')
        >>> len(f)
        12
        >>> print(*f.label())
        f(1,2) f(1,1) f(1,0) f(2,2) f(2,1) f(2,0) f(3,2) f(3,1) f(3,0) f(4,2) f(4,1) f(4,0)
        >>> print(f(3,2))
        7
        >>> print(*f(2,None))
        4 5 6
        """
        if (m < 1 or n < 1):
            raise ValueError("n and m must be positive")
        self.domain_size = n
        self.range_size = m
        self.id_offset = formula.number_of_variables()
        self.bitlength = int(ceil(log(m, 2)))
        nvar = n * self.bitlength
        BaseVariableGroup.__init__(self, formula, nvar, labelfmt=labelfmt)
        self.flips = []
        for flip in product([1, -1], repeat=self.bitlength):
            self.flips.append(flip)


    def domain(self):
        """The domain of the mapping

        If `v` is None it returns the domain of the mapping.
        Otherwise it returns the sequence of elements which is
        possible to map to `v`.

        Examples
        --------
        >>> F = CNFMapping()
        >>> f = BinaryMappingVariables(F,4,6)
        >>> f.domain() == range(1,5)
        True
        >>> F = CNFMapping()
        >>> f = BinaryMappingVariables(F,20,6)
        >>> f.domain() == range(1,21)
        True
        """
        return range(1, self.domain_size+1)

    def range(self):
        """The range of the mapping

        If `u` is None it returns the range of the mapping.
        Otherwise it returns the sequence of all elements to which `u`
        can be mapped.

        Examples
        --------
        >>> F = CNFMapping()
        >>> f = BinaryMappingVariables(F,5,12)
        >>> f.range() == range(0,12)
        True
        >>> len(f)
        20
        >>> F = CNFMapping()
        >>> f = BinaryMappingVariables(F,5,15)
        >>> f.range() == range(0,15)
        True
        >>> len(f)
        20
        """
        return range(self.range_size)

    def indices(self, *pattern):
        """Implementation of :py:classmethod:`BaseVariableGroup.indices`

        Parameters
        ----------
        pattern : sequences(positive integers or None)
            the pattern of the indices

        Returns
        -------
        a tuple or an itertools.product object

        Examples
        --------
        >>> F = CNFMapping()
        >>> f = BinaryMappingVariables(F,5,12)
        >>> print(*f.indices(3,None))
        (3, 3) (3, 2) (3, 1) (3, 0)
        >>> print(*f.indices(None,1))
        (1, 1) (2, 1) (3, 1) (4, 1) (5, 1)
        """
        if len(pattern) not in [0, 2]:
            raise ValueError("Requires either none or two arguments.")

        I = self.domain()
        B = range(self.bitlength-1, -1, -1)

        if len(pattern) == 0:
            i = None
            b = None
        else:
            i = pattern[0]
            b = pattern[1]

        if i is not None:
            if not (1 <= i <= self.domain_size):
                raise ValueError("Preimage is not in the domain")
            I = [i]

        if b is not None:
            if not (0 <= b < self.bitlength):
                raise ValueError("Bit position is not in the domain")
            B = [b]

        return ((i, b) for i in I for b in B)

    def _unsafe_index_to_lit(self, index):
        """Converts (i,b) into a variable ID.

        Parameters
        ----------
        index: a pair of positive integers
            an edge of the graph

        Returns
        -------
        int

        Warning: only for internal use. It does not check of the
        correctness of the arguments.
        """
        i, b = index
        return i * self.bitlength - b + self.id_offset

    def to_index(self, lit):
        """Convert a literal to the corresponding pair (i,b)

        Parameters
        ----------
        lit : positive or negative literal
            -ID or +ID for the ID of the variable

        Returns
        -------
            pair of integers

        Raises
        ------
        ValueError
            when `lit` is not within the appropriate intervals

        Examples
        --------
        >>> F = CNFMapping()
        >>> F.update_variable_number(10)
        >>> V = BinaryMappingVariables(F,10, 13, labelfmt='v({},{})')
        >>> len(V)
        40
        >>> V.to_index(11)
        (1, 3)
        >>> V.to_index(16)
        (2, 2)
        >>> V.to_index(-18)
        (2, 0)
        >>> V.to_index(48)
        (10, 2)
        """
        var = abs(lit)
        if var not in self:
            raise ValueError('Index out of range')
        var = var - self.id_offset
        preimage = (var - 1) // self.bitlength + 1
        bitpos = self.bitlength - 1 - (var - 1) % self.bitlength
        return preimage, bitpos

    def bits(self):
        return self.bitlength

    def forbid(self, i, j):
        '''The clause that forbids i-->j

        Create the unique clause that is false if and only if i is
        mapped to the bit string corresponding to j

        Examples
        --------
        >>> F = CNFMapping()
        >>> V = BinaryMappingVariables(F,4,6)
        >>> V.forbid(2,0)
        [4, 5, 6]
        >>> V.forbid(2,7)
        [-4, -5, -6]
        >>> V.forbid(4,3)
        [10, -11, -12]
        '''
        if j >= 2**self.bitlength:
            raise ValueError("j must be between 0 and {}".format(2**self.bitlength-1))
        pairs = zip(self.flips[j], self(i, None))
        return [ s*v for s,v in pairs ]


class CNFMapping(VariablesManager):
    """CNF with a variable manager

    A CNF formula needs to keep track on variables.
    A :py:class:`VariableManager` allows to do that, while providing
    a nice interface that allows to focus on variable meaning.

    Attributes
    ----------
    name : dict
        associate a variable / literal to its label

    Methods
    -------
    new_mapping(n, m, label):
        add the variables representing a mapping (in unary)

    new_sparse_mapping(B, label):
        add the variables representing a sparse mapping

    Examples
    --------
    >>> F=CNFMapping()
    >>> f = F.new_mapping(2,3,label='f_{{{},{}}}')
    >>> F.number_of_variables()
    6
    >>> B = BipartiteGraph(4,4)
    >>> B.add_edges_from([(1,2), (1,4), (2,3), (4,2), (4,3)])
    >>> g = F.new_sparse_mapping(B, label='g_{{{},{}}}')
    >>> F.number_of_variables()
    11
    >>> print(*f.label())
    f_{1,1} f_{1,2} f_{1,3} f_{2,1} f_{2,2} f_{2,3}
    >>> print(*g.label())
    g_{1,2} g_{1,4} g_{2,3} g_{4,2} g_{4,3}
    """

    def __init__(self, clauses=None, description=None):
        """Construct a variable manager object
        """
        self._groups = []
        VariablesManager.__init__(self,
                                  clauses=clauses,
                                  description=description)

    def new_mapping(self, n, m, label='f({})={}'):
        """Adds variables for a mapping from `n` to `m`

        Creates a group of variables for a mapping from :math:`n`
        elements to :math:`m` elements represented as boolean
        variables :math:`f_{i,j}` for :math:`i in [n]` and :math:`j in
        [m]`.

        Parameters
        ----------
        n : int
            size of the domain
        m : int
            size of the range

        label : str, optional
            string representation of the variables

        Returns
        -------
        UnaryMappingVariables, the new variable group

        Examples
        --------
        >>> F = CNFMapping()
        >>> f = F.new_mapping(4,10)
        >>> f(2,1)
        11
        >>> f(1,8)
        8
        >>> F.number_of_variables()
        40
        >>> f.label(3,8)
        'f(3)=8'
        """
        if n < 0 or m < 0:
            raise ValueError("n and m must be non negative integers")
        B = CompleteBipartiteGraph(n, m)
        newgroup = UnaryMappingVariables(self, B, labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup


    def new_sparse_mapping(self, B, label='f({})={}'):
        """Adds variables for a sparse mapping

        Creates a group of variables representing a mapping.
        The representation is sparse in the sense that the domain and
        range are the two sides of a bipartite graph :math:`B`.
        The map :math:`u \\mapsto v` is available if and only if the
        edge :math:`(u,v) \\in E(B)`.

        Parameters
        ----------
        B : BipartiteGraph
            sparse representation of the mapping

        label : str, optional
            string representation of the variables

        Returns
        -------
        UnaryMappingVariables, the new variable group

        Examples
        --------
        >>> B = BipartiteGraph(5,3)
        >>> B.add_edge(2,1)
        >>> B.add_edge(1,3)
        >>> B.add_edge(2,2)
        >>> B.add_edge(3,3)
        >>> B.add_edge(4,3)
        >>> B.add_edge(4,2)
        >>> B.add_edge(5,1)
        >>> F = CNFMapping()
        >>> f = F.new_sparse_mapping(B)
        >>> f(2,2)
        3
        >>> f(4,3)
        6
        >>> F.number_of_variables()
        7
        >>> f.label(4,2)
        'f(4)=2'
        """
        if not B.is_bipartite():
            raise ValueError("B must be an instance of BipartiteGraph")
        newgroup = UnaryMappingVariables(self, B, labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup


    def new_binary_mapping(self, n, m, label='v({},{})'):
        """Adds variables for a mapping from `n` to `m` encoded in binary

        Creates a group of variables representing a mapping from
        :math:`\\{1,\\ldots,n}` to :math:`\\{0,\\ldots,m-1\\}`.

        The mapping is represented as a sequence of :math:`n` binary
        strings of length :math:`k`, where :math:`k` is the smallest
        integer so that :math:`m \\leq 2^k`.

        The element mapped to :math:`i` is represented using :math:`k`
        boolean variables :math:`v(i,k-1) \\ldots v(i,0)`.

        Parameters
        ----------
        n : int
            size of the domain
        m : int
            size of the range

        label : str, optional
            string representation of the variables

        Returns
        -------
        BinaryMappingVariables, the new variable group

        Examples
        --------
        >>> F = CNFMapping()
        >>> f = F.new_binary_mapping(4,14)
        >>> F.number_of_variables()
        16
        >>> f(2,3)
        5
        >>> f(4,0)
        16
        """
        if n < 0 or m < 0:
            raise ValueError("n and m must be non negative integers")
        newgroup = BinaryMappingVariables(self, n, m, labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup


    def force_complete_mapping(self, f):
        """Enforce the mapping `f` to be complete

        Add the clauses that make the mapping `f` complete.
        Namely that all elements in the domain are mapped to some
        element in the range. These clauses do not exclude the
        possibility that an element from the domain is mapped to
        multiple elements in the range (indeed that may be the case
        for unary representation).

        (See py:classmethod:`CNFMapping.force_functional_mapping`)

        Examples
        --------
        >>> C = CNFMapping()
        >>> f = C.new_mapping(10,5)
        >>> C.force_complete_mapping(f)
        >>> C[2]
        [11, 12, 13, 14, 15]
        >>> len(C)
        10
        >>> g = C.new_binary_mapping(4,14)
        >>> C.force_complete_mapping(g)
        >>> len(C)
        18
        >>> C[10]
        [-51, -52, -53, 54]
        >>> C[11]
        [-51, -52, -53, -54]
        """
        if not isinstance(f,
                          (UnaryMappingVariables,BinaryMappingVariables)):
            ValueError('f must be either UnaryMappingVariables or BinaryMappingVariables')

        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")

        if isinstance(f, BinaryMappingVariables):
            m = len(f.range())
            k = f.bits()
            for i in f.domain():
                for j in range(m, 2**k):
                    self.add_clause(f.forbid(i, j))
            return

        if isinstance(f, UnaryMappingVariables):
            for x in f.domain():
                self.add_clause(f(x, None))

    def force_functional_mapping(self, f):
        """Enforce the mapping `f` to be functional

        Add the clauses that enforce the mapping `f` to be a partial
        function. Namely that every element in the domain can be
        mapped to at most one element in the range.

        Together with
        :py:classmethod:`CNFMapping.force_complete_mapping`, this
        enforces the mapping to be a total function.

        Examples
        --------
        >>> C = CNFMapping()
        >>> f = C.new_mapping(10,5)
        >>> C.force_functional_mapping(f)
        >>> len(C)
        100
        >>> C.number_of_variables()
        50
        >>> max(len(cls) for cls in C)
        2
        >>> C[7]
        [-3, -4]
        >>> len(C)
        100
        """
        if not isinstance(f,
                          (UnaryMappingVariables,BinaryMappingVariables)):
            ValueError('f must be either UnaryMappingVariables or BinaryMappingVariables')

        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")
        if isinstance(f, BinaryMappingVariables):
            return
        if isinstance(f, UnaryMappingVariables):
            for x in f.domain():
                self.add_linear(list(f(x, None)), '<=', 1)

    def force_surjective_mapping(self, f):
        """Enforce the mapping `f` to be surjective

        Add the clauses that make the mapping `f` surjective.
        Namely that all elements in the range have at least one
        element in the domain mapped to it.

        This method works only for mapping represented in unary.

        Examples
        --------
        >>> C = CNFMapping()
        >>> f = C.new_mapping(10,5)
        >>> C.force_surjective_mapping(f)
        >>> C[1]
        [2, 7, 12, 17, 22, 27, 32, 37, 42, 47]
        >>> len(C)
        5
        """
        if not isinstance(f, UnaryMappingVariables):
            ValueError('f must be a UnaryMappingVariables')

        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")

        for y in f.range():
            self.add_clause(f(None, y))


    def force_injective_mapping(self, f):
        """Enforce the mapping `f` to be injective

        Add the clauses that make the mapping `f` injective.
        Namely that all elements in the range have at most one element
        in the domain mapped to it.

        Examples
        --------
        >>> C = CNFMapping()
        >>> f = C.new_mapping(10,5)
        >>> C.force_injective_mapping(f)
        >>> C[0]
        [-1, -6]
        >>> C[1]
        [-1, -11]
        >>> C[45]
        [-2, -7]
        >>> len(C)
        225
        """
        if not isinstance(f,
                          (UnaryMappingVariables,BinaryMappingVariables)):
            ValueError('f must be either UnaryMappingVariables or BinaryMappingVariables')

        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")

        if isinstance(f, UnaryMappingVariables):
            for y in f.range():
                self.add_linear(list(f(None, y)), '<=', 1)

        if isinstance(f, BinaryMappingVariables):
            for y in f.range():
                for x1, x2 in combinations(f.domain(), 2):
                    self.add_clause(f.forbid(x1, y) + f.forbid(x2, y))


    def force_nondecreasing_mapping(self, f):
        """Enforce the mapping `f` to be non decreasing

        Add the clauses that make the mapping `f` injective.
        Namely that all elements in the range have at most one element
        in the domain mapped to it.

        Examples
        --------
        >>> C = CNFMapping()
        >>> B = BipartiteGraph(2,3)
        >>> B.add_edge(1,2)
        >>> B.add_edge(1,3)
        >>> B.add_edge(2,1)
        >>> B.add_edge(2,3)
        >>> f = C.new_sparse_mapping(B)
        >>> C.force_nondecreasing_mapping(f)
        >>> len(C)
        2
        >>> C[0]
        [-1, -3]
        >>> C[1]
        [-2, -3]
        >>> g = C.new_binary_mapping(2,4)
        >>> C.force_nondecreasing_mapping(g)
        >>> len(C)
        8
        """
        if not isinstance(f,
                          (UnaryMappingVariables,BinaryMappingVariables)):
            ValueError('f must be either UnaryMappingVariables or BinaryMappingVariables')

        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")


        if isinstance(f, UnaryMappingVariables):
            fd = f.to_dict()
            for (u1, u2) in combinations(f.domain(), 2):
                for (v1, v2) in product(f.range(u1), f.range(u2)):
                    if v1 > v2:
                        self.add_clause([-fd[(u1, v1)], -fd[(u2, v2)]])

        if isinstance(f, BinaryMappingVariables):
            for (u1, u2) in combinations(f.domain(), 2):
                for (v1, v2) in combinations(f.range(), 2):
                    self.add_clause(f.forbid(u1, v2) + f.forbid(u2, v1))
