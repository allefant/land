#ifdef _PROTOTYPE_

typedef struct LandSprite LandSprite;

#include "array.h"
#include "display.h"
#include "grid.h"

land_type(LandSpriteType)
{
    // TODO need those 4 variables?
    /* A sprite does not need a image, so the below variables are needed. */
    float x, y; /* collision offset in pixel, relative to its position. */
    int w, h; /* collision bounding box. */

    LandImage *image;

    void (*draw)(LandSprite *self, LandView *view);
    int (*overlap)(LandSprite *self, LandSprite *with);
};

struct LandSprite
{
    float x, y, angle;
    LandSpriteType *type;
};

land_type(LandSpritesGrid)
{
    LandGrid super; /* 2D-array of sprite lists */
    LandList **sprites;

    /* maximum sprite extents */
    int max_l, max_t, max_r, max_b;
};

#define LAND_SPRITES_GRID(x) ((LandSpritesGrid *)(x))

#endif /* _PROTOTYPE_ */

#include "sprite.h"
#include "tilegrid.h"
#include "pixelmask.h"

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
    float x = self->x - self->type->x - view->scroll_x + view->x;
    float y = self->y - self->type->y - view->scroll_y + view->y;
    land_color(1, 0, 0);
    land_rectangle(x, y, x + self->type->w,
        y + self->type->h);
}

static void dummy_image(LandSprite *self, LandView *view)
{
    float x = self->x - view->scroll_x + view->x;
    float y = self->y - view->scroll_y + view->y;
    land_image_draw(self->type->image, x, y);
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

int land_sprite_overlap_pixelperfect(LandSprite *self, LandSprite *other) {
    return land_image_overlaps(self->type->image, self->x, self->y, self->angle,
        other->type->image, other->x, other->y, other->angle);
}

LandList *land_sprites_grid_overlap(LandSprite *self, LandGrid *sprites_grid)
{
    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid);
    LandList *retlist = NULL;
    float l = self->x - self->type->x - grid->max_r;
    float t = self->y - self->type->y - grid->max_b;
    float r = self->x - self->type->x + self->type->w + grid->max_l;
    float b = self->y - self->type->y + self->type->h + grid->max_t;
    int tl = l / grid->super.cell_w;
    int tt = t / grid->super.cell_h;
    int tr = r / grid->super.cell_w;
    int tb = b / grid->super.cell_h;
    int tx, ty;
    if (tl < 0) tl = 0;
    if (tt < 0) tt = 0;
    if (tr >= grid->super.x_cells) tr = grid->super.x_cells - 1;
    if (tb >= grid->super.y_cells) tb = grid->super.y_cells - 1;
    for (ty = tt; ty <= tb; ty++)
    {
        for (tx = tl; tx <= tr; tx++)
        {
            LandList *list = grid->sprites[ty * grid->super.x_cells + tx];
            if (list)
            {
                LandListItem *item = list->first;
                while (item)
                {
                    LandSprite *other = item->data;
                    if (self->type->overlap(self, other))
                        land_add_list_data(&retlist, other);
                    item = item->next;
                }
            }
        }
    }
    return retlist;
}

static void grid_place(LandSprite *self, LandSpritesGrid *grid)
{
    int tx = self->x / grid->super.cell_w;
    int ty = self->y / grid->super.cell_h;

    if (self->type->x > grid->max_l)
        grid->max_l = self->type->x;
    if (self->type->w - self->type->x > grid->max_r)
        grid->max_r = self->type->w - self->type->x;
    if (self->type->y > grid->max_t)
        grid->max_t = self->type->y;
    if (self->type->h - self->type->y > grid->max_b)
        grid->max_b = self->type->h - self->type->y;

    //FIXME: need proper sprites container, without allocating a new ListItem
    land_add_list_data(&grid->sprites[ty * grid->super.x_cells + tx],
        self);
}

static void grid_unplace(LandSprite *self, LandSpritesGrid *grid)
{
    int tx = self->x / grid->super.cell_w;
    int ty = self->y / grid->super.cell_h;

    //FIXME: need proper sprites container, without iterating the whole list and
    //de-allocating the ListItem
    land_remove_list_data(&grid->sprites[ty * grid->super.x_cells + tx],
        self);
}

void land_sprite_place_into_grid(LandSprite *self, LandGrid *grid, float x, float y)
{
    self->x = x;
    self->y = y;
    grid_place(self, (LandSpritesGrid *)grid);
}

void land_sprite_move(LandSprite *self, LandGrid *grid, float x, float y)
{
    grid_unplace(self, (LandSpritesGrid *)grid);
    self->x += x;
    if (self->x < 0) self->x = 0;
    if (self->x >= grid->cell_w * grid->x_cells)
        self->x = grid->cell_w * grid->x_cells - 1;

    self->y += y;
    if (self->y < 0) self->y = 0;
    if (self->y >= grid->cell_h * grid->y_cells)
        self->y = grid->cell_h * grid->y_cells - 1;

    grid_place(self, (LandSpritesGrid *)grid);
}

static void land_sprites_grid_draw_cell(LandSpritesGrid *self, LandView *view,
    int cell_x, int cell_y, float pixel_x, float pixel_y)
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

LandSpriteType *land_spritetype_new_with_image(LandImage *image)
{
    land_new(LandSpriteType, self);
    self->draw = dummy_image;
    self->overlap = land_sprite_overlap_pixelperfect;
    self->image = image;
    self->x = image->x;
    self->y = image->y;
    self->w = image->bitmap->w;
    self->h = image->bitmap->h;
    return self;
}
