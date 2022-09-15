#ifndef VECTOR_H
#define VECTOR_H


#include <stdint.h>
typedef enum { false, true } bool;

typedef struct ivec {
    int32_t y, x;
} ivec;

typedef struct vec {
    float y, x;
} vec;


ivec iaddv(ivec* a, ivec* b);
ivec isubv(ivec* a, ivec* b);
ivec imulv(vec* v, int32_t t);
vec ivec2vec(ivec* v);

vec addv(vec* a, vec* b);
vec subv(vec* a, vec* b);
vec mulv(vec* v, float t);
ivec vec2ivec(vec* v);

float length(vec* v);
vec normalize(vec* v);
ivec roundv(vec* v);

bool equalIVec(ivec* target, ivec* other);
bool equalVec(vec* target, vec* other);


#endif // VECTOR_H