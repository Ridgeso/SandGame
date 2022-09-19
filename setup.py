from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy


app = [
    Extension(
        "cver.cdraw", ['./cver/cdraw.pyx', './cver/vector.c'],
        include_dirs=["./cver"],
        library_dirs=["./cver"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp']),
    Extension(
        "cver.cparticle", ['./cver/cparticle.pyx', './cver/vector.c'],
        include_dirs=["./cver"],
        library_dirs=["./cver"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp']),
    Extension(
        "cver.tools", ['./cver/tools.pyx', './cver/vector.c'],
        include_dirs=["./cver"],
        library_dirs=["./cver"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'])
]

setup(
    name="SandGameInCython",
    packages=find_packages(),
    ext_modules=cythonize(app),
    include_dirs=[numpy.get_include()],
    options={
        "build": {
            "build_lib": "."
        }
    },
)
