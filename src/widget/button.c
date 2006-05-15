#ifdef _PROTOTYPE_

typedef struct LandWidgetButton LandWidgetButton;

#include "base.h"

struct LandWidgetButton
{
    LandWidget super;
    unsigned int align : 2; /* 0 = left, 1 = right, 2 = center */
    char *text;
    void (*clicked)(LandWidget *self);
};

#define LAND_WIDGET_BUTTON(widget) ((LandWidgetButton *) \
    land_widget_check(widget, LAND_WIDGET_ID_BUTTON, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "land.h"

LandWidgetInterface *land_widget_button_interface = NULL;

void land_widget_button_draw(LandWidget *base)
{
    LandWidgetButton *self = LAND_WIDGET_BUTTON(base);
    if (!base->no_decoration)
        land_widget_box_draw(base);
    if (self->text)
    {
        int x, y = base->box.y + base->box.it;
        land_widget_theme_color(base);
        switch (self->align)
        {
            case 0:
                x = base->box.x + base->box.il;
                land_text_pos(x, y);
                land_print(self->text);
                break;
            case 1:
                x = base->box.x + base->box.w - base->box.ir;
                land_text_pos(x, y);
                land_print_right(self->text);
                break;
            case 2:
                x = base->box.x + (base->box.w - base->box.il + base->box.ir) / 2;
                land_text_pos(x, y);
                land_print_center(self->text);
                break;
        }
    }
}

void land_widget_button_mouse_tick(LandWidget *base)
{
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base);
    if (!button->clicked) return;
    if (land_mouse_delta_b() & 1)
        if (land_mouse_b() & 1)
            button->clicked(base);
}

void land_widget_button_destroy(LandWidget *base)
{
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base);
    free(button->text);
    land_widget_base_destroy(base);
}

LandWidget *land_widget_button_new(LandWidget *parent, char const *text,
    void (*clicked)(LandWidget *self), int x, int y, int w, int h)
{
    LandWidgetButton *self;

    land_widget_button_interface_initialize();

    land_alloc(self);

    LandWidget *base = &self->super;
    land_widget_base_initialize(base, parent, x, y, w, h);
    base->vt = land_widget_button_interface;
    self->text = strdup(text);
    self->clicked = clicked;
    
    return base;
}

void land_widget_button_interface_initialize(void)
{
    if (land_widget_button_interface) return;

    land_widget_button_interface = land_widget_copy_interface(
        land_widget_base_interface, "button");
    land_widget_button_interface->id |= LAND_WIDGET_ID_BUTTON;
    land_widget_button_interface->destroy = land_widget_button_destroy;
    land_widget_button_interface->draw = land_widget_button_draw;
    land_widget_button_interface->mouse_tick = land_widget_button_mouse_tick;
}
