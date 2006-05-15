/*
 * Polymorphism
 *
 * The widgets are organized in a class hierarchy. To use polymorphism, you need
 * to convert pointers to one class to pointers to a base or specialized class.
 * This is done using land_widget_check, which will use the widgets vtable to
 * assert that the conversion is possible and generate a runtime error
 * otherwise.
 *
 * Reference counting
 *
 * The widgets use reference counting to handle deletion. This is a cheap way
 * out of dealing with stale references/dangling pointers. A GUI without either reference counting
 * or garbage collection is possible, it just needs some more design work. In
 * our case here, following a KISS principle, we do simple naive reference counting,
 * and leave the user to deal with possible problems like circular references.
 *
 * In the normal case, it works like this: You create a widget, and have to
 * pass along a parent widget to the constructor. Now, the parent will hold a
 * reference to the new window. There is no reference from the child to he
 * parent, despite the parent field referencing the parent. This is done to
 * avoid complications with cyclic references. If your own widgets contain
 * cyclic references in another way, you should understand how the reference
 * counting works.
 *
 * The first consequence of the above is, you always should manually reference the
 * top level window, since it has no parent it is referenced by.
 *
 * The apparent problem is the possible dangling pointer of a child to its
 * parent. But it should be save, since whenever the parent is deleted, it will
 * delete all its children anyway.
 *
 * An example:
 * desktop = desktop_new();
 * reference(desktop);
 * child = window_new(desktop);
 * unreference(desktop);
 *
 * This does what is expected. The only reference to desktop is removed manually,
 * therefore it gets destroyed. The destructor will detach all children. The only
 * child in this case will therefore drop its reference count to zero, and get
 * destroyed as well.
 *
 * desktop = desktop_new();
 * reference(desktop);
 * child = window_new(desktop);
 * reference(child);
 * unreference(desktop);
 *
 * Here, a reference is kept to child. Maybe it is the window with keyboard
 * focus, and the focus handler holds a reference to it. So, when the desktop
 * is destroyed, first all childs are detached again. This means, the parent
 * member of child is set to NULL, and its reference is decreased. Since there
 * is still the manual reference, nothing else will be done. The desktop itself
 * however is destroyed. Also note that any other childs without a reference
 * would be destroyed correctly, and it also would work recursively down for
 * their childs. Only the child window stays, and the focus handler won't
 * crash.
 *
 * unreference(child);
 *
 * If the focus handler is done, the reference of child will now drop to zero,
 * and it is destroyed again.
 *
 * Now, about cyclic references, just either don't use them, or else take care
 * to resolve them before dropping the last reference into the cycle. As an
 * example, you make a watchdog window, which somehow watches another window.
 * So, you play good, and along with storing a reference to that other window,
 * you increase the reference count of the other window, just so you never get
 * a dangling pointer. In your destructor, you release the reference again, so
 * everything seems to work out. But consider this:
 *
 * desktop = new_widget(NULL);
 * reference(desktop);
 * watchdog = new_widget(desktop);
 * watchdog_watch(desktop);
 * unreference(desktop);
 *
 * Yikes. Now you see the problem. Although nobody holds a reference to watchdog,
 * and we remove the only real reference to desktop, neither of them gets deleted.
 * Worse, neither of them can ever be deleted again, since the only reference to
 * either is from each other.
 *
 * Simple rule here would be: The watchdog only ever should watch a sibling or
 * unrelated widget, never a parent. Of course, in practice, widgets could get
 * reparented and whatever, so things like this need watching out. And there
 * are many other cases. Also, you never have to use the reference counting. You
 * just need to understand that Land provides no way to directly and forcefully
 * delete one of its widgets, and why it is like that.
 */

#ifdef _PROTOTYPE_

typedef struct LandWidget LandWidget;
typedef struct LandWidgetInterface LandWidgetInterface;
typedef struct LandWidgetProperty LandWidgetProperty;

#include "../hash.h"
#include "gul.h"

#define LAND_WIDGET_ID_BASE 1
#define LAND_WIDGET_ID_CONTAINER 2
#define LAND_WIDGET_ID_SCROLLING 4
#define LAND_WIDGET_ID_BUTTON 8
#define LAND_WIDGET_ID_LIST 16

struct LandWidgetInterface
{
    int id;
    char const *name;

    void (*init)(LandWidget *self);
    void (*enter)(LandWidget *self);
    void (*tick)(LandWidget *self);

    void (*mouse_enter)(LandWidget *self);
    void (*mouse_tick)(LandWidget *self);
    void (*mouse_leave)(LandWidget *self);

    void (*keyboard_enter)(LandWidget *self);
    void (*keyboard_tick)(LandWidget *self);
    void (*keyboard_leave)(LandWidget *self);

    void (*add)(LandWidget *self, LandWidget *add);
    void (*move)(LandWidget *self, float dx, float dy);
    void (*size)(LandWidget *self, float dx, float dy);

    void (*draw)(LandWidget *self);
    void (*leave)(LandWidget *self);
    void (*destroy)(LandWidget *self);
};

struct LandWidget
{
    LandWidgetInterface *vt;
    LandWidget *parent;
    GUL_BOX box;
    int got_mouse : 1;
    int send_to_top : 1;
    int dont_clip : 1;
    int no_decoration : 1;
    int reference;
    LandHash *properties;

   struct LandWidgetTheme *theme;
};

struct LandWidgetProperty
{
    void (*destroy)(void *data);
    void *data;
};

extern LandWidgetInterface *land_widget_base_interface;

#define LAND_WIDGET(widget) ((LandWidget *) \
    land_widget_check(widget, LAND_WIDGET_ID_BASE, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "widget/base.h"
#include "widget/layout.h"

static LandList *cemetery;
LandWidgetInterface *land_widget_base_interface = NULL;

void *land_widget_check(void const *ptr, int id, char const *file,
    int linenum)
{
    LandWidget const *widget = ptr;
    if (widget->vt->id & id)
        return (void *)ptr; /* should provide a const version of the whole function isntead */
    land_exception("%s: %d: Widget cannot be converted.", file, linenum);
    return NULL;
}

void land_widget_set_property(LandWidget *self, char const *property,
    void *data, void (*destroy)(void *data))
{
    if (!self->properties) self->properties = land_hash_new();
    LandWidgetProperty *prop = calloc(1, sizeof *prop);
    prop->data = data;
    prop->destroy = destroy;
    land_hash_insert(self->properties, property, prop);
}

void land_widget_del_property(LandWidget *self, char const *property)
{
    if (!self->properties) return;
    LandWidgetProperty *prop = land_hash_remove(self->properties, property);
    if (prop->destroy) prop->destroy(prop);
}

void *land_widget_get_property(LandWidget *self, char const *property)
{
    if (!self->properties) return NULL;
    LandWidgetProperty *prop = land_hash_get(self->properties, property);
    if (prop) return prop->data;
    return NULL;
}

void land_widget_remove_all_properties(LandWidget *self)
{
    LandHash *hash = self->properties;
    if (!hash) return;
    int i;
    for (i = 0; i < hash->size; i++)
    {
        if (hash->entries[i])
        {
            int j;
            for (j = 0; j < hash->entries[i]->n; j++)
            {
                LandWidgetProperty *prop = hash->entries[i][j].data;
                if (prop->destroy) prop->destroy(prop);
            }
        }
    }
    land_hash_destroy(self->properties);
    self->properties = NULL;
}

void land_widget_base_initialize(LandWidget *self, LandWidget *parent, int x, int y, int w, int h)
{
    land_widget_base_interface_initialize();

    gul_box_initialize(&self->box);
    self->box.x = x;
    self->box.y = y;
    self->box.w = w;
    self->box.h = h;
    land_widget_layout_set_minimum_size(self, w, h);
    if (parent)
    {
        self->theme = parent->theme;
        land_call_method(parent, add, (parent, self));
    }
}

LandWidgetInterface *land_widget_copy_interface(LandWidgetInterface *basevt,
    char const *name)
{
    LandWidgetInterface *vt;
    land_alloc(vt);
    memcpy(vt, basevt, sizeof *vt);
    vt->name = name;
    return vt;
}

void land_widget_create_interface(LandWidget *widget, char const *name)
{
    widget->vt = land_widget_copy_interface(widget->vt, name);
}

LandWidget *land_widget_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidget *self;
    land_alloc(self);
    land_widget_base_initialize(self, parent, x, y, w, h);
    return self;
}

void land_widget_base_destroy(LandWidget *self)
{
    land_widget_remove_all_properties(self);
    free(self);
}

static void land_widget_really_destroy(LandWidget *self)
{
    if (self->vt->destroy)
        self->vt->destroy(self);
    else
        land_widget_base_destroy(self);
}

void land_widget_unreference(LandWidget *self)
{
    self->reference--;
    if (self->reference <= 0)
        land_widget_really_destroy(self);
}

void land_widget_reference(LandWidget *self)
{
    self->reference++;
}

void land_widget_base_mouse_enter(LandWidget *self)
{
    self->got_mouse = 1;
}

void land_widget_base_mouse_leave(LandWidget *self)
{
    self->got_mouse = 0;
}

void land_widget_base_move(LandWidget *self, float dx, float dy)
{
    self->box.x += dx;
    self->box.y += dy;
}

void land_widget_move(LandWidget *self, float dx, float dy)
{
    if (self->vt->move)
        self->vt->move(self, dx, dy);
    else
    {
        land_widget_base_move(self, dx, dy);
    }
}

void land_widget_base_size(LandWidget *self, float dx, float dy)
{
    self->box.w += dx;
    self->box.h += dy;
    if (land_widget_layout(self))
    {
        if (self->box.w < self->box.min_width)
            self->box.w = self->box.min_width;
        if (self->box.h < self->box.min_height)
            self->box.h = self->box.min_height;
        land_widget_layout(self);
    }
}

void land_widget_size(LandWidget *self, float dx, float dy)
{
    if (self->vt->size)
        self->vt->size(self, dx, dy);
    else
    {
        land_widget_base_size(self, dx, dy);
    }
}

void land_widget_tick(LandWidget *self)
{
    land_call_method(self, tick, (self));
}

void land_widget_draw(LandWidget *self)
{
    int pop = 0;
    if (!self->dont_clip)
    {
        land_clip_push();
        land_clip_on();
        land_clip_intersect(self->box.x, self->box.y, self->box.x + self->box.w,
            self->box.y + self->box.h);
        pop = 1;
    }
    land_call_method(self, draw, (self));
    if (pop)
    {
        land_clip_pop();
    }
}

void land_widget_base_interface_initialize(void)
{
    if (land_widget_base_interface) return;

    land_alloc(land_widget_base_interface);
    land_widget_base_interface->id = LAND_WIDGET_ID_BASE;
    land_widget_base_interface->name = "base";
}
