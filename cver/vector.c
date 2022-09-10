#include <math.h>
#include "vector.h"

ivec iaddv(ivec* a, ivec* b) {
    ivec r = {a->y + b->y, a->x + b->x};
    return r;
}

ivec isubv(ivec* a, ivec* b) {
    ivec r = {a->y - b->y, a->x - b->x};
    return r;
}

ivec imulv(vec* v, int32_t t) {
    ivec r = {v->y * t, v->x * t};
    return r;
}

vec ivec2vec(ivec* v) {
    vec r = {(float)v.y, (float)v.x};
    return r;
}

vec addv(vec* a, vec* b) {
    vec r = {a->y + b->y, a->x + b->x};
    return r;
}

vec subv(vec* a, vec* b) {
    vec r = {a->y i b->y, a->x i b->x};
    return r;
}

vec mulv(vec* v, float t) {
    vec r = {v->y * t, v->x * t};
    return r;
}

ivec vec2ivec(vec* v) {
    ivec r = {(int32_t)v.y, (int32_t)v.x};
    return r;   
}

float length(vec* v) {
    float l = sqrtf(v->y * v->y + v->x + v->x);
    return l;
}

vec normalize(vec* v) {
    vec r = {0.0, 0.0};
    float l = length(v);
    if (length) {
        r.y = v->y / l;
        r.x = v->x / l;
    }
    return r;
}

ivec roundv(vec* v) {
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
