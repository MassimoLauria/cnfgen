from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = "Cnf Generator",
    ext_modules = cythonize('reshuffle.pyx'), # accepts a glob pattern
)
