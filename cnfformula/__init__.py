#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Init code of the cnfformula pacakge

Essentially it makes visible the names of the formulas and
transformations implemented, plus some IO functions.

"""

# Basic CNF object
from .cnf import CNF

# IO functions
from .utils.parsedimacs import readCNF
from .graphs import readGraph, writeGraph
from .graphs import supported_formats as supported_graph_formats

# SAT solvers
from .utils.solver import supported_satsolvers
from .utils.solver import some_solver_installed

# Formula families implemented
from .families.cliquecoloring import CliqueColoring
from .families.coloring import GraphColoringFormula
from .families.coloring import EvenColoringFormula
from .families.counting import CountingPrinciple
from .families.counting import PerfectMatchingPrinciple
from .families.dominatingset import DominatingSet
from .families.graphisomorphism import GraphIsomorphism
from .families.graphisomorphism import GraphAutomorphism
from .families.ordering import OrderingPrinciple
from .families.ordering import GraphOrderingPrinciple
from .families.pebbling import PebblingFormula
from .families.pebbling import StoneFormula
from .families.pebbling import SparseStoneFormula
from .families.pigeonhole import PigeonholePrinciple
from .families.pigeonhole import GraphPigeonholePrinciple
from .families.pigeonhole import BinaryPigeonholePrinciple
from .families.ramsey import PythagoreanTriples
from .families.ramsey import RamseyLowerBoundFormula
from .families.randomformulas import RandomKCNF
from .families.subgraph import SubgraphFormula
from .families.subgraph import CliqueFormula
from .families.subgraph import BinaryCliqueFormula
from .families.subgraph import RamseyWitnessFormula
from .families.subsetcardinality import SubsetCardinalityFormula
from .families.tseitin import TseitinFormula
from .families.pitfall import PitfallFormula
from .families.cpls import CPLSFormula

# Formula transformation implemented
from .transformations.substitutions import AllEqualSubstitution
from .transformations.substitutions import ExactlyOneSubstitution
from .transformations.substitutions import FlipPolarity
from .transformations.substitutions import FormulaLifting
from .transformations.substitutions import IfThenElseSubstitution
from .transformations.substitutions import MajoritySubstitution
from .transformations.substitutions import NotAllEqualSubstitution
from .transformations.substitutions import OrSubstitution
from .transformations.substitutions import VariableCompression
from .transformations.substitutions import XorSubstitution
from .transformations.shuffle import Shuffle
