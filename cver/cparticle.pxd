from vector cimport *
from tools cimport *


cdef enum ParticleType:
    SAND,
    WATER,
    WOOD,
    FIRE,
    SMOKE,
    EMPTY


cdef struct Particle_t:
    bint beenUpdated
    bint isFalling

    ParticleType pType
    int color

    ivec pos
    vec vel

    float lifetime
    float flammable
    float heat
    float friction
    float inertialResistance
    float bounciness
    float density
    int dispersion
    float mass

cdef bint onUpdate(Particle_t* particle, Board* board)
cdef void resetParticle(Particle_t* particle)
cdef bint isValid(ParticleType particle, ParticleType spot)

cdef Particle_t Sand(int y, int x, bint beenUpdated, bint isFalling)
cdef Particle_t Water(int y, int x, bint beenUpdated, bint isFalling)
cdef Particle_t Wood(int y, int x, bint beenUpdated, bint isFalling)
cdef Particle_t Fire(int y, int x, bint beenUpdated, bint isFalling)
cdef Particle_t Smoke(int y, int x, bint beenUpdated, bint isFalling)
cdef Particle_t Empty(int y, int x, bint beenUpdated, bint isFalling)
