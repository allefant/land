import global land.land

def _com:
    char *s = land_strdup("♥")
    char *pos = s
    int c = land_utf8_char(&pos)
    printf("%d\n", c)

land_commandline_example()
