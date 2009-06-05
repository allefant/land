static import mem

class LandSound:
    char *filename
    char *name

static import allegro5/a5_sound

static int active

LandSound *def land_sound_load(char const *filename):
    LandSound *sound = platform_sound_load(filename)
    return sound

def land_sound_play(LandSound *s, float volume, pan, frequency):
    if not s: return
    platform_sound_play(s, volume, pan, frequency, false)

def land_sound_loop(LandSound *s, float volume, pan, frequency):
    if not s: return
    platform_sound_play(s, volume, pan, frequency, true)

def land_sound_stop(LandSound *s):
    if not s: return
    platform_sound_stop(s)

def land_sound_destroy(LandSound *s):
    if not s: return
    platform_sound_destroy(s)

def land_sound_init():
    platform_sound_init()
    active = 1

def land_sound_exit():
    platform_sound_exit()
    active = 0
