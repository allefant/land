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

    char *filename

static import allegro5/a5_sound
static import file

static int active

LandStream *_default

def land_sound_load(char const *filename) -> LandSound *:
    char *path = land_path_with_prefix(filename)
    LandSound *sound = platform_sound_load(path)
    land_free(path)
    return sound

def land_sound_new(int samples, float frequency, int bits,
    channels) -> LandSound *:
    LandSound *sound = platform_sound_new(samples, frequency, bits, channels)
    return sound

def land_sound_sample_pointer(LandSound *self) -> void *:
    return platform_sound_sample_pointer(self)

def land_sound_length(LandSound *self) -> int:
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

def land_stream_new(int samples, fragments, float frequency,
    int bits, channels) -> LandStream *:
    return platform_stream_new(samples, fragments, frequency, bits, channels)

def land_stream_destroy(LandStream *self):
    land_free(self.filename)
    platform_stream_destroy(self)

def land_stream_buffer(LandStream *self) -> void *:
    return platform_stream_buffer(self)

def land_stream_fill(LandStream *self):
    platform_stream_fill(self)

def land_stream_music(LandStream *self, char const *filename):
    self.filename = land_path_with_prefix(filename)
    platform_stream_music(self, self.filename, true)

def land_stream_music_once(LandStream *self, char const *filename):
    self.filename = land_path_with_prefix(filename)
    platform_stream_music(self, self.filename, false)

def land_stream_volume(LandStream *self, float volume):
    platform_stream_volume(self, volume)

def land_stream_is_playing(LandStream *self) -> bool:
    return platform_stream_is_playing(self)

def land_stream_set_playing(LandStream *self, bool onoff):
    platform_stream_set_playing(self, onoff)

def land_stream_default -> LandStream*:
    if _default: return _default
    _default = land_stream_new(2048, 4, 22050, 16, 2)
    return _default
