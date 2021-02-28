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

from itertools import combinations, product

from cnfgen.graphs import BipartiteGraph, CompleteBipartiteGraph
from cnfgen.variables import BipartiteEdgesVariables, VariablesManager


class MappingVariables(BipartiteEdgesVariables):
    """A group of variables representing a matching.

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
            size of the domain (when needed)
        m : int
            size of the range (when needed)

        label : str, optional
            string representation of the variables

        Returns
        -------
        MappingVariables, the new variable group

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
        newgroup = MappingVariables(self, B, labelfmt=label)
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
        MappingVariables, the new variable group

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
        if B.number_of_edges() == 0:
            raise ValueError("B must contain edges")
        newgroup = MappingVariables(self, B, labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup

    def force_complete_mapping(self, f):
        """Enforce the mapping `f` to be complete

        Add the clauses that make the mapping `f` complete.
        Namely that all elements in the domain are mapped to some
        element in the range. These clauses do not exclude the
        possibility that an element from the domain is mapped to
        multiple elements in the range.

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

        """
        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")

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
        >>> max(len(cls) for cls in C)
        2
        >>> C[7]
        [-3, -4]
        >>> len(C)
        100

        """
        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")

        for x in f.domain():
            self.add_linear(list(f(x, None)), '<=', 1)


    def force_surjective_mapping(self, f):
        """Enforce the mapping `f` to be surjective

        Add the clauses that make the mapping `f` surjective.
        Namely that all elements in the range have at least one
        element in the domain mapped to it.

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
        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")

        for y in f.range():
            self.add_linear(list(f(None, y)), '<=', 1)


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
        """
        if f.parent_formula() != self:
            raise ValueError("mapping f was created from a different formula")

        for (u1, u2) in combinations(f.domain(), 2):
            for (v1, v2) in product(f.range(u1), f.range(u2)):
                if v1 > v2:
                    self.add_clause([-f(u1, v1), -f(u2, v2)])
