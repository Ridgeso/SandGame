from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy
from os import path

vector_path = path.join('cver', 'vector.c')

app = [
    Extension(
        "cver.cdraw", [path.join('cver', 'cdraw.pyx'), vector_path],
        libraries=["pthread"]
    ),
    Extension(
        "cver.cparticle", [path.join('cver', 'cparticle.pyx'), vector_path],
        libraries=["pthread"]
    ),
    Extension(
        "cver.tools", [path.join('cver', 'tools.pyx'), vector_path],
        libraries=["pthread"]
    )
]

setup(
    name="SandGameInCython",
    packages=find_packages(),
    # ext_modules=cythonize(app),
    # TODO: Make it work for language_level=3
    ext_modules=cythonize(app, compiler_directives={'language_level' : "3"}),
    include_dirs=[numpy.get_include()],
    options={
        "build": {
            "build_lib": "."
        }
    },
    cmdclass={
        'build_ext': build_ext
    }
)
