#!/usr/bin/env python

from .cnf import CNF
from .graphs import readGraph,writeGraph
from .cnfgen import command_line_utility as cnfgen


# Formula families implemented
from .families.cliquecoloring       import CliqueColoring
from .families.coloring             import GraphColoringFormula
from .families.coloring             import EvenColoringFormula
from .families.counting             import CountingPrinciple
from .families.counting             import PerfectMatchingPrinciple
from .families.dominatingset        import DominatingSet
from .families.graphisomorphism     import GraphIsomorphism
from .families.graphisomorphism     import GraphAutomorphism
from .families.ordering             import OrderingPrinciple
from .families.ordering             import GraphOrderingPrinciple
from .families.pebbling             import PebblingFormula
from .families.pebbling             import StoneFormula
from .families.pebbling             import SparseStoneFormula
from .families.pigeonhole           import PigeonholePrinciple
from .families.pigeonhole           import GraphPigeonholePrinciple
from .families.pigeonhole           import BinaryPigeonholePrinciple
from .families.ramsey               import PythagoreanTriples
from .families.ramsey               import RamseyLowerBoundFormula
from .families.randomformulas       import RandomKCNF
from .families.subgraph             import SubgraphFormula
from .families.subgraph             import CliqueFormula
from .families.subgraph             import BinaryCliqueFormula
from .families.subgraph             import RamseyWitnessFormula
from .families.subsetcardinality    import SubsetCardinalityFormula
from .families.tseitin              import TseitinFormula



def _load_formula_transformations():
    """Load CNF transformations from `cnfformula.transformations`.

    This code explores the submodules of `cnfformula.transformations` and
    load the formula transformations, or at least the objects marked as
    such with the `cnfformula.transformations.register_cnf_transformation`
    function decorator.
    """
    
    import sys
    from . import transformations
    from .cmdline import find_methods_in_package
    from .transformations import is_cnf_transformation

    loot = dict( (g.__name__, g)
                 for g in find_methods_in_package(transformations,is_cnf_transformation))
    

    # Load the formula object into the namespace
    self_ref = sys.modules[__name__]
    self_ref.__dict__.update(loot)
    __all__.extend(name for name in loot.keys() if name not in __all__)


