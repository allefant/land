import global land/land

macro N 1024 * 16 * 64
macro S 16

char words[N][S]

def main(int argc, char **argv) -> int:
    land_init()

    printf("Generating %d random strings.\n", N)
    for int i = 0 while i < N with i++:
        for int j = 0 while j < S - 1 with j++:
            words[i][j] = land_rand(33, 127)
        words[i][S - 1] = 0

    LandHash *hash = land_hash_new()

    printf("Adding %d hash entries.\n", N)
    for int i = 0 while i < N with i++:
        char str[256]
        snprintf(str, sizeof str, "%d", i)
        land_hash_insert(hash, words[i], land_strdup(str))
        if i % (1024 * 16) == 1023:    
            land_hash_print_stats(hash)
            fflush(stdout)

    printf("Comparing %d hash entries.\n", N)
    for int i = 0 while i < N with i++:
        char str[256]
        snprintf(str, sizeof str, "%d", i)
        char *found = land_hash_get(hash, words[i])
        if strcmp(str, found):
            printf("Wrong! Wanted %s but got %s.\n", str, found)

    land_hash_print_stats(hash)

    return 0
