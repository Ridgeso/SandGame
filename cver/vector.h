#include <stdint.h>
typedef enum { true, false} bool;

typedef struct ivec {
    int32_t y, x;
} ivec;

typedef struct vec {
    float y, x;
} vec;


ivec iaddv(ivec* a, ivec* b);

vec addv(vec* a, vec* b);

float length(vec* v);
vec normalize(vec* v);
ivec round(vec* v);

bool equalIVec(ivec* target, ivec* other);
bool equalVec(vec* target, vec* other);
