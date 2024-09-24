import global land/land
import all_examples

LandRunner *selected
LandFont *font
LandArray *examples
float column_width
int colsize

def _init:
    land_find_data_prefix("data/")
    int size = land_display_height() / 40
    font = land_font_load("URWGothicBook.ttf", size)
    config_all_examples()
    examples = land_array_new()
    auto runners = land_runner_get_all()
    for LandRunner *runner in runners:
        if land_equals(runner.name, "shortcut"): continue
        land_array_add(examples, runner)

def _tick:
    if land_key_pressed(LandKeyEscape):
        if selected:
            selected = None
            land_font_set(font)
            land_set_fps(60)
        else:
            land_quit()
    if land_closebutton():
        land_quit()

    if selected:
        if selected.tick:
            selected.tick(selected)
    else:
        if land_mouse_button_clicked(0):
            int sel = land_mouse_y() // land_line_height() - 2
            int col = land_mouse_x() // column_width
            sel += col * colsize
            selected = land_array_get_or_none(examples, sel)
            if selected and selected.init:
                if not selected.inited:
                    selected.init(selected)
                    selected.inited = True

def _draw:
    land_reset_projection()
    land_reset_transform()
    land_unclip()
    land_render_state(LAND_DEPTH_TEST, False)
    land_font_reset()
    land_thickness(0)
    glDisable(GL_CULL_FACE)
    land_clear(0, 0, 0, 1)
    if selected:
        if selected.draw:
            selected.draw(selected)
    else:
        land_color(1, 1, 1, 1)
        land_text_pos(0, 0)
        land_print("Click example to run it. Escape to return.")
        land_print("")
        float x = 0
        float y = land_text_y_pos()
        colsize = 0
        int i = 0
        column_width = land_text_get_width("long example name")
        for LandRunner *runner in examples:
            land_print(runner.name)
            i += 1
            if land_text_y_pos() + land_line_height() > land_display_height():
                if colsize == 0:
                    colsize = i
                x += column_width
                land_text_pos(x, y)

def config_run_all:
    pass

def main(int argc, char **argv) -> int:
    land_argc = argc
    land_argv = argv
    land_init()
    land_default_display()
    land_callbacks(_init, _tick, _draw, None)
    land_mainloop()
    return land_get_exitcode()
