import global land/land

macro N 1024 * 16 * 64
macro S 16

char words[N][S]

int def main(int argc, char **argv):
    land_init()

    printf("Generating %d random strings.\n", N)
    for int i = 0; i < N; i++:
        for int j = 0; j < S - 1; j++:
            words[i][j] = land_rand(33, 127)
        words[i][S - 1] = 0

     LandHash *hash = land_hash_new()

    printf("Adding %d hash entries.\n", N)
    for int i = 0; i < N; i++:
        char str[256]
        uszprintf(str, sizeof str, "%d", i)
        land_hash_insert(hash, words[i], land_strdup(str))
        if i % (1024 * 16) == 1023:    
            land_hash_print_stats(hash)
            fflush(stdout)

    printf("Comparing %d hash entries.\n", N)
    for int i = 0; i < N; i++:
        char str[256]
        uszprintf(str, sizeof str, "%d", i)
        char *found = land_hash_get(hash, words[i])
        if ustrcmp(str, found):
            printf("Wrong! Wanted %s but got %s.\n", str, found)

    land_hash_print_stats(hash)

    return 0
