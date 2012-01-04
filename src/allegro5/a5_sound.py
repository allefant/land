import global allegro5.allegro, allegro5.allegro_acodec

import land/sound, land/mem
static import global allegro5.allegro_audio

static class LandSoundPlatform:
    LandSound super
    ALLEGRO_SAMPLE *a5
    ALLEGRO_SAMPLE_ID last_playing
    void *buffer

static class LandStreamPlatform:
    LandStream super
    ALLEGRO_AUDIO_STREAM *a5
    void *fragment

static bool def get_params(int channels, bits, *chan_conf, *depth):
    if channels == 1: *chan_conf = ALLEGRO_CHANNEL_CONF_1
    elif channels == 2: *chan_conf = ALLEGRO_CHANNEL_CONF_2
    else: return False

    if bits == 8: *depth = ALLEGRO_AUDIO_DEPTH_INT8
    elif bits == 16: *depth = ALLEGRO_AUDIO_DEPTH_INT16
    else: return False

    return True

LandSound *def platform_sound_load(char const *filename):
    LandSoundPlatform *self
    land_alloc(self)
    self->a5 = al_load_sample(filename)
    self->super.filename = land_strdup(filename)
    return (void *)self

LandSound *def platform_sound_new(int samples, float frequency, int bits,
    channels):
    LandSoundPlatform *self
    land_alloc(self)
    int chan_conf = 0, depth = 0
    get_params(channels, bits, &chan_conf, &depth)

    int sample_size = al_get_channel_count(chan_conf) * al_get_audio_depth_size(depth)
    int bytes = samples * sample_size;

    self->buffer = land_malloc(bytes)
    self->a5 = al_create_sample(self->buffer, samples, frequency,
        depth, chan_conf, False)
    return (void *)self

void *def platform_sound_sample_pointer(LandSound *super):
    LandSoundPlatform *self = (void *)super
    return al_get_sample_data(self->a5)

def platform_sound_play(LandSound *s, float volume, pan, frequency,
    bool loop):
    LandSoundPlatform *self = (void *)s
    al_play_sample(self->a5, volume, pan, frequency,
        loop ? ALLEGRO_PLAYMODE_LOOP : ALLEGRO_PLAYMODE_ONCE,
        &self->last_playing)

def platform_sound_stop(LandSound *s):
    LandSoundPlatform *self = (void *)s
    al_stop_sample(&self->last_playing)

def platform_sound_destroy(LandSound *s):
    LandSoundPlatform *self = (void *)s
    al_destroy_sample(self->a5)
    if self->buffer: land_free(self->buffer)
    land_free(s->filename)
    land_free(s)

def platform_sound_init():
    al_init_acodec_addon()
    al_install_audio()
    al_reserve_samples(8)

def platform_sound_exit():
    pass

LandStream *def platform_stream_new(int samples, fragments,
    float frequency, int bits, channels):
    LandStreamPlatform *self
    land_alloc(self)
    LandStream *super = (void *)self

    int chan_conf = 0, depth = 0
    get_params(channels, bits, &chan_conf, &depth)

    super->fragments = fragments
    super->samples = samples
    super->sample_size = al_get_channel_count(chan_conf) * al_get_audio_depth_size(depth);
    self->a5 = al_create_audio_stream(fragments, samples, frequency, depth,
        chan_conf)

    al_attach_audio_stream_to_mixer(self->a5, al_get_default_mixer())

    return super

def platform_stream_destroy(LandStream *super):
    LandStreamPlatform *self = (void *)super
    al_destroy_audio_stream(self->a5)
    land_free(super)

void *def platform_stream_buffer(LandStream *super):
    LandStreamPlatform *self = (void *)super
    if al_get_available_audio_stream_fragments(self->a5) == 0: return None
    self->fragment = al_get_audio_stream_fragment(self->a5):
    return self->fragment

def platform_stream_fill(LandStream *super):
    LandStreamPlatform *self = (void *)super
    al_set_audio_stream_fragment(self->a5, self->fragment)

def platform_stream_music(LandStream *super, char const *filename):
    LandStreamPlatform *self = (void *)super
    al_destroy_audio_stream(self->a5)
    self->a5 = al_load_audio_stream(filename,
        super->fragments, super->samples);
    al_attach_audio_stream_to_mixer(self->a5, al_get_default_mixer())
    al_set_audio_stream_playmode(self->a5, ALLEGRO_PLAYMODE_LOOP)
