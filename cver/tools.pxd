from cparticle cimport *


cdef struct Chunk:
    int y, x
    int height, width
    bint updateThisFrame
    bint shouldBeUpdatedNextFrame


cdef struct Board:
    int height, width
    Particle_t** board


cdef struct Brush:
    ParticleType pen
    int penSize
