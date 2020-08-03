#!/usr/bin/env python

try:
    import cnfformula.version
    __version__ = cnfformula.version.__version__
except ImportError:
    pass

__project_name__ = 'CNFgen'
__project_description__ = 'CNF formula generator'

__author__ = 'Massimo Lauria'
__author_email__ = 'massimo.lauria@uniroma1.it'
__aurhor_string__ = __author__ + ' <' + __author_email__ + '>'

__copyright__ = '2012-2020 ' + __author__ + ' <' + __author_email__ + '>'
__license__ = 'GPL-3'
__url__ = 'https://massimolauria.net/cnfgen'
__repo_url__ = 'https://github.com/MassimoLauria/cnfgen'
