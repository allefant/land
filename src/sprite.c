#ifdef _PROTOTYPE_

typedef struct LandSprite LandSprite;

#include "array.h"
#include "display.h"
#include "grid.h"

land_type(LandSpriteType)
{
    float x, y; /* collision offset in pixel, relative to its position. */
    int w, h; /* collision bounding box. */

    void (*draw)(LandSprite *self, LandView *view);
};

struct LandSprite
{
    float x, y;
    LandSpriteType *type;
};

land_type(LandSpritesGrid)
{
    LandGrid super;
    LandList **sprites; /* 2D-array of sprite lists */
};

#endif /* _PROTOTYPE_ */

#include "sprite.h"
#include "tilegrid.h"

land_array(LandSpriteType);
land_array(LandSprite);
land_array(LandSpritesGrid);

LandGridInterface *land_grid_vtable_sprites;

LandGrid *land_sprites_grid_new(int cell_w, int cell_h, int x_cells, int y_cells)
{
    land_new(LandSpritesGrid, self);
    land_grid_initialize(&self->super, cell_w, cell_h, x_cells, y_cells);
    self->super.vt = land_grid_vtable_sprites;

    self->sprites = calloc(x_cells * y_cells, sizeof *self->sprites);

    return &self->super;
}

static void dummy(LandSprite *self, LandView *view)
{
    float x = self->x + self->type->x - view->scroll_x + view->x;
    float y = self->y + self->type->y - view->scroll_y + view->y;
    land_rectangle(x, y, x + self->type->w,
        y + self->type->h, 1, 0, 0);
}

LandSpriteType *land_spritetype_new(void)
{
    land_new(LandSpriteType, self);
    self->draw = dummy;
    return self;
}

void land_sprite_initialize(LandSprite *self, LandSpriteType *type)
{
    self->type = type;
}

LandSprite *land_sprite_new(LandSpriteType *type)
{
    land_new(LandSprite, self);
    land_sprite_initialize(self, type);
    return self;
}

void land_sprite_show(LandSprite *self)
{

}

void land_sprite_hide(int sprite, int grid)
{

}

static void grid_place(LandSprite *self, LandSpritesGrid *grid)
{
    int tx = self->x / grid->super.cell_w;
    int ty = self->y / grid->super.cell_h;

    land_add_list_data(&grid->sprites[ty * grid->super.x_cells + tx],
        self);
}

void land_sprite_place_into_grid(LandSprite *self, LandGrid *grid, float x, float y)
{
    self->x = x;
    self->y = y;
    grid_place(self, (LandSpritesGrid *)grid);
}

void land_sprite_move(LandSprite *self, float x, float y)
{

}

static void land_sprites_grid_draw_cell(LandSpritesGrid *self, LandView *view, int cell_x, int cell_y, float pixel_x, float pixel_y)
{
    LandList *list = self->sprites[cell_y * self->super.x_cells + cell_x];
    if (list)
    {
        LandListItem *item = list->first;
        while (item)
        {
            LandSprite *sprite = item->data;

            sprite->type->draw(sprite, view);

            item = item->next;
        }
    }
}

void land_sprites_init(void)
{
    land_log_msg("land_sprites_init\n");
    land_alloc(land_grid_vtable_sprites);
    land_grid_vtable_sprites->draw = land_grid_draw_normal;
    land_grid_vtable_sprites->draw_cell = (void *)land_sprites_grid_draw_cell;
}
