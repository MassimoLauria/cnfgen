#!/usr/bin/env python
from datetime import datetime
from cnfgen.version import version

__all__ = ['info']

# Project info
info = {
    'project': 'CNFgen',
    'description': 'CNF formula generator',
    'author': 'Massimo Lauria',
    'author_email': 'massimo.lauria@uniroma1.it',
    'license': 'GPL-3',
    'version': "xxx",
    'url': 'https://massimolauria.net/cnfgen',
    'repository': 'https://github.com/MassimoLauria/cnfgen'
}

# Setup additional info
info['copyright'] = "(C) 2012-{0} {1} <{2}>".format(
    datetime.now().year,
    info['author'],
    info['author_email'])
info['version'] = version
