from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

setup(
    name='monotonic_align',
    ext_modules=cythonize([Extension("core", ["plugins/vitsTTS/vits/monotonic_align/core.pyx"], include_dirs=[numpy.get_include()])]),
)

# setup(
#   name = 'monotonic_align',
#   ext_modules = cythonize("plugins/vitsTTS/vits/monotonic_align/core.pyx"),
#   include_dirs=[numpy.get_include()]
# )
