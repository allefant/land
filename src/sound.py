static import mem
import global stdbool

static import allegro5/a5_sound

class LandSound:
    char *filename
    char *name

class LandStream:
    int samples
    int sample_size
    int fragments
    float frequency

static import allegro5/a5_sound

static int active

LandSound *def land_sound_load(char const *filename):
    LandSound *sound = platform_sound_load(filename)
    return sound

LandSound *def land_sound_new(int samples, float frequency, int bits,
    channels):
    LandSound *sound = platform_sound_new(samples, frequency, bits, channels)
    return sound

void *def land_sound_sample_pointer(LandSound *self):
    return platform_sound_sample_pointer(self)

int def land_sound_length(LandSound *self):
    return platform_sound_length(self)

def land_sound_seconds(LandSound *self) -> double:
    return platform_sound_seconds(self)

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

LandStream *def land_stream_new(int samples, fragments, float frequency,
    int bits, channels):
    return platform_stream_new(samples, fragments, frequency, bits, channels)

def land_stream_destroy(LandStream *self):
    platform_stream_destroy(self)

void *def land_stream_buffer(LandStream *self):
    return platform_stream_buffer(self)

def land_stream_fill(LandStream *self):
    platform_stream_fill(self)

def land_stream_music(LandStream *self, char const *filename):
    platform_stream_music(self, filename)

def land_stream_volume(LandStream *self, float volume):
    platform_stream_volume(self, volume)

bool def land_stream_is_playing(LandStream *self):
    return platform_stream_is_playing(self)

def land_stream_set_playing(LandStream *self, bool onoff):
    platform_stream_set_playing(self, onoff)

