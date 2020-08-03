#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Command line tools based on cnfformula package

- main cnfgen implementation
- kthlist2pebbling
- cnfshuffle
- cnftransform
"""

from .kthlist2pebbling import cli as kthlist2pebbling
from .cnfshuffle import cli as cnfshuffle
from .main import cli as cnfgen

from .cmdline import CLIError
