#ifdef _PROTOTYPE_

typedef struct LandWidgetBoard LandWidgetBoard;

struct LandWidgetBoard
{
    LandWidgetContainer super;
};

#define LAND_WIDGET_BOARD(widget) ((LandWidgetBoard *) \
    land_widget_check(widget, LAND_WIDGET_ID_BOARD, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "land.h"
#include "widget/board.h"

LandWidgetInterface *land_widget_board_interface;

void land_widget_board_initialize(LandWidget *base,
    LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetBoard *self = (LandWidgetBoard *)base;
    land_widget_board_interface_initialize();
    LandWidgetContainer *super = &self->super;
    land_widget_container_initialize(&super->super, parent, x, y, w, h);
    base->vt = land_widget_board_interface;
}

LandWidget *land_widget_board_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetBoard *self;
    land_alloc(self);
    land_widget_board_initialize((LandWidget *)self, parent, x, y, w, h);
    return LAND_WIDGET(self);
}

void land_widget_board_add(LandWidget *base, LandWidget *add)
{
    land_widget_container_add(base, add);
}

void land_widget_board_interface_initialize(void)
{
    land_widget_container_interface_initialize();
    land_widget_board_interface = land_widget_copy_interface(
        land_widget_container_interface, "board");
    land_widget_board_interface->id |= LAND_WIDGET_ID_BOARD;
    land_widget_board_interface->add = land_widget_board_add;
}