macro LAND_SPRITE(_) ((LandSprite *)(_))
macro LAND_SPRITE_ANIMATED(_) ((LandSpriteAnimated *)(_))
macro LAND_SPRITE_TYPE(_) ((LandSpriteType *)(_))
macro LAND_SPRITE_TYPE_IMAGE(_) ((LandSpriteTypeImage *)(_))
macro LAND_SPRITE_TYPE_ANIMATION(_) ((LandSpriteTypeAnimation *)(_))
macro LAND_SPRITES_GRID(x) ((LandSpritesGrid *)(x))

import array, display, grid, animation
static import tilegrid, pixelmask
import land.util2d

#*** "define" DEBUG_MASK

class LandSpriteType:
    # TODO: Sprites may have dynamic dimensions. There should be a vtable
    # entry to query the current dimensions, which is used by the sprites
    # grid. Right now, all sprites of the same type have the same dimensions.
    # This is not a big problem, as the grid dimensions only determine the
    # set of objects to test collision against - so setting it to the maximum
    # bounds should work.

    # Dimensions of the sprite inside the grid.
    # If the sprite is on sx/sy, then collision is checked in the rectangle
    # (sx - x, sy - y, sx - x + w, sy - y + h)
    # 
    # Note: This is independent of sprite-sprite collision. But Sprite-sprite
    # collision only will be performed on sprites who overlap in the grid.
    float x, y
    float w, h

    # How to draw sprites of this type.
    void (*draw)(LandSprite *self, LandView *view, LandGrid *grid)
    # Sprite-sprite collision detection.
    int (*overlap)(LandSprite *self, LandSprite *other)
    # How to initialize sprites of this type
    void (*initialize)(LandSprite *self)
    # How to destroy sprites of this type.
    void (*destroy)(LandSprite *self)
    
    # How to destroy the type.
    void (*destroy_type)(LandSpriteType *self)

    # Identification of this sprite type.
    char *name

# Each sprite of this type has its own image.
class LandSpriteTypeWithImage:
    LandSpriteType super

# All sprites of this type share the same image.
class LandSpriteTypeImage:
    LandSpriteType super
    LandImage *image

# All sprites of this type share the same animation.
# must use LandSpriteAnimated sprites
class LandSpriteTypeAnimation:
    LandSpriteTypeImage super
    LandAnimation *animation
    int auto_speed

# A simple sprite, with just a position and (optional) rotation.
class LandSprite:
    float x, y, sx, sy, angle
    LandSpriteType *type
    int tag
    bool shown
    bool flipped
    int sid # can be used by games to identify the kind of sprite

# A sprite with a dynamic image, i.e. each sprite has its own image,
# independent of its type.
class LandSpriteWithImage:
    LandSprite super
    LandImage *image

# A specialized sprite, who controls its current image with a frame number.
class LandSpriteAnimated:
    LandSprite super
    int frame
    float r, g, b, a

class LandSpritesGrid:
    LandGrid super
    LandList **sprites # 2D-array of sprite lists

    # keep all sprites sorted by their y coordinate
    int ysorted

    int tag

static LandGridInterface *land_grid_vtable_sprites

def land_sprites_grid_new(int cell_w, cell_h, x_cells, y_cells) -> LandGrid *:

    LandSpritesGrid *self
    land_alloc(self)
    land_grid_initialize(&self.super, cell_w, cell_h, x_cells, y_cells)
    self.super.vt = land_grid_vtable_sprites

    self.sprites = land_calloc(x_cells * y_cells * sizeof *self->sprites)

    return &self.super

def land_sprites_grid_resize(LandGrid *super, int cell_w, cell_h, x_cells, y_cells):
    LandSpritesGrid *self = (void *)super
    # FIXME: transfer old sprites into new grid
    land_sprites_grid_clear(super)
    land_free(self.sprites)
    self.sprites = land_calloc(x_cells * y_cells * sizeof *self->sprites)
    super->x_cells = x_cells
    super->y_cells = y_cells
    super->cell_w = cell_w
    super->cell_h = cell_h
    
def land_sprites_grid_clear(LandGrid *super):
    """
    Removes all sprites from a grid, but does not destroy them.
    """
    LandSpritesGrid *self = LAND_SPRITES_GRID(super)
    int j
    for j = 0 while j < super->x_cells * super->y_cells with j++:
        if self.sprites[j]:
            land_list_destroy(self.sprites[j])
            self.sprites[j] = None

def land_sprites_grid_del(LandGrid *super):
    """
    Deletes a sprites grid. The sprites themselves are not destroyed.
    """
    land_sprites_grid_clear(super)
    LandSpritesGrid *self = LAND_SPRITES_GRID(super)
    land_free(self.sprites)
    land_free(self)


static def dummy(LandSprite *self, LandView *view, LandGrid *grid):

    float x = (self.x - view->scroll_x) * view->scale_x + view->x
    float y = (self.y - view->scroll_y) * view->scale_y + view->y
    land_color(1, 0, 0, 1)
    land_rectangle(x, y, x + self.type->w * view->scale_x,
        y + self.type->h * view->scale_y)


static def dummy_image(LandSprite *self, LandView *view, LandGrid *grid):
    LandSpriteTypeImage *image = LAND_SPRITE_TYPE_IMAGE(self.type)
    float x = (self.x - view->scroll_x) * view->scale_x + view->x
    float y = (self.y - view->scroll_y) * view->scale_y + view->y

    land_image_draw_scaled_rotated_tinted_flipped(image->image,
        x, y, view->scale_x * self.sx, view->scale_y * self.sy, self.angle,
        view->r, view->g, view->b, view->a, self.flipped)

    if grid.debug_bounds:
        land_premul(1, 0, 0, .5)
        float x2 = x - self.type.x
        float y2 = y - self.type.y
        land_rectangle(x2 + 1, y2 + 1, x2 + image.super.w - 2, y2 + image.super.h - 2)

    *** "ifdef" DEBUG_MASK
    if image->image->mask:
        land_image_debug_pixelmask(image->image, x, y, self.angle, self->flipped)
    *** "endif"


static def dummy_animation(LandSprite *self, LandView *view, LandGrid *grid):

    LandSpriteTypeAnimation *animation = (LandSpriteTypeAnimation *)self->type
    LandSpriteAnimated *animated = (LandSpriteAnimated *)self
    float x = (self.x - view->scroll_x) * view->scale_x + view->x
    float y = (self.y - view->scroll_y) * view->scale_y + view->y
    float sx = self.sx
    float sy = self.sy
    LandImage *image
    if animation->animation:
        int f = animated.frame
        if animation.auto_speed:
            f = land_get_ticks() // animation.auto_speed
            int n = land_array_count(animation.animation.frames)
            if n > 0:
                f %= n
        image = land_animation_get_frame(animation->animation, f)
    else:
        image = animation->super.image
    land_image_draw_scaled_rotated_tinted(image, x, y,
        sx * view->scale_x, sy * view->scale_y, self.angle,
        animated->r * view->r, animated->g * view->g, animated->b * view->b,
        animated->a * view->b)
    # land_image_draw_scaled_rotated(image, x, y, animated->sx, animated->sy,
    #    self.angle)
    if grid.debug_bounds:
        float x2 = x - self.type.x
        float y2 = y - self.type.y
        land_premul(1, 0, 1, .5)
        land_rectangle(x2 + 1, y2 + 1, x2 + self.type.w - 2, y2 + self.type.h - 2)
    *** "ifdef" DEBUG_MASK
    if animation->super.image->mask:
        land_image_debug_pixelmask(animation->super.image, x, y,
            self.angle, self->flipped)
    *** "endif"

def land_sprite_set_frame(LandSprite *self, int frame):
    LandSpriteAnimated *a = (void *)self
    a.frame = frame

def land_sprite_initialize(LandSprite *self, LandSpriteType *type):

    self.type = type
    self.sx = 1
    self.sy = 1
    if self.type->initialize:
        self.type->initialize(self)

def land_sprite_new(LandSpriteType *type) -> LandSprite *:

    if not strcmp(type->name, "animation"):
        return land_sprite_animated_new(type)

    LandSprite *self
    land_alloc(self)
    land_sprite_initialize(self, type)
    return self

def land_sprite_with_image_new(LandSpriteType *type, LandImage
        *image) -> LandSprite *:

    LandSpriteWithImage *self
    land_alloc(self)
    land_sprite_initialize(LAND_SPRITE(self), type)
    self.image = image
    return LAND_SPRITE(self)

def land_sprite_image_destroy(LandSprite *self):
    pass

def land_sprite_image_initialize(LandSprite *super):
    pass

def land_sprite_animated_initialize(LandSprite *super):
    LandSpriteAnimated *self = (void *)super
    self.r = 1
    self.g = 1
    self.b = 1
    self.a = 1

def land_sprite_animated_new(LandSpriteType *type) -> LandSprite *:
    LandSpriteAnimated *self
    land_alloc(self)
    land_sprite_initialize(LAND_SPRITE(self), type)
    return LAND_SPRITE(self)

def land_sprite_animated_destroy(LandSprite *sprite):
    pass


def land_sprite_del(LandSprite *self):
    """
    Destroys a sprite. This will not remove its reference from a grid in case it
    is inside one - so only use this if you know what you are doing.
    """
    if self.type->destroy: self->type->destroy(self)
    land_free(self)


def land_sprite_destroy(LandSprite *self):
    """Same as land_sprite_del."""
    land_sprite_del(self)

def land_sprite_show(LandSprite *self, LandGrid *grid):
    if self.shown: return
    land_sprite_place_into_grid(self, grid, self.x, self->y)

def land_sprite_hide(LandSprite *self, LandGrid *grid):
    if not self.shown: return
    land_sprite_remove_from_grid(self, grid)

def land_sprite_overlap_pixelperfect(LandSprite *self, LandSprite *other) -> int:
    """
    Given two sprites who have a type LandSpriteTypeImage, do a pixel overlap
    test, and return 0 if they don't overlap.
    """
    return land_image_overlaps(LAND_SPRITE_TYPE_IMAGE(self.type)->image,
        self.x, self->y, self->angle, self->flipped,
        LAND_SPRITE_TYPE_IMAGE(other->type)->image,
        other->x, other->y, other->angle, other->flipped)

def land_sprite_grid_ysorted(LandGrid *self):
    LandSpritesGrid *sg = (void *)self
    sg->ysorted = 1

static def get_grid_extents(LandSprite *self, LandGrid *grid,
    int *tl, *tt, *tr, *tb):
    float l = self.x - self->type->x
    float t = self.y - self->type->y
    float r = self.x - self->type->x + self->type->w
    float b = self.y - self->type->y + self->type->h
    *tl = l / grid->cell_w
    *tt = t / grid->cell_h
    *tr = r / grid->cell_w
    *tb = b / grid->cell_h
    # FIXME: for a wrap-around grid, should wrap
    if *tl < 0: *tl = 0
    if *tt < 0: *tt = 0
    if *tr >= grid->x_cells: *tr = grid->x_cells - 1
    if *tb >= grid->y_cells: *tb = grid->y_cells - 1

def land_sprites_grid_get_all(LandGrid *sprites_grid) -> LandArray *:
    LandArray *a = land_array_new()
    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid)
    grid->tag++
    for int ty = 0 while ty < sprites_grid->y_cells with ty++:
        for int tx = 0 while tx < sprites_grid->x_cells with tx++:
            LandList *list = grid->sprites[ty * grid->super.x_cells + tx]
            if list:
                LandListItem *item = list->first
                while item:
                    LandSprite *sprite = item->data
                    if sprite->tag != grid->tag:
                        sprite->tag = grid->tag
                        land_array_add(a, sprite)
                    item = item->next
    return a

def land_sprites_grid_overlap(LandSprite *self,
    LandGrid *sprites_grid) -> LandList *:
    """
    Return a list of all sprites overlapping the sprite in the given grid.
    The sprite itself is not returned.
    Note that this only works if all sprites in the grid have compatible
    overlapping, e.g. if the sprite does a pixel-overlap test, then all other
    sprites must have a pixel mask, or if it does a bounding circle test, then
    all other sprites must have a bounding circle, and so on.
    """

    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid)
    LandList *retlist = NULL
    int tl, tt, tr, tb
    get_grid_extents(self, sprites_grid, &tl, &tt, &tr, &tb)

    grid->tag++

    for int ty = tt while ty <= tb with ty++:
        for int tx = tl while tx <= tr with tx++:
            LandList *list = grid->sprites[ty * grid->super.x_cells + tx]
            if list:
                LandListItem *item = list->first
                while item:
                    LandSprite *other = item->data
                    if other != self and other->tag != grid->tag:
                        other->tag = grid->tag
                        if self.type->overlap(self, other):
                            land_add_list_data(&retlist, other)
                    item = item->next

    return retlist

def land_sprites_grid_get_circle(LandGrid *sprites_grid, float x, y,
    float radius) -> LandList *:
    """
    Return a list of all sprites in the grid, whose position is inside the given
    circle (in pixels). The size of the sprite is currently ignored, only its
    point position is used.
    """

    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid)
    LandList *retlist = NULL
    float l = x - radius
    float t = y - radius
    float r = x + radius
    float b = y + radius
    int tl = l / grid->super.cell_w
    int tt = t / grid->super.cell_h
    int tr = r / grid->super.cell_w
    int tb = b / grid->super.cell_h
    int tx, ty
    if tl < 0: tl = 0
    if tt < 0: tt = 0
    if tr >= grid->super.x_cells: tr = grid->super.x_cells - 1
    if tb >= grid->super.y_cells: tb = grid->super.y_cells - 1

    grid->tag++
    for ty = tt while ty <= tb with ty++:

        for tx = tl while tx <= tr with tx++:

            LandList *list = grid->sprites[ty * grid->super.x_cells + tx]
            if list:

                LandListItem *item = list->first
                while item:
                    LandSprite *other = item->data
                    if other->tag != grid->tag:
                        other->tag = grid->tag
                        float dx = other->x - x
                        float dy = other->y - y
                        if dx * dx + dy * dy < radius * radius:

                            land_add_list_data(&retlist, other)

                    item = item->next

    return retlist

def land_sprites_grid_get_rectangle(LandGrid *sprites_grid,
    float l, t, r, b) -> LandList *:
    """
    Return a list of all sprites in the given rectangle. All the sprites
    who overlap one of the grid cells overlapped by the rectangle are
    returned.
    """
    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid)
    LandList *retlist = None
    int tl = l / grid->super.cell_w
    int tt = t / grid->super.cell_h
    int tr = r / grid->super.cell_w
    int tb = b / grid->super.cell_h
    int tx, ty
    if tl < 0: tl = 0
    if tt < 0: tt = 0
    if tr >= grid->super.x_cells: tr = grid->super.x_cells - 1
    if tb >= grid->super.y_cells: tb = grid->super.y_cells - 1
    grid->tag++
    for ty = tt while ty <= tb with ty++:
        for tx = tl while tx <= tr with tx++:
            LandList *list = grid->sprites[ty * grid->super.x_cells + tx]
            if list:
                LandListItem *item = list->first
                while item:
                    LandSprite *other = item->data
                    if other->tag != grid->tag:
                        other->tag = grid->tag
                        land_add_list_data(&retlist, other)
                    item = item->next

    return retlist

def land_sprites_grid_get_rectangle_exact(LandGrid *sprites_grid,
        float l, t, r, b) -> LandList *:
    LandList *retlist = None
    land_sprites_grid_get_rectangle_exact_into_list(sprites_grid, l, t, r, b, &retlist)
    return retlist

def land_sprites_grid_get_rectangle_exact_into_list(LandGrid *sprites_grid,
        float l, t, r, b, LandList **retlist) -> bool:
    LandRectangle qrect = {l, t, r - l, b - t}
    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid)
    if retlist:
        *retlist = None
    int tl = l / grid->super.cell_w
    int tt = t / grid->super.cell_h
    int tr = r / grid->super.cell_w
    int tb = b / grid->super.cell_h
    int tx, ty
    if tl < 0: tl = 0
    if tt < 0: tt = 0
    if tr >= grid->super.x_cells: tr = grid->super.x_cells - 1
    if tb >= grid->super.y_cells: tb = grid->super.y_cells - 1
    grid->tag++
    for ty = tt while ty <= tb with ty++:
        for tx = tl while tx <= tr with tx++:
            LandList *list = grid->sprites[ty * grid->super.x_cells + tx]
            if list:
                LandListItem *item = list->first
                while item:
                    LandSprite *other = item->data
                    if other->tag != grid->tag:
                        other->tag = grid->tag
    
                        LandRectangle srect = land_sprite_rect(other)
                            
                        if land_rectangles_overlap(qrect, srect):
                            if retlist:
                                land_add_list_data(retlist, other)
                            else:
                                return True
                    item = item->next
    return False

def land_sprite_rect(LandSprite *self) -> LandRectangle:
    return (LandRectangle){self.x - self.type.x, self.y - self.type.y,
        self.type.w, self.type.h}

def land_sprites_grid_get_in_cell(LandGrid *grid,
    int cx, cy) -> LandList *:
    LandList *retlist = None
    LandSpritesGrid *sgrid = LAND_SPRITES_GRID(grid)
    if cx < 0 or cy < 0 or cx >= grid->x_cells or cy >= grid->y_cells: return None
    LandList *list = sgrid->sprites[cy * grid->x_cells + cx]
    if list:
        LandListItem *item = list->first
        while item:
            LandSprite *s = item->data
            int sx = s->x / grid->cell_w
            int sy = s->y / grid->cell_h
            if sx == cx and sy == cy:
                land_add_list_data(&retlist, s)
            item = item->next
    return retlist

static def is_left(float ax, ay, bx, by) -> int:
    return ax * by - ay * bx < 0

static def is_in_triangle(float x, y, p1x, p1y, p2x, p2y, p3x, p3y) -> int:
    if is_left(x - p1x, y - p1y, p2x - p1x, p2y - p1y) and\
        is_left(x - p2x, y - p2y, p3x - p2x, p3y - p2y) and\
        is_left(x - p3x, y - p3y, p1x - p3x, p1y - p3y): return True
    return False

def land_sprites_get_triangle(LandGrid *sprites_grid,
    float p1x, p1y, p2x, p2y, p3x, p3y) -> LandList *:
    """
    Return a list of all sprites in the given triangle. This only considers
    center positions, the size/shape of sprites is completely ignored.
    """

    LandSpritesGrid *grid = LAND_SPRITES_GRID(sprites_grid)

    # get bounding box
    int l = p1x, t = p1y, r = p1y, b = p1y
    if p2x < l: l = p2x
    if p3x < l: l = p3x
    if p2x > r: r = p2x
    if p3x > r: r = p3x
    if p2y < t: t = p2y
    if p3y < t: t = p3y
    if p2y > b: b = p2y
    if p3y > b: b = p3y

    # get cell bounding box
    int tl = l / grid->super.cell_w
    int tt = t / grid->super.cell_h
    int tr = r / grid->super.cell_w
    int tb = b / grid->super.cell_h
    if tl < 0: tl = 0
    if tt < 0: tt = 0
    if tr >= grid->super.x_cells: tr = grid->super.x_cells - 1
    if tb >= grid->super.y_cells: tb = grid->super.y_cells - 1

    # check sprites in all cells
    LandList *retlist = NULL
    grid->tag++
    for int ty = tt while ty <= tb with ty++:
        for int tx = tl while tx <= tr with tx++:
            LandList *list = grid->sprites[ty * grid->super.x_cells + tx]
            if not list: continue
            LandListItem *item = list->first
            while item:
                LandSprite *other = item->data
                if other->tag != grid->tag:
                    other->tag = grid->tag
                    # FIXME: have to re-order triangle points if not anti-clockwise
                    if is_in_triangle(other->x, other->y,
                        p1x, p1y, p2x, p2y, p3x, p3y):
                        land_add_list_data(&retlist, other)
                item = item->next
    return retlist

# Return a list of all sprites in the given view and overlap. The overlap
# increases when negative for t and l and positive for r and l.
def land_sprites_grid_get_in_view(LandGrid *sprites_grid,
    LandView *view, float l, t, r, b) -> LandList *:

    l += view->scroll_x + view->x
    t += view->scroll_y + view->y
    r += view->scroll_x + view->x + view->w
    b += view->scroll_y + view->y + view->h
    return land_sprites_grid_get_rectangle(sprites_grid, l, t, r, b)

static def grid_place(LandSprite *self, LandSpritesGrid *grid):
    """
    Place a sprite into a grid.
    Note: This *must not* be called more than once for a sprite.
    Note: The sprite *must not* change position or dimension after calling this.
    Note: Use grid_unplace to undo the effect of this function.
    """

    int tl, tt, tr, tb
    get_grid_extents(self, &grid->super, &tl, &tt, &tr, &tb)

    self.shown = True

    # Add the sprite to all cells it possibly overlaps.
    for int ty = tt while ty <= tb with ty++:
        for int tx = tl while tx <= tr with tx++:

            # FIXME: need proper sprites container, without allocating a new
            # ListItem
            if grid->ysorted:
                LandList *list = grid->sprites[ty * grid->super.x_cells + tx]
                if not list:
                    list = land_list_new()
                    grid->sprites[ty * grid->super.x_cells + tx] = list
                LandListItem *item = land_listitem_new(self)
                LandListItem *i = list->first
                while i:
                    LandSprite *ls = i->data
                    if ls->y > self.y:
                        land_list_insert_item_before(list, item, i)
                        goto done
                    if ls->y == self.y:
                        if ls->x > self.x:
                            land_list_insert_item_before(list, item, i)
                            goto done
                    i = i->next
                land_list_insert_item(list, item)
                label done
            else:
                land_add_list_data(&grid->sprites[ty * grid->super.x_cells + tx],
                    self)

static def grid_unplace(LandSprite *self, LandSpritesGrid *grid):
    """
    Remove a sprite from a grid.
    """
    int tl, tt, tr, tb
    get_grid_extents(self, &grid->super, &tl, &tt, &tr, &tb)

    for int ty = tt while ty <= tb with ty++:
        for int tx = tl while tx <= tr with tx++:
            # FIXME: need proper sprites container, without iterating the whole
            # list and de-allocating the ListItem
            land_remove_list_data(&grid->sprites[ty * grid->super.x_cells + tx],
                self)

    self.shown = False

def land_sprite_remove_from_grid(LandSprite *self, LandGrid *grid):
    """
    Remove a sprite from a grid.
    """
    grid_unplace(self, LAND_SPRITES_GRID(grid))

def land_sprite_place_into_grid(LandSprite *self, LandGrid *grid, float
        x, float y):
    """
    Place a sprite into a grid.
    """
    self.x = x
    self.y = y
    grid_place(self, (LandSpritesGrid *)grid)


def land_sprite_move(LandSprite *self, LandGrid *grid, float x, float y):
    """
    Move a sprite by the given amount of pixels
    """
    grid_unplace(self, (LandSpritesGrid *)grid)
    self.x += x
    if self.x < 0: self->x = 0
    if self.x >= grid->cell_w * grid->x_cells:
        self.x = grid->cell_w * grid->x_cells - 1

    self.y += y
    if self.y < 0: self->y = 0
    if self.y >= grid->cell_h * grid->y_cells:
        self.y = grid->cell_h * grid->y_cells - 1

    grid_place(self, (LandSpritesGrid *)grid)

def land_sprite_move_to(LandSprite *self, LandGrid *grid, float x, float y):
    """
    Move a sprite to the given position in pixels.
    """
    land_sprite_move(self, grid, x - self.x, y - self->y)

def land_sprites_grid_draw_cell(LandSpritesGrid *self, LandView *view,
    int cell_x, cell_y, float pixel_x, pixel_y):

    LandList *list = self.sprites[cell_y * self->super.x_cells + cell_x]
    if list:

        LandListItem *item = list->first
        while item:

            LandSprite *sprite = item->data
            if sprite->tag != self.tag:
                self.super.stats_drawn += 1
                sprite->type->draw(sprite, view, &self.super)
                sprite->tag = self.tag

            item = item->next

def land_sprites_grid_draw(LandGrid *super, LandView *view):
    LandSpritesGrid *self = (void *)super
    self.tag++
    land_grid_draw_normal(super, view)

static def get_cell_at(LandGrid *self, LandView *view, float view_x, view_y,
    *cell_x, *cell_y):
    float x = view->scroll_x + (view_x - view->x) / view->scale_x
    float y = view->scroll_y + (view_y - view->y) / view->scale_y
    *cell_x = x / self.cell_w
    *cell_y = y / self.cell_h

def land_sprites_init():

    land_log_message("land_sprites_init\n")
    land_alloc(land_grid_vtable_sprites)
    land_grid_vtable_sprites->draw = land_sprites_grid_draw
    land_grid_vtable_sprites->draw_cell = (void *)land_sprites_grid_draw_cell
    land_grid_vtable_sprites->del = land_sprites_grid_del
    land_grid_vtable_sprites->get_cell_at = get_cell_at

def land_sprites_exit():

    land_log_message("land_sprites_exit\n")
    land_free(land_grid_vtable_sprites)


def land_spritetype_new() -> LandSpriteType *:
    LandSpriteType *self
    land_alloc(self)
    self.name = "dummy"
    self.draw = dummy
    return self


def land_spritetype_destroy(LandSpriteType *self):

    if self.destroy_type: self->destroy_type(self)
    land_free(self.name)
    land_free(self)


def land_spritetype_with_image_new() -> LandSpriteTypeWithImage *:

    #FIXME TODO XXX
    return NULL


def land_spritetype_image_initialize(LandSpriteType *super,
    LandImage *image, bool mask, int n):
        
    LandSpriteTypeImage *self = (void *)super

    super->draw = dummy_image
    super->overlap = land_sprite_overlap_pixelperfect
    super->destroy = land_sprite_image_destroy
    super->initialize = land_sprite_image_initialize
    if image:
        super->x = image->x - image->l
        super->y = image->y - image->t
        super->w = land_image_width(image) - image->l - image->r
        super->h = land_image_height(image) - image->t - image->b
    else:
        super->x = super->y = super->w = super->h = 0
    self.image = image
    LAND_SPRITE_TYPE(self)->name = land_strdup("image")

    # TODO: Ok, so we automatically create a mask here.. but is this wanted?
    if image and mask and not image->mask:
        land_image_create_pixelmasks(image, n, 128)

# Create a new image sprite type with the given image. The source clipping of
# the image is honored.
# Ownership of the image is transferred.
def land_spritetype_image_new(LandImage *image, bool mask,
    int n) -> LandSpriteType *:

    LandSpriteTypeImage *self
    land_alloc(self)
    land_spritetype_image_initialize((void *)self, image, mask, n)
    return LAND_SPRITE_TYPE(self)

def land_spritetype_animation_initialize(LandSpriteType *super,
    LandAnimation *animation, LandImage *image, bool mask, int n):
    LandSpriteTypeAnimation *self = (void *)super
    
    if not image and animation:
        image = land_animation_get_frame(animation, 0)

    land_spritetype_image_initialize((void *)self, image, False, 0)
    if image and mask:
        land_image_create_pixelmasks(image, n, 128)
    super->draw = dummy_animation
    super->destroy = land_sprite_animated_destroy
    super->destroy_type = land_spritetype_animation_destroy
    super->initialize = land_sprite_animated_initialize
    self.animation = animation
    land_free(super->name)
    super->name = land_strdup("animation")

def land_spritetype_animation_new(
    LandAnimation *animation, LandImage *image, bool mask, int n) -> LandSpriteType *:
    """
    Create a new animation sprite type with the given animation. The
    image is used for collision detection. If no image is given, the
    first frame of the animation is used instead.
    
    If a mask is request n is the number of rotations. A negative n
    means two variants are made for each rotation (one flipped
    horizontally).
    """
    LandSpriteTypeAnimation *self
    land_alloc(self)
    land_spritetype_animation_initialize((void *)self, animation, image,
        mask, n)
    
    return LAND_SPRITE_TYPE(self)

def land_spritetype_animation_destroy(LandSpriteType *base):

    LandSpriteTypeAnimation *self = LAND_SPRITE_TYPE_ANIMATION(base)
    if self.animation: land_animation_destroy(self->animation)

def land_spritetype_animation_get_animation(LandSpriteType *base) -> LandAnimation *:

    LandSpriteTypeAnimation *self = LAND_SPRITE_TYPE_ANIMATION(base)
    return self.animation
