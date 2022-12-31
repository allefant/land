import global stdint
import global stdbool
static import land.mem

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
enum: LAND_RANDOM_N = 624
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


***scramble
"""
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
"""
***

# generates a random number on [0,0xffffffff]-interval 
static def genrand_int32(LandRandom *r) -> unsigned long:
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

***scramble
"""

# generates a random number on [0,0x7fffffff]-interval 
static def genrand_int31() -> long:
    return (long)(genrand_int32()>>1)

# generates a random number on [0,1]-real-interval 
static def genrand_real1() -> double:
    return genrand_int32()*(1.0/4294967295.0)
    # divided by 2^32-1 

# generates a random number on [0,1)-real-interval 
static def genrand_real2() -> double:
    return genrand_int32()*(1.0/4294967296.0)
    # divided by 2^32 

# generates a random number on (0,1)-real-interval 
static def genrand_real3() -> double:
    return (((double)genrand_int32()) + 0.5)*(1.0/4294967296.0)
    # divided by 2^32 

# generates a random number on [0,1) with 53-bit resolution
static def genrand_res53() -> double:
    unsigned long a=genrand_int32()>>5, b=genrand_int32()>>6
    return(a*67108864.0+b)*(1.0/9007199254740992.0)

# These real versions are due to Isaku Wada, 2002/01/09 added 

"""
***

static macro MAX_NUMBER 4294967295U

def land_seed(int seed):
    init_genrand(&default_state, seed)

def land_rnd(double rmin, rmax) -> double:
    return land_random_f(&default_state, rmin, rmax)

# both rmin and rmax are inclusive
# note: not threadsafe, will crash in genrand_int32
def land_rand(int64_t rmin, rmax) -> int:
    return land_random(&default_state, rmin, rmax)

def land_random_new(int seed) -> LandRandom *:
    LandRandom *self
    land_alloc(self)
    init_genrand(self, seed)
    return self

def land_random_del(LandRandom *self):
    land_free(self)

def land_random(LandRandom *r, int64_t rmin, rmax) -> int:
    """
    rmax is inclusive, so there are (rmax - rmin + 1) total values
    """
    if rmin >= rmax: return rmin
    int64_t d = rmax
    d++
    d -= rmin
    return rmin + genrand_int32(r) % d

def land_random_f(LandRandom *r, double rmin, rmax) -> double:
    """
    Random value in the half-open interval [min, max[, that is min is inclusive
    but max is exclusive.
    """
    if rmin >= rmax: return rmin
    return rmin + (
        (double)genrand_int32(r) / MAX_NUMBER) * (rmax - rmin)

def land_probability(double p) -> bool:
    return land_rnd(0, 1) < p

def land_shuffle(int *a, int n):
    for int i in range(n):
        a[i] = i
    # n=6: 0 1 2 3 4 5
    for int i in range(n - 1): # 0 1 2 3 4
        int j = land_rand(i, n - 1) # [0..5], [1..5], [2..5], [3..5], [4..5]
        int t = a[i]
        a[i] = a[j]
        a[j] = t

def land_select_random(int *weights, int n) -> int:
    int total = 0
    for int i in range(n):
        total += weights[i]
    int r = land_rand(0, total - 1)
    int x = 0
    for int i in range(n):
        x += weights[i]
        if r < x:
            return i
    return 0
