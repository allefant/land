import global land.land

def main() -> int:
    land_init()
    for int i in range(25):
        int r = land_rand(INT_MIN, INT_MAX)
        printf("% 12d %s%.1f\n", r, r < 0 ? "- " : "+ ",
            log2(r < 0 ? -r : r))
    return 0
