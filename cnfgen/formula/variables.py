#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Keep tracks of the variable of a formula.

The module defines a variable manager, that formulas could either use
of specialize. It allows to generates
- single variables
- variables for some tuples of indices
- variables for the edges of a bipartite/direct/simple graph
- in unary encoding
- in binary encoding
- in sparse unary encoding

The module implements the :py:class:`VariablesManager` object, which
is supposed to be inherited from the formula object.

Copyright (C) 2019-2021  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from itertools import product
from itertools import combinations
from itertools import combinations_with_replacement
from itertools import permutations

from bisect import bisect_right

from math import ceil, log

from cnfgen.graphs import BaseBipartiteGraph, BipartiteGraph
from cnfgen.graphs import Graph, DirectedGraph
from cnfgen.graphs import CompleteBipartiteGraph

from cnfgen.formula.basecnf import BaseCNF
from cnfgen.formula.linear import CNFLinear

class BaseVariableGroup():
    """Base object for variable groups

    This object is meant to the base class for the actual variable
    groups, all to be used internally by :py:class:`VariablesManager`.

    In general a variable group is a mapping between some set of
    indices and the corresponding sequential variable IDs (as seen in
    a DIMACS file, for example).
    """

    def __init__(self, formula, N, labelfmt=None):
        """Creates a variables group object

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        N: integer
            number of variables to add
        labelfmt:
            format string for the label of the variables
        """
        self.formula = formula
        self.ids = range(formula.number_of_variables() + 1,
                         formula.number_of_variables() + N+1)  # range excludes last element
        self.labelfmt = labelfmt

    def parent_formula(self):
        """The formula associated to the variable group

        Examples
        --------
        >>> F1 = BaseCNF()
        >>> F2 = BaseCNF()
        >>> G = BaseVariableGroup(F1,10)
        >>> G.parent_formula() == F1
        True
        >>> G.parent_formula() == F2
        False
        """
        return self.formula

    def __call__(self, *index):
        """Convert the index of a variable into its ID.

        An `index` of length 0 or which contains None values will be
        considered a projection pattern of the set of legal indices of
        the variable group. In that case the return value will be
        a generator that iterates through all variable IDs which
        corresponds to indices that at compatible with that pattern.

        Parameters
        ----------
        index : sequences(positive integers or None)
            the index/pattern of the variable

        Returns
        -------
            int / iterable(int)

        Raises
        ------
        ValueError
            when the index (or index pattern) is not compatible with
            the index domain.

        Examples
        --------
        >>> F = BaseCNF()
        >>> V = VariablesManager(F)
        >>> m = V.new_block(2,5,label='m[{},{}]')
        >>> isinstance(m,BaseVariableGroup)
        True
        >>> print(len(m))
        10
        >>> print(*m.indices(2,4))
        (2, 4)
        >>> print(list(m.indices()))
        [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5)]
        >>> print(list(m.indices(None,None)))
        [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5)]
        >>> print(list(m.indices(1,None)))
        [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
        >>> print(list(m.indices(None, 3)))
        [(1, 3), (2, 3)]
        """
        isProjection = len(index) == 0 or None in index
        IDs = (self._unsafe_index_to_lit(t) for t in self.indices(*index))

        if isProjection:
            return IDs
        else:
            return next(IDs)

    def to_dict(self):
        D = {t: self._unsafe_index_to_lit(t) for t in self.indices()}
        return D

    def __len__(self):
        """The number of variables in the group"""
        return len(self.ids)

    def __getitem__(self,choices):
        """Access a variable in the group"""
        return self.ids[choices]

    def __iter__(self):
        return iter(self.ids)

    def __contains__(self, lit):
        """Check in the literal is in the group"""
        return abs(lit) in self.ids

    def label(self, *pattern):
        """Convert the index of a variable into its label.

        If the `pattern` is contains None values, these will be
        considered as "don't care" values. The implementation should
        return a generator enumerating all the IDs compatible with the
        given pattern.
        """
        isProjection = len(pattern) == 0 or None in pattern

        labels = (self.labelfmt.format(*t) for t in self.indices(*pattern))

        if isProjection:
            return labels
        else:
            return next(labels)

    def indices(self, *pattern):
        """Outputs all the indices matching the given pattern"""
        raise NotImplementedError

    def to_index(self, lit):
        """Convert a literal of the index sequence corresponding to the variable"""
        raise NotImplementedError

    def _unsafe_index_to_lit(self, index):
        """Converts a variable index into a variable ID

        Parameters
        ----------
        index: sequence of positive integers
            the index of a variable

        Returns
        -------
        int

        Warning: only for internal use. It does not check of the
        correctness of the arguments.
        """
        raise NotImplementedError


class SingletonVariableGroup(BaseVariableGroup):
    """A group made by a single variable

    Examples
    --------
    >>> c = BaseCNF()
    >>> c.update_variable_number(11)
    >>> X1 = SingletonVariableGroup(c,'X')
    >>> c.update_variable_number(22)
    >>> X2 = SingletonVariableGroup(c,'Y')
    >>> print(X1.label())
    X
    >>> print(*X1.indices())
    ()
    >>> X1()
    12
    >>> X2()
    23
    >>> print(X2.label())
    Y
    >>> print(X2.to_index(23))
    ()
    """

    def __init__(self, formula, name):
        """Variables group for a single variable

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        name: str
            the name of the variable
        """
        self.name = name
        BaseVariableGroup.__init__(self, formula, 1, labelfmt=name)

    def __call__(self):
        return self[0]

    def label(self):
        return self.name

    def indices(self, *pattern):
        """Outputs all the indices matching the given pattern"""
        if len(pattern) > 0:
            raise ValueError("Singleton variable groups have a 0-arity index")
        return [()]

    def to_index(self, lit):
        """Convert a literal of the corresponding variable index"""
        if abs(lit) != self[0]:
            raise ValueError("Literal do not belong to this variable group")
        return ()


class BlockOfVariables(BaseVariableGroup):
    """Group of variables, indexed by a cartesian product.

    This objects represents groups of variables that are indexed by
    some tuples of integers. For example we can have variables
    :math:`p_{i,j}` for :math:`i in [10]` and :math:`j in [7]`.

    A group can have an arbitrary number of indices, each ranging
    independently between :math:`1` and some arbitrary integer.

    This object is meant to be used internally by
    :py:class:`VariablesManager`.

    Examples
    --------
    >>> F = BaseCNF()
    >>> G = BlockOfVariables(F,[2,3],'G[{},{}]')
    >>> print(*G.label())
    G[1,1] G[1,2] G[1,3] G[2,1] G[2,2] G[2,3]
    >>> print(*G.indices())
    (1, 1) (1, 2) (1, 3) (2, 1) (2, 2) (2, 3)
    >>> G(2,1)
    4
    >>> F = BaseCNF()
    >>> V = VariablesManager(F)
    >>> p = V.new_block(10,5,label='p({},{})')
    >>> q = V.new_block(3,3,label='q({},{})')
    >>> isinstance(p,BlockOfVariables)
    True
    >>> print(len(p))
    50
    >>> print(len(q))
    9
    >>> print(p.to_index(23))
    [5, 3]
    >>> print(q.to_index(54))
    [2, 1]
    >>> print(list(q.indices()))
    [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
    >>> print(p(2,3))
    8
    >>> print(list(p(None,3)))
    [3, 8, 13, 18, 23, 28, 33, 38, 43, 48]
    >>> print(q(1,1))
    51
    >>> 52 in q
    True
    >>> 12 in q
    False
    >>> print(q.label(1,1))
    q(1,1)
    >>> print(*q.label(2,None))
    q(2,1) q(2,2) q(2,3)
    >>> print(p.label(4,2))
    p(4,2)
    >>> print(list(p.indices(3,None)))
    [(3, 1), (3, 2), (3, 3), (3, 4), (3, 5)]
    >>> print(p.to_index(p(4,3)))
    [4, 3]
    """

    def __init__(self, formula, ranges, labelfmt=None):
        """Creates a variables group object

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        ranges: list(integer)
            ranges of the indices
        labelfmt: str
            format string for the variable labels
        """
        if labelfmt is None:
            labelfmt = 'X(' + ','.join(['{}'] * len(ranges)) + ')'
        # Check if the format strings can get all parameters
        try:
            labelfmt.format(*ranges)
        except IndexError:
            raise ValueError(
                'label must be a valid format string for all indices')

        if len(ranges) == 0:
            raise ValueError('ranges must have at least dimension one')

        valid_ranges = 0
        for x in ranges:
            if isinstance(x,int) and x >= 0:
                valid_ranges += 1

        if valid_ranges != len(ranges):
            raise ValueError('ranges must be a sequence of non negative integers')

        weights = [1]  # cumulative products
        for r in ranges[::-1]:
            weights.append(weights[-1] * r)

        self.ranges = ranges
        self.N = weights.pop()  # number of variables
        self.weights = weights[::-1]
        self.offset = formula.number_of_variables() + 1
        BaseVariableGroup.__init__(self, formula, self.N, labelfmt)

    def indices(self, *pattern):
        """Implementation of :py:classmethod:`BaseVariableGroup.indices`

        Parameters
        ----------
        pattern : sequences(positive integers or None)
            the pattern of the indices

        Returns
        -------
        a tuple or an itertools.product object
        """
        if len(pattern) > 0 and len(pattern) != len(self.ranges):
            raise ValueError("Wrong number of indices in the pattern")

        if len(pattern) == 0:
            pattern = [None] * len(self.ranges)

        # non trivial patterns
        x = []
        for i, R in zip(pattern, self.ranges):
            if i is None:
                x.append(range(1, R + 1))
            elif 1 <= i <= R:
                x.append((i, ))
            else:
                raise ValueError("Index {} not withing range {}".format(
                    pattern, self.ranges))

        return product(*x)

    def _unsafe_index_to_lit(self, index):
        """Converts a variable index into a variable ID

        Parameters
        ----------
        index: sequence of positive integers
            the index of a variable

        Returns
        -------
        int

        Warning: only for internal use. It does not check of the
        correctness of the arguments.
        """
        relative = sum((i - 1) * w for i, w in zip(index, self.weights))
        return self.offset + relative

    def to_index(self, lit):
        """Convert a literal to the index sequence corresponding to the variable

        A variable is identified by an integer id, but an associate
        index in the variable group. This function convert the
        variable id into such index. If a negative literal is given,
        the function returns the index of the corresponding variable.

        Parameters
        ----------
        lit : positive or negative literal
            -ID or +ID for the ID of the variable

        Returns
        -------
            sequence(positive integers)

        Raises
        ------
        ValueError
            when `lit` is not within the appropriate intervals

        Examples
        --------
        >>> F = BaseCNF()
        >>> VG = BlockOfVariables(F,[3,5,4,3])
        >>> VG.to_index(1)
        [1, 1, 1, 1]
        >>> VG.to_index(-5)
        [1, 1, 2, 2]
        >>> VG.to_index(179)
        [3, 5, 4, 2]
        >>> VG.to_index(180)
        [3, 5, 4, 3]
        """
        var = abs(lit)
        if var not in self:
            raise ValueError('Index out of range')

        index = []
        residue = var - self.offset
        for w in self.weights:
            index.append(residue // w + 1)
            residue = residue % w
        return index

class WordOfIndicesVariables(BaseVariableGroup):
    """Group of variables corrisponding to fixed sequences of indices

    This objects represents groups of variables that are indexed by
    some sequences of integers from a ground set :math:`[n]`. For example we
    can have variables :math:`p_{S}` for :math:`S in
    \\binom{[n]}{k}[10]` for a fixed :math:`k`.

    Each set is identified by an index, which is just the sequence of
    it's elements, sorted.

    Three types of indices are supported:
    - combinations:
          sorted tuples of length :math:`k` with no repetitions
    - combinations_with_replacement:
          sorted tuples of length :math:`k` with repetitions
    - permutation:
          tuples of length :math:`k` with no repetitions
    - words:
          tuples of length :math:`k` with repetitions

    The latter is very similar to cartesian product variable group.

    Examples
    --------
    >>> F = BaseCNF()
    >>> G = WordOfIndicesVariables(F,4,2,'[{}]')
    >>> print(*G.label())
    [1,2] [1,3] [1,4] [2,3] [2,4] [3,4]
    >>> print(*G.indices())
    (1, 2) (1, 3) (1, 4) (2, 3) (2, 4) (3, 4)
    >>> G(2,3)
    4
    >>> F =BaseCNF()
    >>> V = VariablesManager(F)
    >>> p = V.new_combinations(5,3,label='p({})')
    >>> q = V.new_combinations(3,3,label='q({})')
    >>> print(len(p))
    10
    >>> print(len(q))
    1
    >>> print(p.to_index(4))
    (1, 3, 4)
    >>> print(q.to_index(11))
    (1, 2, 3)
    >>> print(list(p.indices()))
    [(1, 2, 3), (1, 2, 4), (1, 2, 5), (1, 3, 4), (1, 3, 5), (1, 4, 5), (2, 3, 4), (2, 3, 5), (2, 4, 5), (3, 4, 5)]
    >>> print(p(2,3,4))
    7
    >>> print(list(p()))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> print(q(1,2,3))
    11
    >>> 11 in q
    True
    >>> 12 in q
    False
    >>> print(q.label(1,2,3))
    q(1,2,3)
    >>> print(*q.label())
    q(1,2,3)
    >>> print(p.label(1,2,5))
    p(1,2,5)

    """

    def __init__(self, formula, n, k,
                 labelfmt=None,
                 wordtype='combinations'):
        """Creates a variables group object



        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        ranges: list(integer)
            ranges of the indices
        labelfmt: str
            format string for the variable labels
        wordtype: {'combinations', 'permutations','combinations_with_replacement', 'words'}
            the type of indices we want. (default: 'combinations')
        """
        if labelfmt is None:
            labelfmt = 'p_{}'
        # Check if the format strings can get all parameters
        try:
            labelfmt.format(2)
        except IndexError:
            raise ValueError(
                'the label for these variables must have one placeholder')

        if not isinstance(n,int) or not isinstance(k,int) or n < 0 or k < 0:
            raise ValueError(
                'k,n must be integer with 0<= k <= n')

        self.n = n
        self.k = k
        self.wordtype = wordtype
        self.offset = formula.number_of_variables()
        self.vid2seq=[]
        self.seq2vid={}
        if wordtype == 'combinations':
            gen = combinations(range(1, n+1), k)
        elif wordtype == 'combinations_with_replacements':
            gen = combinations_with_replacement(range(1,n+1),k)
        elif wordtype == 'permutations':
            gen = permutations(range(1, n+1), k)
        elif wordtype == 'words':
            gen = product(range(1, n+1), repeat=k)

        vid = self.offset
        for c in gen:
            vid += 1
            self.vid2seq.append(c)
            self.seq2vid[c] = vid

        BaseVariableGroup.__init__(self, formula, len(self.vid2seq), labelfmt)

    def label(self,*pattern):

        def text(idx):
            return ",".join(str(x) for x in idx)

        if len(pattern)==0:
            return iter(self.labelfmt.format(text(x)) for x in self.vid2seq)
        elif pattern in self.seq2vid:
            return self.labelfmt.format(text(pattern))
        else:
            raise ValueError("Pattern does not match the indices in this variable group")


    def indices(self,*pattern):
        """Implementation of :py:classmethod:`BaseVariableGroup.indices`

        Returns
        -------
        all the variable indices
        """
        if len(pattern)==0:
            return iter(self.vid2seq)
        elif pattern in self.seq2vid:
            return [pattern]
        else:
            raise ValueError("Pattern does not match the indices in this variable group")

    def __call__(self,*pattern):
        try:
            return self.seq2vid[pattern]
        except KeyError:
            pass
        if len(pattern) == 0:
            return (self._unsafe_index_to_lit(t) for t in self.indices(*pattern))
        else:
            raise ValueError("Pattern does not match the indices in this variable group")

    def _unsafe_index_to_lit(self, index):
        """Converts a variable index into a variable ID

        Parameters
        ----------
        index: sequence of positive integers
            the index of a variable

        Returns
        -------
        int

        Warning: only for internal use. It does not check of the
        correctness of the arguments.
        """
        return self.seq2vid[index]

    def to_index(self, lit):
        """Convert a literal to the index sequence corresponding to the variable

        A variable is identified by an integer id, but an associate
        index in the variable group. This function convert the
        variable id into such index. If a negative literal is given,
        the function returns the index of the corresponding variable.

        Parameters
        ----------
        lit : positive or negative literal
            -ID or +ID for the ID of the variable

        Returns
        -------
            sequence(positive integers)

        Raises
        ------
        ValueError
            when `lit` is not within the appropriate intervals

        Examples
        --------
        >>> F = BaseCNF()
        >>> VG = BlockOfVariables(F,[3,5,4,3])
        >>> VG.to_index(1)
        [1, 1, 1, 1]
        >>> VG.to_index(-5)
        [1, 1, 2, 2]
        >>> VG.to_index(179)
        [3, 5, 4, 2]
        >>> VG.to_index(180)
        [3, 5, 4, 3]
        """
        var = abs(lit)
        if var not in self:
            raise ValueError('Index out of range')

        return self.vid2seq[var-self.offset-1]


class BipartiteEdgesVariables(BaseVariableGroup):
    """A group of variables matching the edges of a bipartite graph

    This objects represents groups of variables corresponding to the
    edges of a bipartite graph.

    Given a bipartite graph :math:`G=(U,V,E)` represented by an object
    of the class :py:class:`BaseBipartiteGraph`, we have variables
    :math:`e_{u,v}` for :math:`u in U` and :math:`v in U`.

    Warning: if the object representing :math:`G` gets modified, the
    behavior of this object may be inconsistent.

    Examples
    --------
    >>> G = BipartiteGraph(2,3)
    >>> G.add_edge(2,1)
    >>> G.add_edge(1,3)
    >>> G.add_edge(2,2)
    >>> F = BaseCNF()
    >>> F.update_variable_number(11)
    >>> e = BipartiteEdgesVariables(F, G, labelfmt='E[{},{}]')
    >>> print(*[e.label(u,v) for u,v in e.indices()])
    E[1,3] E[2,1] E[2,2]
    >>> print(e(2,1))
    13
    >>> print(e(1,3))
    12
    >>> 14 in e
    True
    >>> 10 in e
    False
    >>> print(len(e))
    3
    >>> print(e.label(1,3))
    E[1,3]
    >>> print(*e.label(2,None))
    E[2,1] E[2,2]
    >>> X = BipartiteEdgesVariables(F, G, labelfmt='X[{},{}]')
    >>> W = BipartiteEdgesVariables(F, G, labelfmt='W[{},{}]')
    >>> print(X.label(2,1))
    X[2,1]
    >>> print(W.label(1,3))
    W[1,3]
    >>> [X.label(u,3) for u in G.left_neighbors(3)]
    ['X[1,3]']
    >>> print(*X.label(None,3))
    X[1,3]
    >>> print(*X.label(1,None))
    X[1,3]
    >>> print(*X.label(None,None))
    X[1,3] X[2,1] X[2,2]
    """

    def __init__(self, formula, G, labelfmt='e_{{{},{}}}'):
        """Variables group for the edges of bipartite G

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        G: BipartiteGraph
            bipartite graph
        labelfmt: str
            format string for the variable labels
        """
        if not isinstance(G, BaseBipartiteGraph):
            raise TypeError(
                "Invalid bipartite graph G: a BaseBipartiteGraph object was expected"
            )

        # Check if the format strings can get all parameters
        try:
            labelfmt.format(1, 1)
        except IndexError:
            raise ValueError(
                'label must be a valid format string for two arguments')

        # offsets
        U, V = G.parts()
        startID = formula.number_of_variables() + 1
        offset = [None, startID]
        for u in U:
            d = G.right_degree(u)
            offset.append(offset[-1] + d)
        assert offset[-1] == G.number_of_edges() + startID
        offset.pop()

        self.G = G
        self.offset = offset
        BaseVariableGroup.__init__(self, formula, G.number_of_edges(),
                                   labelfmt)

    def _unsafe_index_to_lit(self, index):
        """Converts an edge of the graph into a variable ID.

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
        vidx = self.G.right_neighbors(index[0]).index(index[1])
        return self.offset[index[0]] + vidx

    def indices(self, *pattern):
        """Print the label of the edge

        Examples
        --------
        >>> G = BipartiteGraph(2,3)
        >>> G.add_edge(2,1)
        >>> G.add_edge(1,3)
        >>> G.add_edge(2,2)
        >>> F = BaseCNF()
        >>> V = BipartiteEdgesVariables(F, G, labelfmt='X[{},{}]')
        >>> print(*V.indices(None,1))
        (2, 1)
        >>> print(*V.indices(None,2))
        (2, 2)
        >>> print(*V.indices(None,3))
        (1, 3)
        >>> print(*V.indices(1,None))
        (1, 3)
        >>> print(*V.indices(2,None))
        (2, 1) (2, 2)
        >>> print(*V.indices(None,None))
        (1, 3) (2, 1) (2, 2)
        >>> print(*V.indices(2,1))
        (2, 1)
        """
        if len(pattern) not in [0, 2]:
            raise ValueError("Requires either none or two arguments.")

        if len(pattern) == 0:
            u, v = None, None
        else:
            u = pattern[0]
            v = pattern[1]

        if u is None and v is None:
            return self.G.edges()

        if v is None:
            if not (1 <= u <= self.G.left_order()):
                raise ValueError("Vertex u is not in the graph")
            return ((u, v) for v in self.G.right_neighbors(u))
        elif u is None:
            if not (1 <= v <= self.G.right_order()):
                raise ValueError("Vertex v is not in the graph")
            return ((u, v) for u in self.G.left_neighbors(v))
        elif not self.G.has_edge(u, v):
            raise ValueError('({},{}) is not an edge of the graph.'.format(
                u, v))
        else:
            return [(u, v)]

    def to_index(self, lit):
        """Convert a literal to the corresponding edge

        Parameters
        ----------
        lit : positive or negative literal
            -ID or +ID for the ID of the variable

        Returns
        -------
            pair of positive integer

        Raises
        ------
        ValueError
            when `lit` is not within the appropriate intervals

        Examples
        --------
        >>> G = BipartiteGraph(2,3)
        >>> G.add_edge(2,1)
        >>> G.add_edge(1,3)
        >>> G.add_edge(2,2)
        >>> F = BaseCNF()
        >>> F.update_variable_number(100)
        >>> V = BipartiteEdgesVariables(F, G, labelfmt='e[{},{}]')
        >>> V.to_index(102)
        (2, 1)
        >>> V.to_index(101)
        (1, 3)
        >>> V.to_index(103)
        (2, 2)
        """
        var = abs(lit)
        if var not in self:
            raise ValueError('Index out of range')
        u = bisect_right(self.offset, var) - 1
        vidx = var - self.offset[u]
        v = self.G.right_neighbors(u)[vidx]
        assert self.__call__(u, v) == var
        return u, v


class DiGraphEdgesVariables(BaseVariableGroup):
    """A variable groups for the edges of a graph.

    Examples
    --------
    >>> G = DirectedGraph(5)
    >>> G.add_edge(1,2)
    >>> G.add_edge(2,3)
    >>> G.add_edge(3,4)
    >>> G.add_edge(4,5)
    >>> G.add_edge(5,1)
    >>> F = BaseCNF()
    >>> F.update_variable_number(100)
    >>> a = DiGraphEdgesVariables(F, G, labelfmt='a({},{})')
    >>> a.to_index(101)
    (1, 2)
    >>> a.to_index(104)
    (4, 5)
    >>> a(5,1)
    105
    >>> print(*a(4,None))
    104
    >>> print(*a())
    101 102 103 104 105
    >>> print(*a.label())
    a(1,2) a(2,3) a(3,4) a(4,5) a(5,1)
    >>> H = DirectedGraph(5)
    >>> H.add_edge(1,2)
    >>> H.add_edge(1,3)
    >>> H.add_edge(2,3)
    >>> H.add_edge(2,4)
    >>> H.add_edge(5,1)
    >>> F = BaseCNF()
    >>> F.update_variable_number(11)
    >>> b = DiGraphEdgesVariables(F,H,labelfmt='b({},{})',sortby='succ')
    >>> b(1,3)
    14
    >>> b.to_index(12)
    (5, 1)
    >>> b.to_index(12)
    (5, 1)
    >>> print(*b.indices())
    (5, 1) (1, 2) (1, 3) (2, 3) (2, 4)
    >>> print(*b.label())
    b(5,1) b(1,2) b(1,3) b(2,3) b(2,4)
    >>> print(*b.indices(None,3))
    (1, 3) (2, 3)
    """

    def __init__(self, formula, D, labelfmt='e_{{{},{}}}', sortby='pred'):
        """Creates a variables group object

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        D: DirectedGraph
            directed graph
        labelfmt: str
            format string for the variable labels
        sortby: 'pred' or 'succ'
            sort edges by either predecessors or successors (default: predecessors)
        """
        if not isinstance(D, DirectedGraph):
            raise TypeError(
                "Invalid direct graph G: a cnfgen.DirectedGraph object was expected"
            )

        if sortby not in ['pred', 'succ']:
            raise ValueError("'indexby' must be one among 'pred', 'succ'")

        # Check if the format strings can get all parameters
        try:
            labelfmt.format(1, 1)
        except IndexError:
            raise ValueError(
                'label must be a valid format string for two arguments')

        V = D.number_of_vertices()
        B = BipartiteGraph(V, V)

        for u, v in D.edges():
            if sortby == 'pred':
                # successors represented in a bipartite graph
                B.add_edge(u, v)
            else:
                # predecessors represented in a bipartite graph
                B.add_edge(v, u)

        self.sortby = sortby
        self.VG = BipartiteEdgesVariables(formula, B)
        BaseVariableGroup.__init__(
            self, formula, B.number_of_edges(), labelfmt)

    def to_index(self, lit):
        u, v = self.VG.to_index(lit)
        if self.sortby == 'pred':
            return u, v
        else:
            return v, u

    def indices(self, *pattern):
        """
        >>> H = DirectedGraph(5)
        >>> H.add_edge(1,2)
        >>> H.add_edge(1,3)
        >>> H.add_edge(2,3)
        >>> H.add_edge(2,4)
        >>> H.add_edge(5,1)
        >>> F = BaseCNF()
        >>> F.update_variable_number(11)
        >>> b = DiGraphEdgesVariables(F,H,labelfmt='b({},{})',sortby='succ')
        >>> print(*b.indices())
        (5, 1) (1, 2) (1, 3) (2, 3) (2, 4)
        >>> print(*b.label())
        b(5,1) b(1,2) b(1,3) b(2,3) b(2,4)
        >>> print(*b.indices(None,3))
        (1, 3) (2, 3)
        >>> print(*b.indices(2,None))
        (2, 3) (2, 4)
        """
        if self.sortby == 'pred':
            return self.VG.indices(*pattern)
        else:
            return ((v, u) for u, v in self.VG.indices(*pattern[::-1]))

    def _unsafe_index_to_lit(self, index):
        """Converts an direct edge of the graph into a variable ID.

        Parameters
        ----------
        index: a pair of positive integers
            a direct edge of the graph

        Returns
        -------
        int

        Warning: only for internal use. It does not check of the
        correctness of the arguments.
        """
        if self.sortby == 'pred':
            return self.VG._unsafe_index_to_lit(index)
        else:
            return self.VG._unsafe_index_to_lit(index[::-1])


class GraphEdgesVariables(BipartiteEdgesVariables):
    """A group of variables matching the edges of a simple graph

    This objects represents groups of variables corresponding to the
    edges of a simple graph.

    Given a simple graph :math:`G=(V,E)` represented by an object of
    the class :py:class:`cnfgen.graphs.Graph`, we have variables
    :math:`e_{u,v}` for :math:`\\{u,v\\} in E`.

    Warning: if the object representing :math:`G` gets modified, the
    behavior of this object may be inconsistent.

    Examples
    --------
    >>> G = Graph(4)
    >>> G.add_edge(2,1)
    >>> G.add_edge(3,2)
    >>> G.add_edge(1,3)
    >>> G.add_edge(4,2)
    >>> F = BaseCNF()
    >>> V = GraphEdgesVariables(F, G, labelfmt='E[{},{}]')
    >>> print(*[V.label(u,v) for u,v in V.indices()])
    E[1,2] E[1,3] E[2,3] E[2,4]
    >>> print(V(2,1))
    1
    >>> print(V(1,3))
    2
    >>> 4 in V
    True
    >>> 10 in V
    False
    >>> print(len(V))
    4
    >>> print(V.label(3,1))
    E[1,3]
    >>> print(*V.label(2,None))
    E[1,2] E[2,3] E[2,4]
    >>> print(*V.label(None,2))
    E[1,2] E[2,3] E[2,4]
    >>> print(*V.label())
    E[1,2] E[1,3] E[2,3] E[2,4]
    >>> print(*V.indices(None,2))
    (1, 2) (2, 3) (2, 4)
    """

    def __init__(self, formula, G, labelfmt='e_{{{}{}}}'):
        """Creates a variables group for the edges of G

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        G: cnfgen.graphs.Graph
            graph
        labelfmt: str
            format string for the variable labels
        """
        if not isinstance(G, Graph):
            raise TypeError(
                "Invalid graph G: a cnfgen.graphs.Graph object was expected"
            )

        V = G.number_of_vertices()
        B = BipartiteGraph(V, V)
        for u, v in G.edges():
            u, v = min(u, v), max(u, v)
            if not B.has_edge(u, v):
                B.add_edge(u, v)
        self.BG = BipartiteEdgesVariables(formula, B, labelfmt=labelfmt)
        BaseVariableGroup.__init__(
            self, formula, B.number_of_edges(), labelfmt)

    def _unsafe_index_to_lit(self, index):
        """Converts an edge of the graph into a variable ID.

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
        return self.BG._unsafe_index_to_lit(sorted(index))

    def indices(self, *pattern):
        """Print the label of the edge

        Examples
        --------
        >>> G = Graph(3)
        >>> G.add_edge(2,1)
        >>> G.add_edge(1,3)
        >>> F = BaseCNF()
        >>> V = GraphEdgesVariables(F, G, labelfmt='X[{},{}]')
        >>> print(*V.indices(None,1))
        (1, 2) (1, 3)
        >>> print(*V.indices(None,2))
        (1, 2)
        >>> print(*V.indices(None,3))
        (1, 3)
        >>> print(*V.indices(1,None))
        (1, 2) (1, 3)
        >>> print(*V.indices(2,None))
        (1, 2)
        >>> print(*V.indices(None,None))
        (1, 2) (1, 3)
        >>> print(*V.indices(2,1))
        (1, 2)
        """
        if len(pattern) not in [0, 2]:
            raise ValueError("Requires either none or two arguments.")

        if len(pattern) == 0:
            u = None
            v = None
        else:
            u = pattern[0]
            v = pattern[1]

        # Zero vertices specified
        if u is None and v is None:
            return self.BG.indices()

        # Two vertices specified
        if u is not None and v is not None:
            iu, iv = min(u, v), max(u, v)
            return self.BG.indices(iu, iv)

        # One vertex specified
        if u is not None:
            w = u
        else:
            w = v

        def _gen(vertex):
            yield from ((u, v) for u, v in self.BG.indices(None, vertex))
            yield from ((v, u) for v, u in self.BG.indices(vertex, None) if u != w)

        return _gen(w)

    def to_index(self, lit):
        """Convert a literal to the corresponding edge

        Parameters
        ----------
        lit : positive or negative literal
            -ID or +ID for the ID of the variable

        Returns
        -------
            pair of positive integer

        Raises
        ------
        ValueError
            when `lit` is not within the appropriate intervals

        Examples
        --------
        >>> G = Graph(4)
        >>> G.add_edge(2,1)
        >>> G.add_edge(3,2)
        >>> G.add_edge(1,3)
        >>> G.add_edge(4,2)
        >>> F = BaseCNF()
        >>> F.update_variable_number(100)
        >>> V = GraphEdgesVariables(F, G)
        >>> V.to_index(102)
        (1, 3)
        >>> V.to_index(101)
        (1, 2)
        >>> V.to_index(104)
        (2, 4)
        """
        return self.BG.to_index(lit)



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
        formula:
            formula to which we add a variable group
        n : int
            size of the domain ( must be > 0)
        m : int
            size of the range ( must be > 0)
        labelfmt: str
            format string for the variable labels

        Examples
        --------
        >>> F = BaseCNF()
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
        >>> F = BaseCNF()
        >>> f = BinaryMappingVariables(F,4,6)
        >>> f.domain() == range(1,5)
        True
        >>> F = BaseCNF()
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
        >>> F = BaseCNF()
        >>> f = BinaryMappingVariables(F,5,12)
        >>> f.range() == range(0,12)
        True
        >>> len(f)
        20
        >>> F = BaseCNF()
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
        >>> F = BaseCNF()
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
        >>> F = BaseCNF()
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
        >>> F = BaseCNF()
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


class VariablesManager:
    """Class for a formula with a variable manager

    A :py:class:`VariablesManager` allows to do that, while providing
    a nice interface that allows to focus on variable meaning.

    Attributes
    ----------
    name : dict
        associate a variable / literal to its label

    Methods
    -------
    new_variable(label=''):
        add a new variable

    new_block(*ranges,label=''):
        add variables with one or more indices

    Examples
    --------
    >>> F=BaseCNF()
    >>> V=VariablesManager(F)
    >>> X = V.new_variable(label="X")
    >>> Y = V.new_variable(label="Y")
    >>> Zs = V.new_block(2,3,label='z_{{{},{}}}')
    >>> F.number_of_variables()
    8
    >>> len(Zs)
    6
    >>> print(*V.all_variable_labels())
    X Y z_{1,1} z_{1,2} z_{1,3} z_{2,1} z_{2,2} z_{2,3}

    """


    def __init__(self,F):
        """Construct a variable manager object for formula F
        """
        self._groups = []
        self._formula = F

    def _add_variable_group(self, vg):
        """Add a group of variables to the formula"""
        if len(vg) == 0:
            # variable groups of length 0
            self._groups.append(vg)
            return

        begin, end = vg[0], vg[-1]
        assert end >= begin
        if begin <= self._formula.number_of_variables():
            raise ValueError(
                "The new variable group must not overlaps old variables")
        self._groups.append(vg)
        self._formula.update_variable_number(end)

    def new_variable(self, label=None):
        """
        Create a new variable

        Parameters
        ----------
        label : str, optional
            string representation of the variables

        Returns
        -------
        int, the new variable

        Examples
        --------
        >>> F=BaseCNF()
        >>> V=VariablesManager(F)
        >>> V.new_variable(label='X')
        1
        >>> F.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> V.new_variable(label='Z')
        3
        >>> F.number_of_variables()
        3
        >>> F.add_clause([1,3,-4])
        >>> F.number_of_variables()
        4
        """
        newgroup = SingletonVariableGroup(self._formula, label)
        self._add_variable_group(newgroup)
        return newgroup()

    def new_block(self, *ranges, label=None):
        """
        Create a new group of indexed variables

        Parameters
        ----------
        ranges : iterable(positive integer)
            the range of the variable indices

        label : str, optional
            string representation of the variables

        Returns
        -------
        BlockOfVariables, the new variable group

        Examples
        --------
        >>> F = BaseCNF()
        >>> V = VariablesManager(F)
        >>> V.new_variable(label='X')
        1
        >>> F.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> V.new_variable(label='Z')
        3
        >>> F.number_of_variables()
        3
        >>> v = V.new_block(3,5,4,3,label='v({},{},{},{})')
        >>> v.to_index(4)
        [1, 1, 1, 1]
        >>> v(1,1,1,1)
        4
        >>> v.to_index(8)
        [1, 1, 2, 2]
        >>> v(1,1,2,2)
        8
        >>> v.to_index(182)
        [3, 5, 4, 2]
        >>> v(3,5,4,2)
        182
        >>> v.to_index(183)
        [3, 5, 4, 3]
        >>> v(3,5,4,3)
        183
        """
        newgroup = BlockOfVariables(self._formula, ranges, label)
        self._add_variable_group(newgroup)
        return newgroup

    def new_combinations(self, n, k, label='p_{{{}}}'):
        """Create a new group of variables indexed by k-subsets of [n]"""

        newgroup = WordOfIndicesVariables(self._formula, n, k, labelfmt=label,
                                          wordtype='combinations')
        self._add_variable_group(newgroup)
        return newgroup

    def new_combinations_with_replacement(self, n, k, label='p_{{{}}}'):
        """Create a new group of variables indexed by k-subsets of [n]"""

        newgroup = WordOfIndicesVariables(self._formula, n, k, labelfmt=label,
                                          wordtype='combinations_with_replacement')
        self._add_variable_group(newgroup)
        return newgroup

    def new_permutations(self, n, k=None, label='p_{{{}}}'):
        """Create a new group of variables indexed by k-permutations of [n]"""

        if k is None:
            k = n
        newgroup = WordOfIndicesVariables(self._formula, n, k, labelfmt=label,
                                          wordtype='permutations')
        self._add_variable_group(newgroup)
        return newgroup

    def new_words(self, n, k, label='p_{{{}}}'):
        """Create a new group of variables indexed by sequences [n]^k"""

        newgroup = WordOfIndicesVariables(self._formula, n, k, labelfmt=label,
                                          wordtype='words')
        self._add_variable_group(newgroup)
        return newgroup

    def new_bipartite_edges(self, G, label='e({},{})'):
        """
        Create a new group variables from the edges of a bipartite graph

        Parameters
        ----------
        G : cnfgen.graphs.BaseBipartiteGraph
            a bipartite graph

        label : str, optional
            string representation of the variables

        Returns
        -------
        BipartiteEdgesVariables, the new variable group

        Examples
        --------
        >>> F = BaseCNF()
        >>> V=VariablesManager(F)
        >>> V.new_variable(label='X')
        1
        >>> F.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> G = BipartiteGraph(5,3)
        >>> G.add_edge(2,1)
        >>> G.add_edge(1,3)
        >>> G.add_edge(2,2)
        >>> G.add_edge(3,3)
        >>> G.add_edge(4,3)
        >>> G.add_edge(4,2)
        >>> G.add_edge(5,1)
        >>> e = V.new_bipartite_edges(G,label='X[{},{}]')
        >>> F.number_of_variables()
        9
        >>> e.to_index(4)
        (2, 1)
        >>> e(3,3)
        6
        >>> e.to_index(8)
        (4, 3)
        >>> e(5,1)
        9
        """
        newgroup = BipartiteEdgesVariables(self._formula, G, labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup

    def new_graph_edges(self, G, label='e({},{})'):
        """
        Create a new group variables from the edges of a bipartite graph

        Parameters
        ----------
        G : cnfgen.graphs.Graph
            a directed graph
        label : str, optional
            string representation of the variables

        Returns
        -------
        GraphEdgesVariables, the new variable group

        Examples
        --------
        >>> F = BaseCNF()
        >>> V=VariablesManager(F)
        >>> V.new_variable(label='X')
        1
        >>> F.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> G = Graph(6)
        >>> G.add_edge(2,1)
        >>> G.add_edge(1,3)
        >>> G.add_edge(2,6)
        >>> G.add_edge(2,3)
        >>> G.add_edge(4,3)
        >>> G.add_edge(4,2)
        >>> a = V.new_graph_edges(G)
        >>> V.new_variable(label='Y')
        9
        >>> print(*a())
        3 4 5 6 7 8
        >>> print(*a.indices())
        (1, 2) (1, 3) (2, 3) (2, 4) (2, 6) (3, 4)
        >>> a.to_index(4)
        (1, 3)
        >>> a(2,6)
        7
        >>> a.to_index(8)
        (3, 4)
        >>> a(2,1)
        3
        """
        G = Graph.normalize(G)
        newgroup = GraphEdgesVariables(self._formula,
                                         G,
                                         labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup

    def new_digraph_edges(self, G, label='e({},{})', sortby='pred'):
        """
        Create a new group variables from the edges of a bipartite graph

        Parameters
        ----------
        G : DirectedGraph
            a directed graph
        label : str, optional
            string representation of the variables
        sortby : 'pred' or 'succ'
            sort the edge veriables either by predecessor (default) or by successor

        Returns
        -------
        DiGraphEdgesVariables, the new variable group

        Examples
        --------
        >>> F=BaseCNF()
        >>> V=VariablesManager(F)
        >>> V.new_variable(label='X')
        1
        >>> F.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> G = DirectedGraph(6)
        >>> G.add_edge(2,1)
        >>> G.add_edge(1,3)
        >>> G.add_edge(2,6)
        >>> G.add_edge(2,3)
        >>> G.add_edge(4,3)
        >>> G.add_edge(4,2)
        >>> a = V.new_digraph_edges(G,sortby='succ')
        >>> V.new_variable(label='Y')
        9
        >>> print(*a())
        3 4 5 6 7 8
        >>> print(*a.indices())
        (2, 1) (4, 2) (1, 3) (2, 3) (4, 3) (2, 6)
        >>> a.to_index(4)
        (4, 2)
        >>> a(2,6)
        8
        >>> a.to_index(7)
        (4, 3)
        >>> a(2,1)
        3
        >>> F.number_of_variables()
        9
        """
        newgroup = DiGraphEdgesVariables(self._formula,
                                         G,
                                         labelfmt=label,
                                         sortby=sortby)
        self._add_variable_group(newgroup)
        return newgroup



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
        >>> F = BaseCNF()
        >>> V = VariablesManager(F)
        >>> f = V.new_mapping(4,10)
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
        newgroup = UnaryMappingVariables(self._formula, B, labelfmt=label)
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
        >>> F = BaseCNF()
        >>> V = VariablesManager(F)
        >>> f = V.new_sparse_mapping(B)
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
        newgroup = UnaryMappingVariables(self._formula, B, labelfmt=label)
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
        >>> F = BaseCNF()
        >>> V = VariablesManager(F)
        >>> f = V.new_binary_mapping(4,14)
        >>> F.number_of_variables()
        16
        >>> f(2,3)
        5
        >>> f(4,0)
        16
        """
        if n < 0 or m < 0:
            raise ValueError("n and m must be non negative integers")
        newgroup = BinaryMappingVariables(self._formula, n, m, labelfmt=label)
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

        (See py:classmethod:`VariablesManager.force_functional_mapping`)

        Examples
        --------
        >>> C = BaseCNF()
        >>> V = VariablesManager(C)
        >>> f = V.new_mapping(10,5)
        >>> V.force_complete_mapping(f)
        >>> C[2]
        [11, 12, 13, 14, 15]
        >>> len(C)
        10
        >>> g = V.new_binary_mapping(4,14)
        >>> V.force_complete_mapping(g)
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
        F = self._formula
        if f.parent_formula() != F:
            raise ValueError("mapping f was created from a different formula")

        if isinstance(f, BinaryMappingVariables):
            m = len(f.range())
            k = f.bits()
            for i in f.domain():
                for j in range(m, 2**k):
                    F.add_clause(f.forbid(i, j), check=False)

        if isinstance(f, UnaryMappingVariables):
            for x in f.domain():
                F.add_clause(f(x, None), check=False)

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
        >>> C = CNFLinear()
        >>> V = VariablesManager(C)
        >>> f = V.new_mapping(10,5)
        >>> V.force_functional_mapping(f)
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

        F = self._formula
        if f.parent_formula() != F:
            raise ValueError("mapping f was created from a different formula")

        if isinstance(f, BinaryMappingVariables):
            return
        if isinstance(f, UnaryMappingVariables):
            for x in f.domain():
                F.at_most(f(x, None), 1, check=False)

    def force_surjective_mapping(self, f):
        """Enforce the mapping `f` to be surjective

        Add the clauses that make the mapping `f` surjective.
        Namely that all elements in the range have at least one
        element in the domain mapped to it.

        This method works only for mapping represented in unary.

        Examples
        --------
        >>> C = BaseCNF()
        >>> V = VariablesManager(C)
        >>> f = V.new_mapping(10,5)
        >>> V.force_surjective_mapping(f)
        >>> C[1]
        [2, 7, 12, 17, 22, 27, 32, 37, 42, 47]
        >>> len(C)
        5
        """
        if not isinstance(f, UnaryMappingVariables):
            ValueError('f must be a UnaryMappingVariables')

        F = self._formula
        if f.parent_formula() != F:
            raise ValueError("mapping f was created from a different formula")

        for y in f.range():
            F.add_clause(f(None, y), check=False)

    def force_injective_mapping(self, f):
        """Enforce the mapping `f` to be injective

        Add the clauses that make the mapping `f` injective.
        Namely that all elements in the range have at most one element
        in the domain mapped to it.

        Examples
        --------
        >>> C = CNFLinear()
        >>> V = VariablesManager(C)
        >>> f = V.new_mapping(10,5)
        >>> V.force_injective_mapping(f)
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

        F = self._formula
        if f.parent_formula() != F:
            raise ValueError("mapping f was created from a different formula")

        if isinstance(f, UnaryMappingVariables):
            for y in f.range():
                F.at_most(f(None, y), 1, check=False)

        if isinstance(f, BinaryMappingVariables):
            for y in f.range():
                for x1, x2 in combinations(f.domain(), 2):
                    F.add_clause(f.forbid(x1, y) + f.forbid(x2, y), check=False)

    def force_nondecreasing_mapping(self, f):
        """Enforce the mapping `f` to be non decreasing

        Add the clauses that make the mapping `f` injective.
        Namely that all elements in the range have at most one element
        in the domain mapped to it.

        Examples
        --------
        >>> C = BaseCNF()
        >>> V = VariablesManager(C)
        >>> B = BipartiteGraph(2,3)
        >>> B.add_edge(1,2)
        >>> B.add_edge(1,3)
        >>> B.add_edge(2,1)
        >>> B.add_edge(2,3)
        >>> f = V.new_sparse_mapping(B)
        >>> V.force_nondecreasing_mapping(f)
        >>> len(C)
        2
        >>> C[0]
        [-1, -3]
        >>> C[1]
        [-2, -3]
        >>> g = V.new_binary_mapping(2,4)
        >>> V.force_nondecreasing_mapping(g)
        >>> len(C)
        8
        """
        if not isinstance(f,
                          (UnaryMappingVariables,BinaryMappingVariables)):
            ValueError('f must be either UnaryMappingVariables or BinaryMappingVariables')

        F = self._formula
        if f.parent_formula() != F:
            raise ValueError("mapping f was created from a different formula")

        if isinstance(f, UnaryMappingVariables):
            fd = f.to_dict()
            for (u1, u2) in combinations(f.domain(), 2):
                for (v1, v2) in product(f.range(u1), f.range(u2)):
                    if v1 > v2:
                        F.add_clause([-fd[(u1, v1)], -fd[(u2, v2)]], check=False)

        if isinstance(f, BinaryMappingVariables):
            for (u1, u2) in combinations(f.domain(), 2):
                for (v1, v2) in combinations(f.range(), 2):
                    F.add_clause(f.forbid(u1, v2) + f.forbid(u2, v1), check=False)


    def all_variable_labels(self, default_label_format='x{}'):
        """Produces the labels of all the variables

Variable belonging to special variable groups are translated
accordingly. The others get a standard variable name as defined by the
argument `default_label_format` (e.g. 'x{}').
        """
        # We cycle through all variables,
        #
        varid = 1
        end = self._formula.number_of_variables()
        for vg in self._groups:
            if len(vg) == 0:
                continue
            if isinstance(vg, SingletonVariableGroup):
                yield vg.name
                varid += 1
                continue
            begin = vg[0]
            while varid < begin:
                yield default_label_format.format(varid)
                varid += 1
            yield from vg.label()
            varid += len(vg)
        while varid <= end:
            yield default_label_format.format(varid)
            varid += 1
        assert varid == end+1
