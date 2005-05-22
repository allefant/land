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

#define land_begin() \
    static void _land_main(void); \
    int main(void) {_land_main(); return 0;} END_OF_MAIN() \
    static void _land_main(void)

#define land_begin_shortcut(w, h, bpp, hz, flags, \
    init, enter, tick, draw, leave, destroy) \
    int main(void) \
    { \
        land_init(); \
        LandRunner *runner = land_runner_register("shortcut", \
            init, enter, tick, draw, leave, destroy); \
        land_set_display_parameters(w, h, bpp, hz, flags); \
        land_set_initial_runner(runner); \
        land_set_frequency(hz); \
        land_main(); \
        return 0; \
    }

#endif /* _PROTOTYPE_ */
