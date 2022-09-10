#include <math.h>
#include "vector.h"

ivec iaddv(ivec* a, ivec* b) {
    ivec r = {a->y + b->y, a->x + b->x};
    return r;
}

vec addv(vec* a, vec* b) {
    vec r = {a->y + b->y, a->x + b->x};
    return r;
}

float length(vec* v) {
    float l = sqrtf(v->y * v->y + v->x + v->x);
    return l;
}

vec normalize(vec* v) {
    float l = length(v);
    vec r = {v->y / l, v->x / l};
    return r;
}

ivec round(vec* v) {
    ivec r = {(int32_t)roundf(v->y), (int32_t)roundf(v->x)};
    return r;
}

bool equalIVec(ivec* target, ivec* other) {
    if (target->y == other->y && target->x == other->x)
        return true;
    return false;
}

bool equalVec(vec* target, vec* other) {
    if (target->y == other->y && target->x == other->x)
        return true;
    return false;
}
