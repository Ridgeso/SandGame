import random
from libc.stdio cimport printf

from cparticle cimport *


cdef int[5][4] COLORS = [  # R G B  24bits
    [0xE4EB15, 0xFFCD18, 0xC1C707, 0xE49009],  # Sand
    [0x0F5E9C, 0x1CA3EC, 0x2389DA, 0x5ABCD8],  # Water
    [0x461F00, 0x643D01, 0x8C6529, 0x000000],  # Wood
    [0xFF0000, 0xFF4500, 0xE25822, 0x000000],  # Fire
    [0x0A0A0A, 0x232323, 0x2C2424, 0x000000]   # Smoke
]


cdef bint eqParticle(Particle_t* particle, Particle_t* other):
    if other.pType == EMPTY:
        return False

    if equalIVec(&particle.pos, &other.pos):
        return True
    return False

cdef void printParticle(Particle_t* particle):
    printf("Particle at y=%d x=%d\n", particle.pos.y, particle.pos.x)

cdef void pushNeighbors(Particle_t* particle, Board* board):
    pass

cdef bint step(Particle_t* particle, Board* board):
    if particle.pType == SAND:
        return sandStep(particle, board)
    elif particle.pType == WATER:
        return waterStep(particle, board)
    elif particle.pType == WOOD:
        return woodStep(particle, board)
    elif particle.pType == FIRE:
        return fireStep(particle, board)
    elif particle.pType == SMOKE:
        return smokeStep(particle, board)
    else:
        return False

cdef bint onUpdate(Particle_t* particle, Board* board):
    if particle.pType == EMPTY:
        return False
    if particle.beenUpdated:
        return False
    particle.beenUpdated = True

    cdef bint hasBeenModified = step(particle, board)

    return hasBeenModified

cdef void resetParticle(Particle_t* particle):
    particle.beenUpdated = False

cdef bint isValid(ParticleType particle, ParticleType spot):
    return True


##### SAND
cdef bint sandStep(Particle_t* particle, Board* board):
    cdef bint hasBeenModified = False
    cdef ivec nextPos = particle.pos

    if inBounds(board, particle.pos.y + 1, particle.pos.x):
        nextPos.y = particle.pos.y + 1
        nextPos.x = particle.pos.x
        hasBeenModified = True
    elif inBounds(board, particle.pos.y + 1, particle.pos.x - 1):
        nextPos.y = particle.pos.y + 1
        nextPos.x = particle.pos.x - 1
        hasBeenModified = True
    elif inBounds(board, particle.pos.y + 1, particle.pos.x + 1):
        nextPos.y = particle.pos.y + 1
        nextPos.x = particle.pos.x + 1
        hasBeenModified = True
    
    if hasBeenModified:
        # printf("Moved from %d %d %d | ", particle.pType, particle.pos.y, particle.pos.x)
        # board.board[nextPos.y][nextPos.x] = particle[0]
        # particle.pos = nextPos
        swapParticles(board, particle, nextPos.y, nextPos.x)
        # printf("to %d %d %d\n", particle.pType, particle.pos.y, particle.pos.x)
    
    return hasBeenModified

cdef bint sandIsValid(ParticleType other):
    return False

cdef Particle_t Sand(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t sand

    sand.beenUpdated = beenUpdated
    sand.isFalling = isFalling

    sand.pType = SAND
    sand.color = COLORS[<int>SAND][random.randint(0, 3)]

    sand.pos.y = y
    sand.pos.x = x
    sand.vel.y = 0.0
    sand.vel.x = 0.0
    
    sand.lifetime = 0.0
    sand.flammable = 100.0
    sand.heat = 0.0
    sand.friction = 0.75
    sand.inertialResistance = 0.5
    sand.bounciness = 0.5
    sand.density = 0.0
    sand.dispersion = 0
    sand.mass = 54.0

    return sand


##### Water
cdef bint waterStep(Particle_t* particle, Board* board):
    return False

cdef bint waterIsValid(ParticleType other):
    return False

cdef Particle_t Water(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t water

    water.beenUpdated = beenUpdated
    water.isFalling = isFalling

    water.pType = WATER
    water.color = COLORS[<int>WATER][random.randint(0, 3)]

    water.pos.y = y
    water.pos.x = x
    water.vel.y = 0.0
    water.vel.x = 0.0
    
    water.lifetime = 0.0
    water.flammable = 100.0
    water.heat = 0.0
    water.friction = 0.75
    water.inertialResistance = 0.5
    water.bounciness = 0.5
    water.density = 0.0
    water.dispersion = 0
    water.mass = 54.0

    return water


##### WOOD
cdef bint woodStep(Particle_t* particle, Board* board):
    return False

cdef bint woodIsValid(ParticleType other):
    return False

cdef Particle_t Wood(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t wood

    wood.beenUpdated = beenUpdated
    wood.isFalling = isFalling

    wood.pType = WOOD
    wood.color = COLORS[<int>WOOD][random.randint(0, 2)]

    wood.pos.y = y
    wood.pos.x = x
    wood.vel.y = 0.0
    wood.vel.x = 0.0
    
    wood.lifetime = 0.0
    wood.flammable = 100.0
    wood.heat = 0.0
    wood.friction = 0.75
    wood.inertialResistance = 0.5
    wood.bounciness = 0.5
    wood.density = 0.0
    wood.dispersion = 0
    wood.mass = 54.0

    return wood


##### Fire
cdef bint fireStep(Particle_t* particle, Board* board):
    return False

cdef bint fireIsValid(ParticleType other):
    return False

cdef Particle_t Fire(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t fire

    fire.beenUpdated = beenUpdated
    fire.isFalling = isFalling

    fire.pType = FIRE
    fire.color = COLORS[<int>FIRE][random.randint(0, 2)]

    fire.pos.y = y
    fire.pos.x = x
    fire.vel.y = 0.0
    fire.vel.x = 0.0
    
    fire.lifetime = 0.0
    fire.flammable = 100.0
    fire.heat = 0.0
    fire.friction = 0.75
    fire.inertialResistance = 0.5
    fire.bounciness = 0.5
    fire.density = 0.0
    fire.dispersion = 0
    fire.mass = 54.0

    return fire


##### Smoke
cdef bint smokeStep(Particle_t* particle, Board* board):
    return False

cdef bint smokeIsValid(ParticleType other):
    return False

cdef Particle_t Smoke(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t smoke

    smoke.beenUpdated = beenUpdated
    smoke.isFalling = isFalling

    smoke.pType = SMOKE
    smoke.color = COLORS[<int>SMOKE][random.randint(0, 2)]

    smoke.pos.y = y
    smoke.pos.x = x
    smoke.vel.y = 0.0
    smoke.vel.x = 0.0
    
    smoke.lifetime = 0.0
    smoke.flammable = 100.0
    smoke.heat = 0.0
    smoke.friction = 0.75
    smoke.inertialResistance = 0.5
    smoke.bounciness = 0.5
    smoke.density = 0.0
    smoke.dispersion = 0
    smoke.mass = 54.0

    return smoke


##### EMPTY CELL
cdef Particle_t Empty(int y, int x, bint beenUpdated, bint isFalling):
    cdef Particle_t empty

    empty.beenUpdated = beenUpdated
    empty.isFalling = isFalling

    empty.pType = EMPTY
    empty.color = 0x000000

    empty.pos.y = y
    empty.pos.x = x
    empty.vel.y = 0.0
    empty.vel.x = 0.0
    
    empty.lifetime = 0.0
    empty.flammable = 0.0
    empty.heat = 0.0
    empty.friction = 0.0
    empty.inertialResistance = 0.0
    empty.bounciness = 0.0
    empty.density = 0.0
    empty.dispersion = 0
    empty.mass = 0.0


    return empty