#include <land/land.h>

Widget *desktop;
Widget *scrolling1;
Widget *outside;
Widget *list;

static void my_draw(Widget *self)
{
    land_color(1, 1, 0);
    int x, y;
    x = self->box.x;
    for (y = self->box.y; y < self->box.y + self->box.h; y += 8)
    {
        land_line(x + 1 + 0.5, y + 0.5, x + self->box.w - 0.5, y);
    }
    y = self->box.y;
    land_rectangle(x + 0.5, y + 0.5, x + self->box.w - 0.5, y + self->box.h - 0.5);
}

static void init(LandRunner *self)
{
    int i;

    WidgetTheme *theme = widget_theme_new("blue/agup.cfg");

    LandFont *f = land_load_font("../../data/galaxy.ttf", 10);
    land_set_font(f);

    desktop = widget_container_new(NULL, 0, 0, 640, 480);
    desktop->theme = theme;

    /*
    Widget *container2 = widget_container_new(desktop, 100, 100, 100, 100);

    // next 2 lines should be done automatic
    widget_layout_add(desktop, scrolling1);
    widget_layout_add(desktop, container2);

    // instead, could set a flag "horizontal" or "vertical", then simply add new
    // ones and they would be automatically placed, and the size updated
    widget_layout_set_grid(desktop, 2, 1);
    widget_layout_set_grid_position(scrolling1, 0, 0);
    widget_layout_set_grid_position(container2, 1, 0);

    widget_layout(desktop);
    */

#if 0
    scrolling1 = widget_scrolling_new(desktop, 100, 200, 100, 100);

    Widget *container = widget_container_new(desktop, 600, 20, 20, 200);
    Widget *bar = widget_scrollbar_new(container, outside, 1, 600, 20, 20, 20);
#endif

#if 1
    scrolling1 = widget_scrolling_new(desktop, 100, 200, 100, 100);

    outside = widget_box_new(scrolling1, 102, 202, 200, 200);
    widget_create_interface(outside);
    outside->vt->draw = my_draw;
#endif

    Widget *text = widget_text_new(desktop, "Land", 10, 10, 100, 20);

#if 1
    Widget *window = widget_container_new(desktop, 100, 100, 100, 100);
    Widget *mover = widget_mover_new(window, 100, 100, 100, 20);
#endif

//    scrolling1 = widget_scrolling_new(desktop, 100, 200, 100, 100);

/*
    list = widget_list_new(scrolling1, 104, 204, 200, 200);
    widget_text_new(list, "Antelope", 0, 0, 0, 0);
    widget_text_new(list, "Beaver", 0, 0, 0, 0);
    widget_text_new(list, "Chamaelion", 0, 0, 0, 0);
    widget_text_new(list, "Dax", 0, 0, 0, 0);
*/
    /*for (i = 0; i < 10; i++)
    {
        Widget *container = widget_container_new(desktop, 100, 100 + 10 * i, 100, 100);
        widget_layout_set_border(container, 2, 2, 2, 2, 1, 1);
        widget_layout_set_grid(container, 1, 3);

        Widget *mover = widget_mover_new(container, 0, 0, 0, 0);
        widget_layout_add(container, mover);
        widget_layout_set_grid_position(mover, 0, 0);
        widget_layout_set_minimum_size(mover, 16, 16);
        widget_layout_set_shrinking(mover, 0, 1);

        Widget *contents = widget_box_new(container, 0, 0, 0, 0);
        widget_layout_add(container, contents);
        widget_layout_set_grid_position(contents, 0, 1);
        widget_layout_set_minimum_size(contents, 16, 16);

        Widget *status = widget_container_new(container, 0, 0, 0, 0);
        widget_layout_add(container, status);
        widget_layout_set_grid_position(status, 0, 2);
        widget_layout_set_grid(status, 2, 1);
        widget_layout_set_border(status, 2, 2, 2, 2, 1, 1);
        widget_layout_set_shrinking(status, 0, 1);

        Widget *left = widget_container_new(status, 0, 0, 0, 0);
        widget_layout_add(status, left);
        widget_layout_set_grid_position(left, 0, 0);
        widget_layout_set_minimum_size(left, 16, 16);

        Widget *sizer = widget_sizer_new(status, 0, 0, 0, 0);
        widget_layout_add(status, sizer);
        widget_layout_set_grid_position(sizer, 1, 0);
        widget_layout_set_minimum_size(sizer, 16, 16);
        widget_layout_set_shrinking(sizer, 1, 1);
        WIDGET_SIZER(sizer)->target = container;

        widget_layout(container);
    }*/
}

static void tick(LandRunner *self)
{
    if (land_key(KEY_ESC))
        land_quit();

    if (land_key(KEY_LEFT))
        widget_move(list, -1, 0);

    if (land_key(KEY_RIGHT))
        widget_move(list, 1, 0);

    if (land_key(KEY_UP))
        widget_move(list, 0, -1);

    if (land_key(KEY_DOWN))
        widget_move(list, 0, 1);

    desktop->vt->mouse_tick(desktop);
}

static void draw(LandRunner *self)
{
    land_unclip();
    land_clear(0, 0, 0);
    widget_draw(desktop);
    /*land_color(1, 0, 0);
      land_rectangle(scrolling1->box.x - 1.5, scrolling1->box.y - 1.5,
        scrolling1->box.x + scrolling1->box.w + 1.5,
        scrolling1->box.y + scrolling1->box.h + 1.5);
    */
    /*int i, j;
    int x = 1, y = 1;
    for (i = 1; i < 25; i++)
    {
        int ox = x;
        for (j = 1; j < 25; j++)
        {
            Widget *widget = widget_box_new(desktop, x, y, j, i);
            widget_theme_draw(widget);
            widget_del(widget);
            x += j + 1;
        }
        x = ox;
        y += i + 1;
    }*/
}

land_begin_shortcut(640, 480, 32, 60, LAND_WINDOWED | LAND_OPENGL, init, NULL, tick,
        draw, NULL, NULL)

