#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Init code of the cnfgen pacakge

Essentially it makes visible the names of the formulas and
transformations implemented, plus some IO functions.

"""

# Basic CNF object
from cnfgen.cnf import CNF

# IO functions
from cnfgen.utils.parsedimacs import readCNF
from cnfgen.graphs import readGraph, writeGraph
from cnfgen.graphs import supported_formats as supported_graph_formats

# SAT solvers
from cnfgen.utils.solver import supported_satsolvers
from cnfgen.utils.solver import some_solver_installed

# Formula families implemented
from cnfgen.families.cliquecoloring import CliqueColoring
from cnfgen.families.coloring import GraphColoringFormula
from cnfgen.families.coloring import EvenColoringFormula
from cnfgen.families.counting import CountingPrinciple
from cnfgen.families.counting import PerfectMatchingPrinciple
from cnfgen.families.dominatingset import DominatingSet
from cnfgen.families.dominatingset import Tiling
from cnfgen.families.graphisomorphism import GraphIsomorphism
from cnfgen.families.graphisomorphism import GraphAutomorphism
from cnfgen.families.ordering import OrderingPrinciple
from cnfgen.families.ordering import GraphOrderingPrinciple
from cnfgen.families.pebbling import PebblingFormula
from cnfgen.families.pebbling import StoneFormula
from cnfgen.families.pebbling import SparseStoneFormula
from cnfgen.families.pigeonhole import PigeonholePrinciple
from cnfgen.families.pigeonhole import GraphPigeonholePrinciple
from cnfgen.families.pigeonhole import BinaryPigeonholePrinciple
from cnfgen.families.pigeonhole import RelativizedPigeonholePrinciple
from cnfgen.families.ramsey import PythagoreanTriples
from cnfgen.families.ramsey import RamseyLowerBoundFormula
from cnfgen.families.randomformulas import RandomKCNF
from cnfgen.families.subgraph import SubgraphFormula
from cnfgen.families.subgraph import CliqueFormula
from cnfgen.families.subgraph import BinaryCliqueFormula
from cnfgen.families.subgraph import RamseyWitnessFormula
from cnfgen.families.subsetcardinality import SubsetCardinalityFormula
from cnfgen.families.tseitin import TseitinFormula
from cnfgen.families.pitfall import PitfallFormula
from cnfgen.families.cpls import CPLSFormula

# Formula transformation implemented
from cnfgen.transformations.substitutions import AllEqualSubstitution
from cnfgen.transformations.substitutions import ExactlyOneSubstitution
from cnfgen.transformations.substitutions import ExactlyKSubstitution
from cnfgen.transformations.substitutions import AnythingButKSubstitution
from cnfgen.transformations.substitutions import AtLeastKSubstitution
from cnfgen.transformations.substitutions import AtMostKSubstitution
from cnfgen.transformations.substitutions import FlipPolarity
from cnfgen.transformations.substitutions import FormulaLifting
from cnfgen.transformations.substitutions import IfThenElseSubstitution
from cnfgen.transformations.substitutions import MajoritySubstitution
from cnfgen.transformations.substitutions import NotAllEqualSubstitution
from cnfgen.transformations.substitutions import OrSubstitution
from cnfgen.transformations.substitutions import VariableCompression
from cnfgen.transformations.substitutions import XorSubstitution
from cnfgen.transformations.shuffle import Shuffle

# Main Command Line tool
from cnfgen.clitools import cnfgen
