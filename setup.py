from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy


app = [
    Extension(
        "cver.cdraw", ['./cver/cdraw.pyx', './cver/vector.c'],
        include_dirs=["./cver"],
        library_dirs=["./cver"],
        libraries=["pthread"],),
    Extension(
        "cver.cparticle", ['./cver/cparticle.pyx', './cver/vector.c'],
        include_dirs=["./cver"],
        library_dirs=["./cver"],),
    Extension(
        "cver.tools", ['./cver/tools.pyx', './cver/vector.c'],
        include_dirs=["./cver"],
        library_dirs=["./cver"],)
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
