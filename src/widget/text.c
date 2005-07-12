#ifdef _PROTOTYPE_

typedef struct WidgetText WidgetText;

#include "widget/base.h"

struct WidgetText
{
    Widget super;
    char *text;
};

#define WIDGET_TEXT(widget) ((WidgetText *)widget)

#endif /* _PROTOTYPE_ */

#include "land.h"

WidgetInterface *widget_text_interface = NULL;

void widget_text_draw(Widget *base)
{
    WidgetText *self = WIDGET_TEXT(base);
    widget_box_draw(base);
    land_color(0, 0.5, 0);
    land_filled_rectangle(base->box.x, base->box.y,
        base->box.x + base->box.w, base->box.y + base->box.h);
    if (self->text)
    {
        int x = base->box.x + base->box.il + 1;
        int y = base->box.y + base->box.it + 1;
        land_text_color(0, 1, 0, 1);
        land_text_pos(x, y);
        land_print(self->text);
    }
}

Widget *widget_text_new(Widget *parent, char const *text, int x, int y, int w, int h)
{
    WidgetText *self;
    if (!widget_text_interface)
        widget_text_interface_initialize();
    land_alloc(self);
    Widget *base = WIDGET(self);
    widget_base_initialize(base, parent, x, y, w, h);
    base->vt = widget_text_interface;
    self->text = strdup(text);
    return base;
}

void widget_text_interface_initialize(void)
{
    land_alloc(widget_text_interface);
    memcpy(widget_base_interface, widget_text_interface,
        sizeof *widget_base_interface);
    widget_text_interface->name = "text";
    widget_text_interface->draw = widget_text_draw;
}

