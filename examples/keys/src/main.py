import global land/land

def init(LandRunner *self):
    for int i = 0 while i < LandKeysCount with i++:
        printf("%d: %s\n", i, land_key_name(i))

def tick(LandRunner *self):
    land_quit()

def draw(LandRunner *self):
    pass

land_begin_shortcut(640, 480, 30, LAND_OPENGL | LAND_WINDOWED,
    init, NULL, tick, draw, NULL, NULL)
