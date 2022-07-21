# from distutils.core import setup, Extension
# from Cython.Build import cythonize
# import numpy
#
# setup(
#     ext_modules=cythonize([
#         Extension("cparticle", ["cparticle.pyx"]),
#         Extension("cdraw", ["cdraw.pyx"])
#     ], language="c++"),
#     include_dirs=[numpy.get_include(), "map"]
# )
from setuptools import setup, find_packages
from Cython.Build import cythonize
import numpy

setup(
    packages=find_packages(),
    ext_modules=cythonize(['cver/cparticle.pyx', 'cver/cdraw.pyx']),
    include_dirs=[numpy.get_include()],
    options={
        "build": {
            "build_lib": "cver"
        }
    },
)
