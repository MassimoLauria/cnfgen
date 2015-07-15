#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula families useful in proof complexity

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""


# Import formulas for library access
from .pigeonhole import PigeonholePrinciple,GraphPigeonholePrinciple
from .graphisomorphism import GraphIsomorphism, GraphAutomorphism
from .pebbling import PebblingFormula, StoneFormula
from .counting import PerfectMatchingPrinciple, CountingPrinciple
from .ordering import OrderingPrinciple,GraphOrderingPrinciple
from .tseitin  import TseitinFormula
from .subsetcardinality import SubsetCardinalityFormula
from .subgraph import SubgraphFormula,CliqueFormula,RamseyWitnessFormula
from .coloring import GraphColoringFormula,EvenColoringFormula
from .randomformulas import RandomKCNF
from .ramsey import RamseyLowerBoundFormula

__all__ = ["PigeonholePrinciple",
           "GraphPigeonholePrinciple",
           "PebblingFormula",
           "StoneFormula",
           "OrderingPrinciple",
           "GraphOrderingPrinciple",
           "GraphIsomorphism",
           "GraphAutomorphism",
           "RamseyLowerBoundFormula",
           "SubsetCardinalityFormula",
           "TseitinFormula",
           "PerfectMatchingPrinciple",
           "CountingPrinciple",
           "GraphColoringFormula",
           "EvenColoringFormula",
           "SubgraphFormula",
           "CliqueFormula",
           "RamseyWitnessFormula",
           "RandomKCNF"]
