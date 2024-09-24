import land/land

def _draw(LandRunner *self):
    pass

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape): land_quit()

def _config():
    land_set_display_parameters(640, 480, LAND_FULLSCREEN | LAND_OPENGL)
land_example(_config, None, _tick, _draw, None)
