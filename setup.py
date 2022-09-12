from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy

vector = Extension(
    name="vector",
    sources=['cver/vector.c']
)

tools = Extension(
    name="tools",
    sources=['cver/tools.pyx', 'cver/vector.c']
)

particle = Extension(
    name="particle",
    sources=['cver/cparticle.pyx', 'cver/vector.c']
)

draw = Extension(
    name="draw",
    sources=['cver/cdraw.pyx']
)

setup(
    packages=find_packages(),
    # ext_modules=cythonize(['cver/cparticle.pyx', 'cver/cdraw.pyx', 'cver/vector.c']),
    ext_modules=cythonize([draw, particle, tools, vector]),
    # ext_modules=cythonize([draw]),
    include_dirs=[numpy.get_include()],
    options={
        "build": {
            "build_lib": "cver"
        }
    },
)
