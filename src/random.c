#include <stdlib.h>

#include "random.h"

float land_rnd(float min, float max)
{
    if (min >= max)
        return min;
    return min + ((float)rand() / RAND_MAX) * (max - min);
}

int land_rand(int min, int max)
{
    if (min >= max)
        return min;
    return min + rand() % (max - min + 1);
}
