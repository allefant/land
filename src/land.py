"""
![Land!](logo.png)

## the name

It has no special meaning, it's just that in computer games, you make
virtual worlds or lands - and that inspired it as use as name for this.
The only limits of this land should be your imagination, not programming
language obstacles. But if you insist, it could also be a recursive
acronym for "Land All New Design".

## history

Well, I really started working on this version only some days ago. But I
made a library called "land", with the very same goals, about 10-20 years
ago. I actually recovered some files of that, but they require a program
called TASM to work. I actually found a copy of that, and tried to
compile it in dosbox, but still, it wouldn't work. Not that the result
would have been interesting for anyone but me :)

## what it is

Land is, currently, just a simple framework to assist in creating games,
which will work under Windows, Linux and OSX. As well as some others,
basically everything Allegro/SDL/OpenGL can get to run (currently only
Allegro). It doesn't do a lot, just handle a basic game loop for you.
Some may not want this, since it takes control away. But for beginners,
it may make things somewhat simpler. And especially, and that's the only
thing I care about, for me.

## features/limitations
- Written in C, preprocessed by a Python-like syntax.

- Automated build process using scons.

- Load images as single files, from directories, from .zip files, from
  fixed-grid/transparent/color-keyed sheets.

- Free-form multi-layer tilemaps. The layers use no fixed tile-layout,
  you can place there what and where you want. (Of course this includes
  classic tiles.)

- Pixel-perfect collision between tilemap-sprite and sprite-sprite,
  efficient for 1000ds of objects and huge maps. (The algorithm is to
  first check a grid-cash for proximity, then do a bounding-box check,
  then pixel-perfect with pre-generated bit-masks.)

- Parallax scrolling with arbitrary amount of layers. Define some of the
  tilemap layers to be parallax layers - scrolling is handled by Land.

## source code

Normally, the split into .c/.cpp and .h files is not a problem, either you
work out the API first in he .h and then implement, or write first the
implementation then derive the .h. But in two cases it is very bad: Designing
a new library, and maintaining a library. In the former, it means you need
to make every interface change at multiple locations. In the latter case it
means, you end up with en entangled mess of headers all over the place.

Therefore, in Land, I ended up using preprocessed files from which .c and .h
files are auto-generated. That way, the source always stays clean and
managable. Looking at the changes of the build process would show how hard it
was to end up at the current system (but a lot of that happened before the code
was stable enough to move to SVN).

## inheritance and polymorphism
What does the technical inplementation of Land look like, given it is
implemented in C? Well, polymorphism is done by using VTables, similar to e.g.
the Allegro drivers. Inheritance is done by manual aggregation (along with
VTables).

For example, let's say, you want to use a tilemap, but have your own drawing
function called for each tile. Simple create a LandGridInterface object,
replace the ->draw_cell method with your own, and replace the ->vt member of your
LandGrid object with your own LandGridInterface.

TODO: Maybe a macro, something like:

LandGridInterface *my_grid_vtable =
    land_override(land_grid_vtable_normal, cell_draw, my_cell_draw);

## user data

Instead of inheriting your own types, it is much easier to simply attach data to
land types. For example:

int index = land_attach_data(sprite, "mydata", mydata);

or

int index = land_attach_data(sprite, NULL, mydata);

In both cases, you can retrieve the data with:

mydata = land_retrieve_data(sprite, index);

In the first case, also with:

mydata = land_retrieve_named_data(sprite, "mydata")

## containers

  LandList - a doubly linked list of items. Fast insertion and deletion of
  items.

  LandArray - a dynamically growing array. The number of used and allocated
  elements can differ, so can allocate items in advance, or not de-allocate
  items in case more are added shortly.
  
  LandQueue - like an array but the items are always kept sorted. Useful
  for something like a priority queue or if you want to (heap-)sort some
  other container.
  
  LandHash - a mapping of strings to the data. Useful if there are many strings
  to look up, in which case this is faster than looping through a list/array.

## maps, layers, tiles, sprites..

  One question still is.. what to do about maximum sprite size? Two brute force
  approaches:
- render as much overlap cells that the biggest sprite would be catched
  This leaves the solution very high-level.. simply draw a bigger area.
  Drawback is possibly drawing more than necessary most of the time.
- add a sprite to every cell it covers.. this is somewhat more complicated,
  but can have other advantages as well, like easy collision detection

  Another solution would be to have a maximum size of the cell size in each
  layer - then simply can group large sprites into a layer with a big enough
  cell size. This also would deal with collision detection - a sprite simply can
  never be outside of its cell and the adjacent ones.

## graphics primitives

You can directly use all of Allegro's API, as well as OpenGL. Additionally, with
the time, Land got it's own graphics primitives:

land_color(r, g, b) Sets the color
land_transparency(a) Sets transparency
land_thickness(t) Sets thickness of lines/pixels/rectangles
land_line(x, y, x_, y_) Like the one in Allegro
land_move_to(x, y) Sets the cursor position
land_line_to(x, y) Draws from the current position towards x/y, but not on x/y
itself, and sets the cursor to x/y.
land_line_end(x, y) Like land_line_to, but doesn't change the cursor, and also
draws on x/y.
land_pixel(x, y) Draws a single pixel.

land_clip(x, y, w, h)

How can you draw not to the screen, but into an image?

land_target(image)

So far, the state maintained by a LandDisplay thus is:

- color_r, color_g, color_b, color_a
- thickness
- font
- text_x, text_y
- target
- clip_x, clip_y, clip_w, clip_h

## The land song

+ lalalala-land
+ Land is "Land All New Design"
+ so new so shiny so well designed
+ lalalala-land
+ Land in sight!
+ lalalala-land
+ lalalalalala-land
+ lal-land

(this chapter is all the progress I made when I tried to work on it drunk)
"""

# Import everything so the complete Land API is available.
# Also the platform independent macros to launch the Land main loop are here.

import common
import global stdio, stdlib, string, stdarg
import global stdbool
global *** "define" y1 libc_y1
global *** "define" yn libc_yn
import global math
global *** "undef" y1
global *** "undef" yn

import config
import main, array, display, runner, random, mouse, keyboard, image
import triangles, shader
import exception, font, sprite, map, tilegrid, isometric, sprite
import log, color, data, mem, widget, net, queue, sound, buffer, ini
import file, thread, protobuf
import joystick
import atlas
import yaml
import noise

import land/allegro5/a5_opengl

static str _version = "1.0.0"

def land_version -> char const *:
    return _version

static LandArray *exit_functions
static int _exitcode
   
macro land_use_main(m):
    def main(int argc, char **argv) -> int:
        land_argc = argc
        land_argv = argv
        m()
        land_log_message("Return code is %d.\n", land_get_exitcode())
        return land_get_exitcode()

macro land_begin_shortcut(w, h, hz, flags, init, enter, tick, draw,
    leave, destroy):
    def main(int argc, char **argv) -> int:
        land_argc = argc
        land_argv = argv
        land_init()
        shortcut_runner = land_runner_new("shortcut",
            (void *)init, (void *)enter, (void *)tick, (void *)draw,
            (void *)leave, (void *)destroy)
        land_runner_register(shortcut_runner)
        land_set_display_parameters(w, h, flags)
        land_set_initial_runner(shortcut_runner)
        land_set_fps(hz)
        land_mainloop()
        land_log_message("Return code is %d.\n", land_get_exitcode())
        return land_get_exitcode()

def land_without_main(void (*cb)(void)):
    platform_without_main(cb)

def land_set_exitcode(int code):
    _exitcode = code

def land_get_exitcode() -> int:
    return _exitcode

def land_exit_function(void (*function)(void)):
    land_array_add_data(&exit_functions, function)

def land_exit_functions():
    int i, n = land_array_count(exit_functions)
    for i = n - 1 while i >= 0  with i--:
        void (*function)(void) = land_array_get_nth(exit_functions, i)
        function()
    land_array_destroy(exit_functions)

def land_wait(double seconds):
    platform_wait(seconds)

typedef void (VoidFunction)(void)

def land_callbacks(VoidFunction *init, VoidFunction *tick,
        VoidFunction *draw, VoidFunction *done):
    shortcut_runner = land_runner_new("shortcut",
            (void *)init, None, (void *)tick, (void *)draw,
            None, (void *)done)
    land_runner_register(shortcut_runner)
    land_set_initial_runner(shortcut_runner)

global int land_argc
global char **land_argv
global LandRunner *shortcut_runner
