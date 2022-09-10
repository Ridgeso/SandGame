from setuptools import setup, find_packages
from Cython.Build import cythonize
import numpy

setup(
    packages=find_packages(),
    ext_modules=cythonize(['cver/cparticle.pyx', 'cver/cdraw.pyx', 'cver/vector.pyx']),
    include_dirs=[numpy.get_include()],
    options={
        "build": {
            "build_lib": "cver"
        }
    },
)
