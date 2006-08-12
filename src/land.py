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
#include "memory.h"

#include "widget.h"

extern LandRunner *shortcut_runner;
extern int land_argc;
extern char **land_argv;

#define land_begin() \
    static void _land_main(void); \
    int main(int argc, char **argv) {land_argc = argc; land_argv = argv; \
        _land_main(); return 0;} END_OF_MAIN() \
    static void _land_main(void)

#define land_begin_shortcut(w, h, bpp, hz, flags, \
    init, enter, tick, draw, leave, destroy) \
    int main(int argc, char **argv) \
    { \
        land_argc = argc; land_argv = argv; \
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

int land_argc;
char **land_argv;

LandRunner *shortcut_runner;
