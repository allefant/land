import global stdint
static import global land/land
#
#   A C-program for MT19937, with initialization improved 2002/1/26.
#   Coded by Takuji Nishimura and Makoto Matsumoto.
#
#   Before using, initialize the state by using init_genrand(seed)
#   or init_by_array(init_key, key_length).
#
#   Copyright (C) 1997 - 2002, Makoto Matsumoto and Takuji Nishimura,
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. The names of its contributors may not be used to endorse or promote
#        products derived from this software without specific prior written
#        permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
#   Any feedback is very welcome.
#   http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/emt.html
#   email: m-mat @ math.sci.hiroshima-u.ac.jp (remove space)
#

# Period parameters 
macro LAND_RANDOM_N 624
static macro N LAND_RANDOM_N
static macro M 397
static macro MATRIX_A 0x9908b0dfUL   # constant vector a 
static macro UPPER_MASK 0x80000000UL # most significant w-r bits 
static macro LOWER_MASK 0x7fffffffUL # least significant r bits 

class LandRandom:
    uint32_t mt[LAND_RANDOM_N] # the array for the state vector  
    uint32_t mti # mti==N+1 means mt[N] is not initialized 

static LandRandom default_state = {.mti = N + 1}

# initializes mt[N] with a seed 
static def init_genrand(LandRandom *r, unsigned long s):
    r->mt[0]= s & 0xffffffffUL
    for r->mti=1 while r->mti<N with r->mti++:
        r->mt[r->mti] = (1812433253UL * (
            r->mt[r->mti-1] ^ (r->mt[r->mti-1] >> 30)
            ) + r->mti)
        # See Knuth TAOCP Vol2. 3rd Ed. P.106 for multiplier. 
        # In the previous versions, MSBs of the seed affect   
        # only MSBs of the array mt[].                        
        # 2002/01/09 modified by Makoto Matsumoto             
        r->mt[r->mti] &= 0xffffffffUL
        # for >32 bit machines 


*** "if" 0
# initialize by an array with array-length 
# init_key is the array for initializing keys 
# key_length is its length 
# slight change for C++, 2004/2/26 
static def init_by_array(unsigned long init_key[], int key_length):
    int i, j, k
    init_genrand(19650218UL)
    i=1; j=0
    k = (N>key_length ? N : key_length)
    for  while k with k--:
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1664525UL)) + init_key[j] + j # non linear 
        mt[i] &= 0xffffffffUL # for WORDSIZE > 32 machines 
        i++; j++
        if i>=N: mt[0] = mt[N-1]; i=1
        if j>=key_length: j=0

    for k=N-1 while k with k--:
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1566083941UL)) - i # non linear 
        mt[i] &= 0xffffffffUL # for WORDSIZE > 32 machines 
        i++
        if i>=N: mt[0] = mt[N-1]; i=1

    mt[0] = 0x80000000UL # MSB is 1; assuring non-zero initial array 
*** "endif"

# generates a random number on [0,0xffffffff]-interval 
static unsigned long def genrand_int32(LandRandom *r):
    unsigned long y
    static const unsigned long mag01[2]={0x0UL, MATRIX_A}
    # mag01[x] = x * MATRIX_A  for x=0,1 

    if r->mti >= N: # generate N words at one time 
        int kk

        if r->mti == N+1: # if init_genrand() has not been called, 
            init_genrand(r, 5489UL); # a default initial seed is used 

        for kk=0 while kk<N-M with kk++:
            y = (r->mt[kk]&UPPER_MASK)|(r->mt[kk+1]&LOWER_MASK)
            r->mt[kk] = r->mt[kk+M] ^ (y >> 1) ^ mag01[y & 0x1UL]

        for  while kk<N-1 with kk++:
            y = (r->mt[kk]&UPPER_MASK)|(r->mt[kk+1]&LOWER_MASK)
            r->mt[kk] = r->mt[kk+(M-N)] ^ (y >> 1) ^ mag01[y & 0x1UL]

        y = (r->mt[N-1]&UPPER_MASK)|(r->mt[0]&LOWER_MASK)
        r->mt[N-1] = r->mt[M-1] ^ (y >> 1) ^ mag01[y & 0x1UL]

        r->mti = 0

    y = r->mt[r->mti++]

    # Tempering 
    y ^= (y >> 11)
    y ^= (y << 7) & 0x9d2c5680UL
    y ^= (y << 15) & 0xefc60000UL
    y ^= (y >> 18)

    return y

*** "if" 0

# generates a random number on [0,0x7fffffff]-interval 
static long def genrand_int31():
    return (long)(genrand_int32()>>1)

# generates a random number on [0,1]-real-interval 
static double def genrand_real1():
    return genrand_int32()*(1.0/4294967295.0)
    # divided by 2^32-1 

# generates a random number on [0,1)-real-interval 
static double def genrand_real2():
    return genrand_int32()*(1.0/4294967296.0)
    # divided by 2^32 

# generates a random number on (0,1)-real-interval 
static double def genrand_real3():
    return (((double)genrand_int32()) + 0.5)*(1.0/4294967296.0)
    # divided by 2^32 

# generates a random number on [0,1) with 53-bit resolution
static double def genrand_res53():
    unsigned long a=genrand_int32()>>5, b=genrand_int32()>>6
    return(a*67108864.0+b)*(1.0/9007199254740992.0)

# These real versions are due to Isaku Wada, 2002/01/09 added 

*** "endif"

static macro MAX_NUMBER 4294967295U

def land_seed(int seed):
    init_genrand(&default_state, seed)

float def land_rnd(float min, float max):
    if min >= max: return min
    return min + (
        (float)genrand_int32(&default_state) / MAX_NUMBER) * (max - min)

int def land_rand(int min, int max):
    if min >= max: return min
    return min + genrand_int32(&default_state) % (max - min + 1)

LandRandom *def land_random_new(int seed):
    LandRandom *self
    land_alloc(self)
    init_genrand(self, seed)
    return self

def land_random_del(LandRandom *self):
    land_free(self)

int def land_random(LandRandom *r, int min, int max):
    if min >= max: return min
    return min + genrand_int32(r) % (max - min + 1)
