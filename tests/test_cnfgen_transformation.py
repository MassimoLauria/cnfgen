#!/usr/bin/env python

import sys
import pytest

from cnfgen.clitools import cnfgen
from cnfgen.clitools import get_transformation_helpers, CLIError


def test_invalid_transformation_help():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', 'and', '0', '0', '-T', 'spam', '-h'])



def test_no_trasformation():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', 'and', '0', '0', '-T'])


def test_no_transformation_help():
    with pytest.raises(SystemExit) as cm:
        cnfgen(['cnfgen', 'and', '0', '0', '-T', '-h'])
    assert cm.value.code == 0

def test_transformation_help():
    transformations = get_transformation_helpers()
    for t in transformations:
        with pytest.raises(SystemExit) as cm:
            cnfgen(["cnfgen", 'and', '0', '0', t.name, "-h"])
        assert cm.value.code == 0
