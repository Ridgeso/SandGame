from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize


app = [
    Extension(
        "cver.cdraw", ['./cver/cdraw.pyx'],
        include_dirs=["./cver"],
        library_dirs=["./cver"]),
    Extension(
        "cver.cparticle", ['./cver/cparticle.pyx'],
        include_dirs=["./cver"],
        library_dirs=["./cver"]),
    Extension(
        "cver.tools", ['./cver/tools.pyx', './cver/vector.c'],
        include_dirs=["./cver"],
        library_dirs=["./cver"])
]

setup(
    name="SandGameInCython",
    packages=find_packages(),
    ext_modules=cythonize(app),
    options={
        "build": {
            "build_lib": "."
        }
    },
)
