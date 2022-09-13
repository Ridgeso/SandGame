from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy
 
 
app = [
    Extension(
        "cdraw", ['./cdraw.pyx', './vector.c'],
        include_dirs=["."],
        library_dirs=["."]),
    Extension(
        "cparticle", ['./cparticle.pyx', './vector.c'],
        include_dirs=["."],
        library_dirs=["."]),
    Extension(
        "tools", ['./tools.pyx', './vector.c'],
        include_dirs=["."],
        library_dirs=["."])
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


# from vector cimport *

# cdef int[5][4] COLORS  # R G B  24bits
# COLORS[0][:] = [0xE4EB15, 0xFFCD18, 0xC1C707, 0xE49009]  # Sand
# COLORS[1][:] = [0x0F5E9C, 0x1CA3EC, 0x2389DA, 0x5ABCD8]  # Water
# COLORS[2][:] = [0x461F00, 0x643D01, 0x8C6529, 0x000000]  # Wood
# COLORS[3][:] = [0xFF0000, 0xFF4500, 0xE25822, 0x000000]  # Fire
# COLORS[4][:] = [0x0A0A0A, 0x232323, 0x2C2424, 0x000000]  # Smoke

# cdef int[5 * 4] COLORS = [ # R G B  24bits
#     0xE4EB15, 0xFFCD18, 0xC1C707, 0xE49009,  # Sand
#     0x0F5E9C, 0x1CA3EC, 0x2389DA, 0x5ABCD8,  # Water
#     0x461F00, 0x643D01, 0x8C6529, 0x000000,  # Wood
#     0xFF0000, 0xFF4500, 0xE25822, 0x000000,  # Fire
#     0x0A0A0A, 0x232323, 0x2C2424, 0x000000  # Smoke
# ]
