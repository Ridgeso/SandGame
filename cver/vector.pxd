cdef extern from "vector.h":
    cdef struct ivec:
        int y, x

    cdef struct vec:
        float y, x

    ivec iaddv(ivec* a, ivec* b)
    ivec isubv(ivec* a, ivec* b)
    ivec imulv(vec* v, int t)
    vec ivec2vec(ivec* v)

    vec addv(vec* a, vec* b)
    vec subv(vec* a, vec* b)
    vec mulv(vec* v, float t)
    ivec vec2ivec(vec* v)

    float length(vec* v)
    vec normalize(vec* v)
    ivec roundv(vec* v)

    bint equalIVec(ivec* target, ivec* other)
    bint equalVec(vec* target, vec* other)
