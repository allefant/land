import global land.land

def main() -> int:
    land_init()
    char *s = land_strdup("♥")
    char *pos = s
    int c = land_utf8_char(&pos)
    printf("%d\n", c)
    return 0
