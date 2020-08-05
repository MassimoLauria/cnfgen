#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Init code of the cnfformula pacakge

Essentially it makes visible the names of the formulas and
transformations implemented, plus some IO functions.

"""

# Basic CNF object
from cnfformula.cnf import CNF

# IO functions
from cnfformula.utils.parsedimacs import readCNF
from cnfformula.graphs import readGraph, writeGraph
from cnfformula.graphs import supported_formats as supported_graph_formats

# SAT solvers
from cnfformula.utils.solver import supported_satsolvers
from cnfformula.utils.solver import some_solver_installed

# Formula families implemented
from cnfformula.families.cliquecoloring import CliqueColoring
from cnfformula.families.coloring import GraphColoringFormula
from cnfformula.families.coloring import EvenColoringFormula
from cnfformula.families.counting import CountingPrinciple
from cnfformula.families.counting import PerfectMatchingPrinciple
from cnfformula.families.dominatingset import DominatingSet
from cnfformula.families.graphisomorphism import GraphIsomorphism
from cnfformula.families.graphisomorphism import GraphAutomorphism
from cnfformula.families.ordering import OrderingPrinciple
from cnfformula.families.ordering import GraphOrderingPrinciple
from cnfformula.families.pebbling import PebblingFormula
from cnfformula.families.pebbling import StoneFormula
from cnfformula.families.pebbling import SparseStoneFormula
from cnfformula.families.pigeonhole import PigeonholePrinciple
from cnfformula.families.pigeonhole import GraphPigeonholePrinciple
from cnfformula.families.pigeonhole import BinaryPigeonholePrinciple
from cnfformula.families.ramsey import PythagoreanTriples
from cnfformula.families.ramsey import RamseyLowerBoundFormula
from cnfformula.families.randomformulas import RandomKCNF
from cnfformula.families.subgraph import SubgraphFormula
from cnfformula.families.subgraph import CliqueFormula
from cnfformula.families.subgraph import BinaryCliqueFormula
from cnfformula.families.subgraph import RamseyWitnessFormula
from cnfformula.families.subsetcardinality import SubsetCardinalityFormula
from cnfformula.families.tseitin import TseitinFormula
from cnfformula.families.pitfall import PitfallFormula
from cnfformula.families.cpls import CPLSFormula

# Formula transformation implemented
from cnfformula.transformations.substitutions import AllEqualSubstitution
from cnfformula.transformations.substitutions import ExactlyOneSubstitution
from cnfformula.transformations.substitutions import FlipPolarity
from cnfformula.transformations.substitutions import FormulaLifting
from cnfformula.transformations.substitutions import IfThenElseSubstitution
from cnfformula.transformations.substitutions import MajoritySubstitution
from cnfformula.transformations.substitutions import NotAllEqualSubstitution
from cnfformula.transformations.substitutions import OrSubstitution
from cnfformula.transformations.substitutions import VariableCompression
from cnfformula.transformations.substitutions import XorSubstitution
from cnfformula.transformations.shuffle import Shuffle
