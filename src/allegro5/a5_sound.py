import global allegro5.allegro, allegro5.allegro_acodec

import land/sound, land/mem
static import global allegro5.allegro_audio
static import land.array
static import land.log

static class LandSoundPlatform:
    LandSound super
    ALLEGRO_SAMPLE *a5
    ALLEGRO_SAMPLE_ID last_playing
    void *buffer
    bool last_failed
    bool last_started

static class LandStreamPlatform:
    LandStream super
    ALLEGRO_AUDIO_STREAM *a5
    void *fragment

static LandArray *streaming

static def get_params(int channels, bits, *chan_conf, *depth) -> bool:
    if channels == 1: *chan_conf = ALLEGRO_CHANNEL_CONF_1
    elif channels == 2: *chan_conf = ALLEGRO_CHANNEL_CONF_2
    else: return False

    if bits == 8: *depth = ALLEGRO_AUDIO_DEPTH_INT8
    elif bits == 16: *depth = ALLEGRO_AUDIO_DEPTH_INT16
    else: return False

    return True

def platform_sound_load(char const *filename) -> LandSound *:
    LandSoundPlatform *self
    land_alloc(self)
    self.a5 = al_load_sample(filename)
    self.super.filename = land_strdup(filename)
    if self.a5:
        self.super.loaded = True
    return (void *)self

def platform_sound_new(int samples, float frequency, int bits,
    channels) -> LandSound *:
    LandSoundPlatform *self
    land_alloc(self)
    int chan_conf = 0, depth = 0
    get_params(channels, bits, &chan_conf, &depth)

    int sample_size = al_get_channel_count(chan_conf) * al_get_audio_depth_size(depth)
    int bytes = samples * sample_size;

    self.buffer = land_malloc(bytes)
    self.a5 = al_create_sample(self->buffer, samples, frequency,
        depth, chan_conf, False)
    return (void *)self

def platform_sound_sample_pointer(LandSound *super) -> void *:
    LandSoundPlatform *self = (void *)super
    return al_get_sample_data(self.a5)

def platform_sound_length(LandSound *super) -> int:
    LandSoundPlatform *self = (void *)super
    return al_get_sample_length(self.a5)

def platform_sound_seconds(LandSound *super) -> double:
    LandSoundPlatform *self = (void *)super
    double x = al_get_sample_length(self.a5)
    x /= al_get_sample_frequency(self.a5)
    return x

def platform_sound_play(LandSound *s, float volume, pan, frequency,
    bool loop):
    LandSoundPlatform *self = (void *)s
    if not self.a5: return
    if al_play_sample(self.a5, volume, pan, frequency,
            loop ? ALLEGRO_PLAYMODE_LOOP : ALLEGRO_PLAYMODE_ONCE,
            &self.last_playing):
        self.last_started = True
        self.last_failed = False
    else:
        self.last_started = False
        self.last_failed = True

def platform_sound_change(LandSound *s, float volume, pan, frequency):
    LandSoundPlatform *self = (void *)s
    ALLEGRO_SAMPLE_INSTANCE* inst = al_lock_sample_id(&self.last_playing)
    al_set_sample_instance_gain(inst, volume)
    al_set_sample_instance_pan(inst, pan)
    al_set_sample_instance_speed(inst, frequency)
    al_unlock_sample_id(&self.last_playing)

def platform_sound_stop(LandSound *s):
    LandSoundPlatform *self = (void *)s
    if self.last_failed:
        return
    al_stop_sample(&self.last_playing)
    self.last_started = False

def platform_sound_is_playing(LandSound *s) -> bool:
    LandSoundPlatform *self = (void *)s
    if self.last_failed:
        return False
    if not self.last_started:
        return False
    ALLEGRO_SAMPLE_INSTANCE* inst = al_lock_sample_id(&self.last_playing)
    bool r = al_get_sample_instance_playing(inst)
    al_unlock_sample_id(&self.last_playing)
    return r

def platform_sound_destroy(LandSound *s):
    LandSoundPlatform *self = (void *)s
    al_destroy_sample(self.a5)
    if self.buffer: land_free(self->buffer)
    land_free(s->filename)
    land_free(s)

def platform_sound_init():
    al_init_acodec_addon()
    al_install_audio()
    al_reserve_samples(32)

def platform_sound_exit():
    if streaming:
        for LandStream *s in LandArray *streaming:
            LandStreamPlatform *s2 = (void *)s
            al_destroy_audio_stream(s2.a5)
            s2.a5 = None

def platform_sound_resume():
    al_restore_default_mixer()
    ALLEGRO_MIXER *mix = al_get_default_mixer()
    if mix:
        al_set_mixer_playing(mix, 1)
    #al_install_audio()
    #al_reserve_samples(8)

    #if streaming:
    #    for LandStream *s in LandArray *streaming:
    #        platform_stream_music(s, s.filename)

def platform_sound_halt():
    ALLEGRO_MIXER *mix = al_get_default_mixer()
    if mix:
        al_set_mixer_playing(al_get_default_mixer(), 0)
    al_set_default_voice(None)
    #al_uninstall_audio()

def platform_stream_new(int samples, fragments,
    float frequency, int bits, channels) -> LandStream *:
    LandStreamPlatform *self
    land_alloc(self)
    LandStream *super = (void *)self

    int chan_conf = 0, depth = 0
    get_params(channels, bits, &chan_conf, &depth)

    super->fragments = fragments
    super->samples = samples
    super->sample_size = al_get_channel_count(chan_conf) * al_get_audio_depth_size(depth);
    self.a5 = al_create_audio_stream(fragments, samples, frequency, depth,
        chan_conf)

    al_attach_audio_stream_to_mixer(self.a5, al_get_default_mixer())

    if not streaming:
        streaming = land_array_new()
    land_array_add(streaming, self)

    return super

def platform_stream_destroy(LandStream *super):
    int i = land_array_find(streaming, super)
    if i >= 0:
        land_array_swap(streaming, i, -1)
        land_array_pop(streaming)

    LandStreamPlatform *self = (void *)super
    al_destroy_audio_stream(self.a5)
    land_free(super)

def platform_stream_buffer(LandStream *super) -> void *:
    LandStreamPlatform *self = (void *)super
    if al_get_available_audio_stream_fragments(self.a5) == 0: return None
    self.fragment = al_get_audio_stream_fragment(self->a5):
    return self.fragment

def platform_stream_fill(LandStream *super):
    LandStreamPlatform *self = (void *)super
    al_set_audio_stream_fragment(self.a5, self->fragment)

def platform_stream_music(LandStream *super, char const *filename,
        bool looping):
    LandStreamPlatform *self = (void *)super
    al_destroy_audio_stream(self.a5)
    self.a5 = al_load_audio_stream(filename,
        super->fragments, super->samples)
    if not self.a5:
        land_log_message("Could not load %s\n", filename)
        return
    al_attach_audio_stream_to_mixer(self.a5, al_get_default_mixer())
    if looping:
        al_set_audio_stream_playmode(self.a5, ALLEGRO_PLAYMODE_LOOP)

def platform_stream_volume(LandStream *super, float volume):
    LandStreamPlatform *self = (void *)super
    if not self.a5:
        return
    al_set_audio_stream_gain(self.a5, volume)

def platform_stream_is_playing(LandStream *super) -> bool:
    LandStreamPlatform *self = (void *)super
    if not self.a5:
        return False
    return al_get_audio_stream_playing(self.a5)

def platform_stream_set_playing(LandStream *super, bool onoff):
    LandStreamPlatform *self = (void *)super
    if not self.a5:
        return
    al_set_audio_stream_playing(self.a5, onoff)
