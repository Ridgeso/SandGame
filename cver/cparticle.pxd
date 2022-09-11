from vector cimport *

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

    bint(* step)(Particle_t*)
