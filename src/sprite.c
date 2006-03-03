#ifdef _PROTOTYPE_

typedef struct LandSprite LandSprite;
typedef struct LandSpriteWithImage LandSpriteWithImage;
typedef struct LandSpriteAnimated LandSpriteAnimated;

typedef struct LandSpriteType LandSpriteType;
typedef struct LandSpriteTypeImage LandSpriteTypeImage;
typedef struct LandSpriteTypeAnimation LandSpriteTypeAnimation;
typedef struct LandSpriteTypeWithImage LandSpriteTypeWithImage;

typedef struct LandSpritesGrid LandSpritesGrid;

#define LAND_SPRITE(_) ((LandSprite *)(_))
#define LAND_SPRITE_ANIMATED(_) ((LandSpriteAnimated *)(_))
#define LAND_SPRITE_TYPE(_) ((LandSpriteType *)(_))
#define LAND_SPRITE_TYPE_IMAGE(_) ((LandSpriteTypeImage *)(_))

#include "array.h"
#include "display.h"
#include "grid.h"
#include "animation.h"

struct LandSpriteType
{
    // TODO: Sprites may have dynamic dimensions. There should be a vtable
    // entry to query the current dimensions, which is used by the sprites
    // grid.

    /* Dimensions of the sprite inside the grid.
     * If the sprite is on sx/sy, then collision is checked in the rectangle
     * (sx - x, sy - y, sx - x + w, sy - y + h)
     * 
     * Note: This is independent of sprite-sprite collision. But Sprite-sprite
     * collision only will be performed on sprites who overlap in the grid.
     */
    float x, y;
    int w, h;

    /* How to draw sprites of this type. */
    void (*draw)(LandSprite *self, LandView *view);
    /* Sprite-sprite collision detection. */
    int (*overlap)(LandSprite *self, LandSprite *with);

    /* Identification of this sprite type. */
    char const *name;
};

/* Each sprite of this type has its own image. */
struct LandSpriteTypeWithImage
{
    LandSpriteType super;
};


/* All sprites of this type share the same image. */
struct LandSpriteTypeImage
{
    LandSpriteType super;
    LandImage *image;
};

/* All sprites of this type share the same animation. */
struct LandSpriteTypeAnimation
{
    LandSpriteTypeImage super;
    LandAnimation *animation;
};

/* A simple sprite, with just a position and (optional) rotation. */
struct LandSprite
{
    float x, y, angle;
    LandSpriteType *type;
};

/* A sprite with a dynamic image, i.e. each sprite has its own image,
 * independent of its type.
 */
struct LandSpriteWithImage
{
    LandSprite super;
    LandImage *image;
};

/* A specialized sprite, who controls its current image with a frame number. */
struct LandSpriteAnimated
{
    LandSprite super;
    int frame;
    float sx, sy;
};

struct LandSpritesGrid
{
    LandGrid super; /* 2D-array of sprite lists */
    LandList **sprites;

    /* Maximum sprite extents. This is the maximum values of the x/y/w/h of
     * the sprite type above, relative to the sprite position.
     * E.g. if a sprite has: (5, 5, 20, 20), then the max values would be
     * 5, 5, 15, 15, since a sprite on sx/sy could collide with anything
     * overlapping (sx - 5, sy - 5, sx + 15, sy + 15).
     */
    int max_l, max_t, max_r, max_b;
};

#define LAND_SPRITES_GRID(x) ((LandSpritesGrid *)(x))

#endif /* _PROTOTYPE_ */

#include "sprite.h"
#include "tilegrid.h"
#include "pixelmask.h"

LandGridInterface *land_grid_vtable_sprites;

LandGrid *land_sprites_grid_new(int cell_w, int cell_h, int x_cells, int y_cells)
{
    LandSpritesGrid *self;
    land_alloc(self);
    land_grid_initialize(&self->super, cell_w, cell_h, x_cells, y_cells);
    self->super.vt = land_grid_vtable_sprites;

    self->sprites = calloc(x_cells * y_cells, sizeof *self->sprites);

    return &self->super;
}

static void dummy(LandSprite *self, LandView *view)
{
    float x = self->x - self->type->x - view->scroll_x + view->x;
    float y = self->y - self->type->y - view->scroll_y + view->y;
    land_color(1, 0, 0, 1);
    land_rectangle(x, y, x + self->type->w,
        y + self->type->h);
}

static void dummy_image(LandSprite *self, LandView *view)
{
    float x = self->x - view->scroll_x + view->x;
    float y = self->y - view->scroll_y + view->y;
    land_image_draw_rotated(LAND_SPRITE_TYPE_IMAGE(self->type)->image, x, y,
        self->angle);
    //if (self->type->image->mask)
    //    land_image_debug_pixelmask(self->type->image, x, y, 0);
}

static void dummy_animation(LandSprite *self, LandView *view)
{
    LandSpriteTypeAnimation *animation = (LandSpriteTypeAnimation *)self->type;
    LandSpriteAnimated *animated = (LandSpriteAnimated *)self;
    float x = self->x - view->scroll_x + view->x;
    float y = self->y - view->scroll_y + view->y;
    LandImage *image = land_animation_get_frame(animation->animation,
        animated->frame);
    land_image_draw_scaled_rotated(image, x, y, animated->sx, animated->sy,
        self->angle);
    //if (animation->super.image->mask)
    //    land_image_debug_pixelmask(animation->super.image, x, y, 0);
}

void land_sprite_initialize(LandSprite *self, LandSpriteType *type)
{
    self->type = type;
}

LandSprite *land_sprite_new(LandSpriteType *type)
{
    if (!ustrcmp(type->name, "animation"))
        return land_sprite_animated_new(type);

    LandSprite *self;
    land_alloc(self);
    land_sprite_initialize(self, type);
    return self;
}

LandSprite *land_sprite_with_image_new(LandSpriteType *type, LandImage *image)
{
    LandSpriteWithImage *self;
    land_alloc(self);
    land_sprite_initialize(LAND_SPRITE(self), type);
    self->image = image;
    return LAND_SPRITE(self);
}

void land_sprite_animated_initialize(LandSpriteAnimated *self,
    LandSpriteType *type)
{
    land_sprite_initialize(LAND_SPRITE(self), type);
    self->sx = 1;
    self->sy = 1;
}

LandSprite *land_sprite_animated_new(LandSpriteType *type)
{
    LandSpriteAnimated *self;
    land_alloc(self);
    land_sprite_animated_initialize(LAND_SPRITE_ANIMATED(self), type);
    return LAND_SPRITE(self);
}

void land_sprite_del(LandSprite *self)
{
    land_free(self);
}

void land_sprite_destroy(LandSprite *self)
{
    land_sprite_del(self);
}


void land_sprite_show(LandSprite *self)
{

}

void land_sprite_hide(int sprite, int grid)
{

}

/* Given to sprites who have a type LandSpriteTypeImage, do a pixel overlap
 * test, and return 0 if they don't overlap.
 */
int land_sprite_overlap_pixelperfect(LandSprite *self, LandSprite *other) {
    return land_image_overlaps(LAND_SPRITE_TYPE_IMAGE(self->type)->image,
    self->x, self->y, self->angle,
    LAND_SPRITE_TYPE_IMAGE(other->type)->image,
    other->x, other->y, other->angle);
}

/* Return a list of all sprites overlapping the sprite in the given grid.
 * The sprite itself is not returned.
 * Note that this only works if all sprites in the grid have compatible
 * overlapping, e.g. if the sprite does a pixel-overlap test, then all other
 * sprites must have a pixel mask, or if it does a bounding circle test, then
 * all other sprites must have a bounding circle.
 */
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
                    if (other != self)
                        if (self->type->overlap(self, other))
                            land_add_list_data(&retlist, other);
                    item = item->next;
                }
            }
        }
    }
    return retlist;
}

/* Return a list of all sprites in the grid, which are inside the given circle
 * (in pixels).
 */
LandList *land_sprites_grid_get_circle(LandGrid *sprites_grid, float x, float y,
    float radius)
{
    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid);
    LandList *retlist = NULL;
    float l = x - radius;
    float t = y - radius;
    float r = x + radius;
    float b = y + radius;
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
                    float dx = other->x - x;
                    float dy = other->y - y;
                    if (dx + dx + dy * dy < radius * radius)
                    {
                        land_add_list_data(&retlist, other);
                    }
                    item = item->next;
                }
            }
        }
    }
    return retlist;
}

/* Return a list of all sprites in the given rectangle.
 */
LandList *land_sprites_grid_get_rectangle(LandGrid *sprites_grid,
    float l, float t, float r, float b)
{
    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid);
    LandList *retlist = NULL;
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
                    land_add_list_data(&retlist, other);
                    item = item->next;
                }
            }
        }
    }
    return retlist;
}


/* Return a list of all sprites in the given view and overlap. The overlap
 * increases when negative for t and l and positive for r and l.
 */
LandList *land_sprites_grid_get_in_view(LandGrid *sprites_grid, LandView *view,
    float l, float t, float r, float b)
{
    l += view->scroll_x + view->x;
    t += view->scroll_y + view->y;
    r += view->scroll_x + view->x + view->w;
    b += view->scroll_y + view->y + view->h;
    return land_sprites_grid_get_rectangle(sprites_grid, l, t, r, b);
}

static void grid_place(LandSprite *self, LandSpritesGrid *grid)
{
    int tx = self->x / grid->super.cell_w;
    int ty = self->y / grid->super.cell_h;

    if (tx < 0 || ty < 0 || tx >= grid->super.x_cells || ty >= grid->super.y_cells)
        return;

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

    if (tx < 0 || ty < 0 || tx >= grid->super.x_cells || ty >= grid->super.y_cells)
        return;

    //FIXME: need proper sprites container, without iterating the whole list and
    //de-allocating the ListItem
    land_remove_list_data(&grid->sprites[ty * grid->super.x_cells + tx],
        self);
}

void land_sprite_remove_from_grid(LandSprite *self, LandGrid *grid)
{
    grid_unplace(self, LAND_SPRITES_GRID(grid));
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

static void land_sprites_grid_draw(LandGrid *super, LandView *view)
{
    LandSpritesGrid *self = LAND_SPRITES_GRID(super);
    LandView v = *view;
    /* If sprites extend right/down, we need draw more left and up. */
    v.x -= self->max_r;
    v.y -= self->max_b;
    v.scroll_x -= self->max_r;
    v.scroll_y -= self->max_b;
    /* If sprites extend left/up, we need to draw more right/down. */
    v.w += self->max_l + self->max_r;
    v.h += self->max_t + self->max_b;
    land_grid_draw_normal(super, &v);
}

void land_sprites_init(void)
{
    land_log_msg("land_sprites_init\n");
    land_alloc(land_grid_vtable_sprites);
    land_grid_vtable_sprites->draw = land_sprites_grid_draw;
    land_grid_vtable_sprites->draw_cell = (void *)land_sprites_grid_draw_cell;
}

LandSpriteType *land_spritetype_new(void)
{
    LandSpriteType *self;
    land_alloc(self);
    self->draw = dummy;
    return self;
}

LandSpriteTypeWithImage *land_spritetype_with_image_new(void)
{
    //FIXME TODO XXX
    return NULL;
}

void land_spritetype_image_initialize(LandSpriteTypeImage *self,
    LandImage *image)
{
    LAND_SPRITE_TYPE(self)->draw = dummy_image;
    LAND_SPRITE_TYPE(self)->overlap = land_sprite_overlap_pixelperfect;
    LAND_SPRITE_TYPE(self)->x = image->x - image->l;
    LAND_SPRITE_TYPE(self)->y = image->y - image->t;
    LAND_SPRITE_TYPE(self)->w = image->bitmap->w - image->l - image->r;
    LAND_SPRITE_TYPE(self)->h = image->bitmap->h - image->t - image->b;
    self->image = image;
    LAND_SPRITE_TYPE(self)->name = "image";
}

/* Create a new image sprite type with the given image. The source clipping of
 * the image is honored.
 */
LandSpriteType *land_spritetype_image_new(LandImage *image)
{
    LandSpriteTypeImage *self;
    land_alloc(self);
    land_spritetype_image_initialize(self, image);
    return LAND_SPRITE_TYPE(self);
}

/* Create a new animation sprite type with the given animation. The image is
 * used for collision detection.
 */
LandSpriteType *land_spritetype_animation_new(LandAnimation *animation,
    LandImage *image)
{
    LandSpriteTypeAnimation *self;
    land_alloc(self);
    if (!image)
        image = land_animation_get_frame(animation, 0);

    // TODO: Ok, so we automatically create a mask here.. but is this wanted?
    if (!image->mask)
        land_image_create_pixelmasks(image, 1, 128);

    land_spritetype_image_initialize(LAND_SPRITE_TYPE_IMAGE(self), image);
    LAND_SPRITE_TYPE(self)->draw = dummy_animation;
    self->animation = animation;
    self->super.super.name = "animation";
    return LAND_SPRITE_TYPE(self);
}
