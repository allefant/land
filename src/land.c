#ifdef _PROTOTYPE_
#include <allegro.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>

#include "main.h"
#include "array.h"
#include "display.h"
#include "runner.h"
#include "random.h"
#include "mouse.h"
#include "keyboard.h"
#include "image.h"
#include "exception.h"
#include "font.h"
#include "sprite.h"
#include "map.h"
#include "tilegrid.h"
#include "isometric.h"
#include "sprite.h"
#include "log.h"
#include "color.h"
#include "data.h"

#include "widget.h"

extern LandRunner *shortcut_runner;

#define land_begin() \
    static void _land_main(void); \
    int main(void) {_land_main(); return 0;} END_OF_MAIN() \
    static void _land_main(void)

#define land_begin_shortcut(w, h, bpp, hz, flags, \
    init, enter, tick, draw, leave, destroy) \
    int main(void) \
    { \
        land_init(); \
        shortcut_runner = land_runner_new("shortcut", \
            init, enter, tick, draw, leave, destroy); \
        land_runner_register(shortcut_runner); \
        land_set_display_parameters(w, h, bpp, hz, flags); \
        land_set_initial_runner(shortcut_runner); \
        land_set_frequency(hz); \
        land_main(); \
        return 0; \
    } \
    END_OF_MAIN()

#endif /* _PROTOTYPE_ */

#include "land.h"

static LandDisplay *_global_image_shortcut_display = NULL;
static LandImage *_global_image = NULL;
static int nested = 0;

LandRunner *shortcut_runner;

void land_set_image_display(LandImage *image)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(_global_image_shortcut_display);
    if (nested)
    {
        land_exception("land_set_image_display cannot be nested");
    }
    if (!_global_image_shortcut_display)
    {
        _global_image_shortcut_display = land_display_image_new(image, 0);
    }
    else
    {
        self->bitmap = image->memory_cache;
        self->super.w = land_image_width(image);
        self->super.h = land_image_height(image);
        self->super.bpp = bitmap_color_depth(image->memory_cache);
    }
    _global_image = image;
    land_display_select(_global_image_shortcut_display);
}

void land_unset_image_display(void)
{
    land_display_unselect();
    land_image_prepare(_global_image);
    _global_image = NULL;
}
