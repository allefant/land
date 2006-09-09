# Import everything so the complete Land API is available.
# Also the platform independent macros to launch the Land main loop are here.

import global allegro, stdio, stdlib, string, stdarg, math
import main, array, display, runner, random, mouse, keyboard, image
import exception, font, sprite, map, tilegrid, isometric, sprite
import log, color, data, memory, widget, net

macro land_begin() static void _land_main(); int main(int argc, char **argv) {
    land_argc = argc; land_argv = argv; _land_main();
    return 0;} END_OF_MAIN() static void _land_main()
    
macro land_use_main(m) int main(int argc,
    char **argv) {
    land_argc = argc;
    land_argv = argv;
    m();
    return 0;} END_OF_MAIN()

macro land_begin_shortcut(w, h, bpp, hz, flags, init, enter, tick, draw, leave,
    destroy) int main(int argc, char **argv) { land_argc = argc;
    land_argv = argv; land_init();
    shortcut_runner = land_runner_new("shortcut", init, enter, tick, draw,
        leave, destroy);
    land_runner_register(shortcut_runner);
    land_set_display_parameters(w, h, bpp, hz, flags);
    land_set_initial_runner(shortcut_runner);
    land_set_frequency(hz); land_main(); return 0; } END_OF_MAIN()

global int land_argc
global char **land_argv
global LandRunner *shortcut_runner
