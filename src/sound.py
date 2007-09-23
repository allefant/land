import global allegro
static import mem
static import global logg

class LandSound:
    SAMPLE *sample
    char *filename
    char *name

static int active

LandSound *def land_sound_load(char const *filename):
    LandSound *sound
    land_alloc(sound)
    sound->sample = load_sample(filename)
    sound->filename = land_strdup(filename)
    return sound

def land_sound_play(LandSound *s, float volume, pan, frequency):
    play_sample(s->sample, 255 * volume, 127.5 + 127.5 * pan, 1000 * frequency,
        0)

def land_sound_destroy(LandSound *s):
    land_free(s->filename)
    land_free(s)

def land_sound_init():
    register_sample_file_type("ogg", logg_load, None)
    active = 1

def land_sound_exit():
    active = 0
