#ifdef _PROTOTYPE_

typedef struct LandWidgetPanel LandWidgetPanel;

struct LandWidgetPanel
{
    LandWidgetContainer super;
};

#define LAND_WIDGET_PANEL(widget) ((LandWidgetList *) \
    land_widget_check(widget, LAND_WIDGET_ID_PANEL, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "land.h"
#include "widget/panel.h"

LandWidgetInterface *land_widget_panel_interface;

void land_widget_panel_initialize(LandWidgetPanel *self,
    LandWidget *parent, int x, int y, int w, int h)
{
   land_widget_panel_interface_initialize();
   LandWidgetContainer *super = &self->super;
   land_widget_container_initialize(super, parent, x, y, w, h);
   LAND_WIDGET(self)->vt = land_widget_panel_interface;
}

LandWidget *land_widget_panel_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetPanel *self = calloc(1, sizeof *self);
    land_widget_panel_initialize(self, parent, x, y, w, h);
    return LAND_WIDGET(self);
}

void land_widget_panel_interface_initialize(void)
{
    if (land_widget_panel_interface) return;
    land_widget_panel_interface = land_widget_copy_interface(
        land_widget_container_interface, "panel");
    land_widget_panel_interface->id |= LAND_WIDGET_ID_PANEL;
}
