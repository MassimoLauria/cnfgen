# Test for the threshold substitutions

# At most K
# At least K
# Exactly K
# Anything but K

import pytest

from cnfgen import CNF
from cnfgen import ExactlyKSubstitution
from cnfgen import AnythingButKSubstitution
from cnfgen import AtMostKSubstitution
from cnfgen import AtLeastKSubstitution
from cnfgen.clitools import cnfgen, CLIError


def test_exactk_check_args():
    # Negative N
    with pytest.raises(ValueError):
        F = CNF([[(True, 'x')], [(False, 'y')]])
        F = ExactlyKSubstitution(F, -1, 1)


def test_cli_exactk_check_args():
    # Negative N
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '-q', 'and', 1, 1, '-T', 'exact', -1, 1],
               mode='string')


def test_anybutk_check_args():
    # Negative N
    with pytest.raises(ValueError):
        F = CNF([[(True, 'x')], [(False, 'y')]])
        F = AnythingButKSubstitution(F, -1, 1)


def test_cli_anybutk_check_args():
    # Negative N
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '-q', 'and', 1, 1, '-T', 'anybut', -1, 1],
               mode='string')


def test_atmostk_check_args():
    # Negative N
    with pytest.raises(ValueError):
        F = CNF([[(True, 'x')], [(False, 'y')]])
        F = AtMostKSubstitution(F, -1, 1)


def test_cli_atmostk_check_args():
    # Negative N
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '-q', 'and', 1, 1, '-T', 'atmost', -1, 1],
               mode='string')


def test_atleastk_check_args():
    # Negative N
    with pytest.raises(ValueError):
        F = CNF([[(True, 'x')], [(False, 'y')]])
        F = AtLeastKSubstitution(F, -1, 1)


def test_cli_atleastk_check_args():
    # Negative N
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', '-q', 'and', 1, 1, '-T', 'atleast', -1, 1],
               mode='string')
