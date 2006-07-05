#ifdef _PROTOTYPE_

typedef struct LandWidgetPanel LandWidgetPanel;

struct LandWidgetPanel
{
    LandWidgetContainer super;
};

#define LAND_WIDGET_PANEL(widget) ((LandWidgetPanel *) \
    land_widget_check(widget, LAND_WIDGET_ID_PANEL, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "land.h"
#include "widget/panel.h"

LandWidgetInterface *land_widget_panel_interface;

void land_widget_panel_initialize(LandWidget *base,
    LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetPanel *self = (LandWidgetPanel *)base;
    land_widget_panel_interface_initialize();
    LandWidgetContainer *super = &self->super;
    land_widget_container_initialize(&super->super, parent, x, y, w, h);
    base->vt = land_widget_panel_interface;
}

LandWidget *land_widget_panel_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetPanel *self;
    land_alloc(self);
    land_widget_panel_initialize((LandWidget *)self, parent, x, y, w, h);
    return LAND_WIDGET(self);
}

void land_widget_panel_add(LandWidget *base, LandWidget *add)
{
    land_widget_container_add(base, add);

    land_widget_layout_inhibit(base);

    land_widget_layout_set_grid_position(add, 0, 0);
    land_widget_layout_set_grid(base, 1, 1);

    land_widget_layout_add(base, add);

    land_widget_layout_enable(base);

    land_widget_layout_adjust(base, 1, 1);
}

void land_widget_panel_interface_initialize(void)
{
    if (land_widget_panel_interface) return;
    land_widget_container_interface_initialize();
    land_widget_panel_interface = land_widget_copy_interface(
        land_widget_container_interface, "panel");
    land_widget_panel_interface->id |= LAND_WIDGET_ID_PANEL;
    land_widget_panel_interface->add = land_widget_panel_add;
}
