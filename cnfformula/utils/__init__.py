#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Various utilities for the manipulation of the CNFs.
"""

from .parsedimacs import dimacs2cnf

from .solver import supported_satsolvers
from .solver import have_satsolver
from .solver import is_satisfiable

from .kthlist2pebbling import command_line_utility as kthlist2pebbling
from .cnfshuffle       import command_line_utility as cnfshuffle
from .dimacstransform  import command_line_utility as dimacstransform

