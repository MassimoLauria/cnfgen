#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Keep tracks of the variable of a formula.

The module defines a variable manager, that formulas could either use
of specialize. It allows to generates
- single variables
- variables for some tuples of indices
- variables for the edges of a bipartite/direct/simple graph

The module implements the :py:class:`VariablesManager` object, which
is supposed to be inherited from the :py:class:`CNF` object.

Copyright (C) 2019-2021  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from itertools import product,combinations, combinations_with_replacement
from bisect import bisect_right

from cnfgen.graphs import BaseBipartiteGraph, BipartiteGraph, CompleteBipartiteGraph
import networkx as nx

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
        >>> V = VariablesManager()
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

    def __len__(self):
        """The number of variables in the group"""
        return len(self.ids)

    def variable_ids(self):
        """The ID interval for this variable group"""
        return self.ids

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
        return self.variable_ids()[0]

    def label(self):
        return self.name

    def indices(self, *pattern):
        """Outputs all the indices matching the given pattern"""
        if len(pattern) > 0:
            raise ValueError("Singleton variable groups have a 0-arity index")
        return [()]

    def to_index(self, lit):
        """Convert a literal of the corresponding variable index"""
        if abs(lit) != self.variable_ids()[0]:
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
    >>> F = VariablesManager()
    >>> G = BlockOfVariables(F,[2,3],'G[{},{}]')
    >>> print(*G.label())
    G[1,1] G[1,2] G[1,3] G[2,1] G[2,2] G[2,3]
    >>> print(*G.indices())
    (1, 1) (1, 2) (1, 3) (2, 1) (2, 2) (2, 3)
    >>> G(2,1)
    4
    >>> V = VariablesManager()
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
            raise ValueError(
                'The index domain must have at least dimension one')

        if len([x for x in ranges if x < 1]):
            raise ValueError('Indices range must be all positive')

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
        >>> V = VariablesManager()
        >>> VG = BlockOfVariables(V,[3,5,4,3])
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

class CombinationVariables(BaseVariableGroup):
    """Group of variables corrisponding to sets (or multisets) of indices

    This objects represents groups of variables that are indexed by
    some sets of integers from a ground set :math:`[n]`. For example we
    can have variables :math:`p_{S}` for :math:`S in
    \\binom{[n]}{k}[10]` for a fixed :math:`k`.

    Each set is identified by an index, which is just the sequence of
    it's elements, sorted.

    Examples
    --------
    >>> F = VariablesManager()
    >>> G = CombinationVariables(F,4,2,'[{}]')
    >>> print(*G.label())
    [1,2] [1,3] [1,4] [2,3] [2,4] [3,4]
    >>> print(*G.indices())
    (1, 2) (1, 3) (1, 4) (2, 3) (2, 4) (3, 4)
    >>> G(2,3)
    4
    >>> V = VariablesManager()
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
    >>> print(q(1,1))
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

    def __init__(self, formula, n, k, labelfmt=None, replacement=False):
        """Creates a variables group object

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        ranges: list(integer)
            ranges of the indices
        labelfmt: str
            format string for the variable labels
        replacements: bool
            include combinations with replacement
        """
        if labelfmt is None:
            labelfmt = 'p_{{{}}}'
        # Check if the format strings can get all parameters
        try:
            labelfmt.format(2)
        except IndexError:
            raise ValueError(
                'label must be a valid format string one index')

        if n<0 or k<0 or n<k:
            raise ValueError(
                'It must be that 0<= k <= n')

        self.n = n
        self.k = k
        self.replacement = replacement
        self.offset = formula.number_of_variables()
        self.vid2seq=[]
        self.seq2vid={}
        if not self.replacement:
            gen = combinations(range(1,n+1),k)
        else:
            gen = combinations_with_replacement(range(1,n+1),k)

        vid = self.offset
        for c in gen:
            vid += 1
            self.vid2seq.append(c)
            self.seq2vid[c] = vid

        BaseVariableGroup.__init__(self, formula, len(self.vid2seq), labelfmt)

    def label(self,*pattern):
        isProjection = len(pattern) == 0 or None in pattern
        assert pattern in self.seq2vid

        labels = (self.labelfmt.format(','.join(str(x) for x in t)) for t in self.indices(*pattern))

        if isProjection:
            return (self.labelfmt.format(*t) for t in self.indices(*pattern))
        else:
            return next(labels)

    def indices(self,*pattern):
        """Implementation of :py:classmethod:`BaseVariableGroup.indices`

        Returns
        -------
        all the variable indices
        """
        if pattern in self.seq2vid:
            return [pattern]
        return iter(self.vid2seq)

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
        >>> V = VariablesManager()
        >>> VG = BlockOfVariables(V,[3,5,4,3])
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
    >>> F = VariablesManager()
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
        >>> F = VariablesManager()
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
        >>> F = VariablesManager()
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
    >>> G = nx.DiGraph()
    >>> G.add_nodes_from(range(1,6))
    >>> G.add_edge(1,2)
    >>> G.add_edge(2,3)
    >>> G.add_edge(3,4)
    >>> G.add_edge(4,5)
    >>> G.add_edge(5,1)
    >>> F = VariablesManager()
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
    >>> H = nx.DiGraph()
    >>> H.add_nodes_from(range(1,6))
    >>> H.add_edge(1,2)
    >>> H.add_edge(1,3)
    >>> H.add_edge(2,3)
    >>> H.add_edge(2,4)
    >>> H.add_edge(5,1)
    >>> F = VariablesManager()
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

    def __init__(self, formula, G, labelfmt='e_{{{},{}}}', sortby='pred'):
        """Creates a variables group object

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        G: networkx.DiGraph
            directed graph
        labelfmt: str
            format string for the variable labels
        sortby: 'pred' or 'succ'
            sort edges by either predecessors or successors (default: predecessors)
        """
        if not isinstance(G, nx.DiGraph):
            raise TypeError(
                "Invalid direct graph G: a networkx.DiGraph object was expected"
            )

        if sortby not in ['pred', 'succ']:
            raise ValueError("'indexby' must be one among 'pred', 'succ'")

        # Check if the format strings can get all parameters
        try:
            labelfmt.format(1, 1)
        except IndexError:
            raise ValueError(
                'label must be a valid format string for two arguments')

        V = G.number_of_nodes()
        B = BipartiteGraph(V, V)

        for u, v in G.edges():
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
        >>> H = nx.DiGraph()
        >>> H.add_edge(1,2)
        >>> H.add_edge(1,3)
        >>> H.add_edge(2,3)
        >>> H.add_edge(2,4)
        >>> H.add_edge(5,1)
        >>> F = VariablesManager()
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
    the class :py:class:`networkx.Graph`, we have variables
    :math:`e_{u,v}` for :math:`\{u,v\} in E`.

    Warning: if the object representing :math:`G` gets modified, the
    behavior of this object may be inconsistent.

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_nodes_from(range(1,5))
    >>> G.add_edge(2,1)
    >>> G.add_edge(3,2)
    >>> G.add_edge(1,3)
    >>> G.add_edge(2,2)
    >>> G.add_edge(4,2)
    >>> F = VariablesManager()
    >>> V = GraphEdgesVariables(F, G, labelfmt='E[{},{}]')
    >>> print(*[V.label(u,v) for u,v in V.indices()])
    E[1,2] E[1,3] E[2,2] E[2,3] E[2,4]
    >>> print(V(2,1))
    1
    >>> print(V(1,3))
    2
    >>> 4 in V
    True
    >>> 10 in V
    False
    >>> print(len(V))
    5
    >>> print(V.label(3,1))
    E[1,3]
    >>> print(*V.label(2,None))
    E[1,2] E[2,2] E[2,3] E[2,4]
    >>> print(*V.label(None,2))
    E[1,2] E[2,2] E[2,3] E[2,4]
    >>> print(*V.label())
    E[1,2] E[1,3] E[2,2] E[2,3] E[2,4]
    >>> print(*V.indices(None,2))
    (1, 2) (2, 2) (2, 3) (2, 4)
    """

    def __init__(self, formula, G, labelfmt='e_{{{}{}}}'):
        """Creates a variables group for the edges of G

        Parameters
        ----------
        formula: CNF
            formula to which we add a variable group
        G: BipartiteGraph
            bipartite graph
        labelfmt: str
            format string for the variable labels
        """
        if not isinstance(G, nx.Graph):
            raise TypeError(
                "Invalid bipartite graph G: a networkx.Graph object was expected"
            )

        V = G.number_of_nodes()
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
        >>> G = BipartiteGraph(2,3)
        >>> G.add_edge(2,1)
        >>> G.add_edge(1,3)
        >>> G.add_edge(2,2)
        >>> F = VariablesManager()
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
            return self.BG.indices()

        u = pattern[0]
        v = pattern[1]
        if u is not None and v is not None:
            iu, iv = min(u, v), max(u, v)
            return self.BG.indices(iu, iv)

        # Only one vertex is set. Fix w to it
        if u is not None:
            w = u
        else:
            w = v

        # Enumerates all neighbors of w
        def _gen():
            yield from ((u, w) for u, w in self.BG.indices(None, w))
            yield from ((w, u) for w, u in self.BG.indices(w, None) if u != w)

        return _gen()

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
        >>> G = nx.Graph()
        >>> G.add_nodes_from(range(1,5))
        >>> G.add_edge(2,1)
        >>> G.add_edge(3,2)
        >>> G.add_edge(1,3)
        >>> G.add_edge(2,2)
        >>> G.add_edge(4,2)
        >>> F = VariablesManager()
        >>> F.update_variable_number(100)
        >>> V = GraphEdgesVariables(F, G)
        >>> V.to_index(102)
        (1, 3)
        >>> V.to_index(101)
        (1, 2)
        >>> V.to_index(105)
        (2, 4)
        """
        return self.BG.to_index(lit)


class VariablesManager(CNFLinear):
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
    new_variable(label=''):
        add a new variable

    new_block(*ranges,label=''):
        add variables with one or more indices

    Examples
    --------
    >>> V=VariablesManager()
    >>> X = V.new_variable(label="X")
    >>> Y = V.new_variable(label="Y")
    >>> Zs = V.new_block(2,3,label='z_{{{},{}}}')
    >>> V.number_of_variables()
    8
    >>> len(Zs)
    6
    >>> print(*V.all_variable_labels())
    X Y z_{1,1} z_{1,2} z_{1,3} z_{2,1} z_{2,2} z_{2,3}

    """

    def __init__(self, clauses=None, description=None):
        """Construct a variable manager object
        """
        self._groups = []
        CNFLinear.__init__(self, clauses=clauses, description=description)

    def _add_variable_group(self, vg):
        """Add a group of variables to the formula"""
        ids = vg.variable_ids()
        if len(ids) == 0:
            # variable groups of length 0
            self._groups.append(vg)
            return

        begin, end = ids[0], ids[-1]
        assert end >= begin
        if begin <= self.number_of_clauses():
            raise ValueError(
                "The new variable group must not overlaps old variables")
        self._groups.append(vg)
        self.update_variable_number(end)

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
        >>> V=VariablesManager()
        >>> V.new_variable(label='X')
        1
        >>> V.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> V.new_variable(label='Z')
        3
        >>> V.number_of_variables()
        3
        >>> V.add_clause([1,3,-4])
        >>> V.number_of_variables()
        4
        """
        newgroup = SingletonVariableGroup(self, label)
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
        >>> V=VariablesManager()
        >>> V.new_variable(label='X')
        1
        >>> V.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> V.new_variable(label='Z')
        3
        >>> V.number_of_variables()
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
        newgroup = BlockOfVariables(self, ranges, label)
        self._add_variable_group(newgroup)
        return newgroup

    def new_combinations(self, n, k, label='p_{{{}}}'):
        """Create a new group of variables indexed by k-subsets of [n]"""

        newgroup = CombinationVariables(self, n, k, labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup

    def new_combinations_with_replacement(self, n, k, label='p_{{{}}}'):
        """Create a new group of variables indexed by k-subsets of [n]"""

        newgroup = CombinationVariables(self, n, k, labelfmt=label, replacement=True)
        self._add_variable_group(newgroup)
        return newgroup

    def new_bipartite_edges(self, G, label='e({},{})'):
        """
        Create a new group variables from the edges of a bipartite graph

        Parameters
        ----------
        G : BaseBipartiteGraph
            a bipartite graph

        label : str, optional
            string representation of the variables

        Returns
        -------
        BipartiteEdgesVariables, the new variable group

        Examples
        --------
        >>> V=VariablesManager()
        >>> V.new_variable(label='X')
        1
        >>> V.number_of_variables()
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
        >>> V.number_of_variables()
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
        newgroup = BipartiteEdgesVariables(self, G, labelfmt=label)
        self._add_variable_group(newgroup)
        return newgroup


    def new_digraph_edges(self, G, label='e({},{})', sortby='pred'):
        """
        Create a new group variables from the edges of a bipartite graph

        Parameters
        ----------
        G : networkx.DiGraph
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
        >>> V=VariablesManager()
        >>> V.new_variable(label='X')
        1
        >>> V.number_of_variables()
        1
        >>> V.new_variable(label='Y')
        2
        >>> G = nx.DiGraph()
        >>> G.add_nodes_from(range(1,7))
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
        """
        newgroup = DiGraphEdgesVariables(self,
                                         G,
                                         labelfmt=label,
                                         sortby=sortby)
        self._add_variable_group(newgroup)
        return newgroup

    def all_variable_labels(self, default_label_format='x{}'):
        """Produces the labels of all the variables

Variable belonging to special variable groups are translated
accordingly. The others get a standard variable name as defined by the
argument `default_label_format` (e.g. 'x{}').
        """
        # We cycle through all variables,
        #
        varid = 1
        for vg in self._groups:
            if len(vg.variable_ids()) == 0:
                continue
            begin = vg.variable_ids()[0]
            while varid < begin:
                yield default_label_format.format(varid)
                varid += 1
            yield from vg.label()
            varid += len(vg)
        while varid <= self._numvar:
            yield default_label_format.format(varid)
            varid += 1
        assert varid == self._numvar+1
