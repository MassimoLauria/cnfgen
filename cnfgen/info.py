#!/usr/bin/env python
copyright_years = '(C) 2012-2020'

__all__ = ['info']


def get_version():
    """Compute CNFgen verison number

Version number is obtained from the GIT repository, either
hardcoding that number into version.py file (for release) or
directly calling GIT (for development).
"""
    try:
        from cnfgen.version import version
        return version
    except ImportError:
        pass

    try:
        import subprocess
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--always"]).strip().decode('utf-8')
        return version
    except subprocess.CalledProcessError:
        pass


# Project info
info = {
    'project': 'CNFgen',
    'description': 'CNF formula generator',
    'author': 'Massimo Lauria',
    'author_email': 'massimo.lauria@uniroma1.it',
    'version': 'unknown version',
    'license': 'GPL-3',
    'url': 'https://massimolauria.net/cnfgen',
    'repository': 'https://github.com/MassimoLauria/cnfgen'
}

# Setup additional info
info['copyright'] = "{0} {1} <{2}>".format(copyright_years, info['author'],
                                           info['author_email'])
info['version'] = get_version()
