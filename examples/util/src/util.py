import global land.land

def _com:
    for int i in range(25):
        int r = land_rand(INT_MIN, INT_MAX)
        printf("% 12d %s%.1f\n", r, r < 0 ? "- " : "+ ",
            log2(r < 0 ? -r : r))

land_commandline_example()

