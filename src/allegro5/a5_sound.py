import global allegro5/allegro5

import land/sound, land/mem
static import global allegro5/acodec
static import global allegro5/kcm_audio

static class LandSoundPlatform:
    LandSound super
    ALLEGRO_SAMPLE *a5
    ALLEGRO_SAMPLE_ID last_playing

LandSound *def platform_sound_load(char const *filename):
    LandSoundPlatform *self
    land_alloc(self)
    self->a5 = al_load_sample(filename)
    self->super.filename = land_strdup(filename)
    return (void *)self

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
    land_free(s->filename)
    land_free(s)

def platform_sound_init():
    al_install_audio(ALLEGRO_AUDIO_DRIVER_AUTODETECT)
    al_reserve_samples(100)

def platform_sound_exit():
    pass
