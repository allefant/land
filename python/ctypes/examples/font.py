#!/usr/bin/env python3
import sys, array
from math import *
sys.path.append("..")
from land import *

def game_init(self):
    global gradient
    global big
    global small
    global tiny
    global truecolor
    global paletted
    global muli

    big = land_font_load(b"../../data/galaxy.ttf", 60)
    small = land_font_load(b"../../data/galaxy.ttf", 30)
    tiny = land_font_load(b"../../data/galaxy.ttf", 12)
    truecolor = land_font_load(b"../../data/truecolor.tga", 0)
    paletted = land_font_load(b"../../data/paletted.tga", 0)
    muli = land_font_load(b"../../data/Muli-Regular.ttf", 14)
    # builtin = land_allegro_font()
    
    gradient = land_image_new(4, 4)
    rgba = (c_ubyte * 64)(
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 
        255, 255, 000, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 000, 255,
        000, 255, 255, 255, 000, 255, 255, 255, 000, 255, 255, 255, 000, 255, 255, 255, 
        000, 000, 255, 255, 000, 000, 255, 255, 000, 000, 255, 255, 000, 000, 255, 255,
        )
    land_image_set_rgba_data(gradient, rgba)

def game_tick(self):
    if land_key(LandKeyEscape):
        land_quit()

def game_draw(self):
    w = land_display_width()
    h = land_display_height()
    land_clear(0, 1, 0, 1)
    xy = (c_float * 8)(0, 0, w, 0, w, h, 0, h)
    uv = (c_float * 8)(1, 1, 3, 1, 3, 3, 1, 3)
    land_color(1, 1, 1, 1)
    land_textured_polygon(gradient, 4, xy, uv)

    land_font_set(muli)
    land_color(0, 0, 0, 1)
    land_text_pos(w / 2, land_font_height(muli))
    s1 = b"Tulip Rose Lily Daffodil Iris Orchid Narcissus Violet"
    n = len(s1) + 1
    land_print_center(b"%s", s1)
    tx = w / 2 - land_text_get_width(s1) / 2
    ty = land_font_height(muli) * 2
    for i in range(n):
        c = land_color_hsv(i * 360 / n + land_get_time() * 120, 1, 1)
        tw = land_text_get_width(s1[:i])
        land_color(c.r, c.g, c.b, 1)        
        land_text_pos(tx + tw, ty)
        land_print(s1[i:i + 1], b"")

    land_font_set(big)
    x = w / 2
    y = h / 2 - land_font_height(big) / 2
    alpha = 0.5 if int(land_get_time()) & 1 else 0
    land_color(alpha, alpha, 0, alpha)
    land_reset_transform()
    land_rotate(sin(land_get_time() * pi * 0.5) * pi / 4)
    land_translate(x, y)
    land_line(0 - 3, 0, 0 + 3, 0)
    land_line(0, 0 - 3, 0, 0 + 3)
    
    for i in range(21):
        land_reset_transform()
        land_rotate(sin(land_get_time() * pi * 0.5) * pi / 4 - pi / 4)
        land_rotate(pi / 2 * i / 20)
        land_translate(x, y)
        land_line(0, 0.02 * h, 0, h * 0.35)

    land_reset_transform()
    land_color(0, 0, 1, 1)
    land_text_pos(x, y)
    land_print_center(b"%s", b"Land Fonts")

    land_font_set(small)
    land_color(0, 0, 0, 1)
    land_print_center(b"%s", b"font example")

    land_font_set(tiny)
    land_color(0, 0, 0, 1)
    land_print_center(b"%s", b"Demonstrates use of different fonts accessible with Land.")
    land_print_center(b"%s", b"And shows how to use the text cursor for positioning.")

    land_font_set(truecolor)
    land_color(1, 1, 1, 1)

    land_reset_transform()
    land_translate(0, h * 0.35)
    land_rotate(sin(land_get_time() * pi * 0.5) * pi / 4)
    land_translate(x, y)
    land_text_pos(0, 0)
    land_print_center(b"%s", b"Truecolor")

    s = 0.6 + 0.5 * sin(land_get_time() * pi)
    t = land_get_time()
    a = fmod((t + sin(t)) * 180, 360) * pi / 180

    land_reset_transform()
    land_font_set(paletted)
    land_scale(s, s)
    land_rotate(a)
    land_translate(land_display_width() / 4, 2 * land_display_height() / 5)
    land_color(0, 1, 0, 1)
    land_text_pos(0, -30)
    land_print_center(b"%s", b"paletted")

    land_reset_transform()
    land_font_set(paletted)
    land_scale(s, s)
    land_rotate(-a)
    land_translate(land_display_width() * 0.75, 2 * land_display_height() / 5)
    land_color(1, 0, 0, 1)
    land_text_pos(0, -30)
    land_print_center(b"%s", b"paletted")
    
    land_reset_transform()

def my_main():
    land_init()
    land_set_display_parameters(640, 480,
        LAND_WINDOWED | LAND_OPENGL | LAND_MULTISAMPLE | LAND_ANTIALIAS)
    game_runner = land_runner_new(b"font example",
        CFUNCTYPE(None, LP_LandRunner)(game_init),
        None,
        CFUNCTYPE(None, LP_LandRunner)(game_tick),
        CFUNCTYPE(None, LP_LandRunner)(game_draw),
        None,
        None)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(my_main)
