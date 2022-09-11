import random
from libc.stdio cimport printf


cdef extern from "vector.h": *


cdef int COLORS[][] = {  # R G B  24bits
    {0xE4EB15, 0xFFCD18, 0xC1C707, 0xE49009},  # Sand
    {0x0F5E9C, 0x1CA3EC, 0x2389DA, 0x5ABCD8},  # Water
    {0x461F00, 0x643D01, 0x8C6529, 0x000000},  # Wood
    {0xFF0000, 0xFF4500, 0xE25822, 0x000000},  # Fire
    {0x0A0A0A, 0x232323, 0x2C2424, 0x000000}   # Smoke
}


ctypedef enum ParticleType:
    SAND = 0
    WATER
    WOOD
    FIRE
    SMOKE
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

cdef bint eqParticle(Particle_t* particle, Particle_t* other):
    if other.pType == EMPTY:
        return False

    if equalIVec(&particle.pos, &other.pos):
        return True
    return False

cdef void printParticle(Particle_t* particle):
    printf("Particle at y=%d x=%d\n", particle.y, particle.x)

cdef void pushNeighbors(Particle_t* particle, Board* board):
    pass

cdef bint onUpdate(Particle_t* particle, Board* board):
    if particle.pType == EMPTY:
        return False
    if particle.beenUpdated:
        return False
    particle.beenUpdated = True

    cdef bint hasBeenModified = particle.step()

    return hasBeenModified

cdef void resetParticle(Particle_t* particle):
    particle.been_updated = False


##### SAND
cdef sandStep(Particle_t* particle):
    pass

cdef Particle_t Sand(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t sand

    sand.beenUpdated = beenUpdated
    sand.isFalling = isFalling

    sand.pType = SAND
    sand.color = COLORS[SAND][random.randint(0, 3)]

    sand.pos.y = y
    sand.pos.x = x
    sand.vel.y = 0.0
    sand.vel.x = 0.0
    
    sand.lifetime = 0.0
    sand.flammable = 100.0
    sand.heat = 0.0
    sand.friction = 0.75
    sand.inertial_resistance = 0.5
    sand.bounciness = 0.5
    sand.density = 0.0
    sand.dispersion = 0
    sand.mass = 54.0

    sand.step = &sandStep

    return sand


##### Water
cdef waterStep(Particle_t* particle):
    pass

cdef Particle_t Water(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t water

    water.beenUpdated = beenUpdated
    water.isFalling = isFalling

    water.pType = WATER
    water.color = COLORS[WATER][random.randint(0, 3)]

    water.pos.y = y
    water.pos.x = x
    water.vel.y = 0.0
    water.vel.x = 0.0
    
    water.lifetime = 0.0
    water.flammable = 100.0
    water.heat = 0.0
    water.friction = 0.75
    water.inertial_resistance = 0.5
    water.bounciness = 0.5
    water.density = 0.0
    water.dispersion = 0
    water.mass = 54.0

    water.step = &waterStep

    return water


##### WOOD
cdef woodStep(Particle_t* particle):
    pass

cdef Particle_t Wood(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t wood

    wood.beenUpdated = beenUpdated
    wood.isFalling = isFalling

    wood.pType = WOOD
    wood.color = COLORS[WOOD][random.randint(0, 2)]

    wood.pos.y = y
    wood.pos.x = x
    wood.vel.y = 0.0
    wood.vel.x = 0.0
    
    wood.lifetime = 0.0
    wood.flammable = 100.0
    wood.heat = 0.0
    wood.friction = 0.75
    wood.inertial_resistance = 0.5
    wood.bounciness = 0.5
    wood.density = 0.0
    wood.dispersion = 0
    wood.mass = 54.0

    wood.step = &woodStep

    return wood


##### Fire
cdef fireStep(Particle_t* particle):
    pass

cdef Particle_t Fire(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t fire

    fire.beenUpdated = beenUpdated
    fire.isFalling = isFalling

    fire.pType = FIRE
    fire.color = COLORS[FIRE][random.randint(0, 2)]

    fire.pos.y = y
    fire.pos.x = x
    fire.vel.y = 0.0
    fire.vel.x = 0.0
    
    fire.lifetime = 0.0
    fire.flammable = 100.0
    fire.heat = 0.0
    fire.friction = 0.75
    fire.inertial_resistance = 0.5
    fire.bounciness = 0.5
    fire.density = 0.0
    fire.dispersion = 0
    fire.mass = 54.0

    fire.step = &fireStep
    return fire


##### Smoke
cdef smokeStep(Particle_t* particle):
    pass

cdef Particle_t Smoke(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t smoke

    smoke.beenUpdated = beenUpdated
    smoke.isFalling = isFalling

    smoke.pType = SMOKE
    smoke.color = COLORS[SMOKE][random.randint(0, 2)]

    smoke.pos.y = y
    smoke.pos.x = x
    smoke.vel.y = 0.0
    smoke.vel.x = 0.0
    
    smoke.lifetime = 0.0
    smoke.flammable = 100.0
    smoke.heat = 0.0
    smoke.friction = 0.75
    smoke.inertial_resistance = 0.5
    smoke.bounciness = 0.5
    smoke.density = 0.0
    smoke.dispersion = 0
    smoke.mass = 54.0

    smoke.step = &smokeStep
    return smoke


##### EMPTY CELL
cdef Particle_t Empty(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t empty
    wood.pType = EMPTY
    wood.color = 0x000000

    return empty