import global stdlib
import global string

import global land/land

char const *data[] = {
    "Aardvark", "Antelope", "Ape", "Armadillo", "Anteater",
    "Badger",  "Bat", "Bear",  "Beaver", "Boar", "Buffalo", "Bison",
    "Camel", "Chinchilla", "Coyote", "Cave bear", "Cat", "Cuscus", "Chimpanzee",
    "Deer", "Dingo", "Dolphin", "Dog", "Donkey", "Dromedary", "Dugong", "Dormouse",
    "Elephant",
    "Ferret", "Fox", "Firefox",
    "Goat", "Giraffe", "Glyptodon", "Gnu", "Grizzly", "Gorilla", "Galago", "Gaur", "Gibbon",
    "Hippo", "Hyena", "Hedgehog", "Hamster", "Horse", "Hyrax",
    "Ibex",
    "Jackal", "Jaguar",
    "Kangaroo", "Kinkajou", "Koala", "Kodiak",
    "Leopard", "Lion", "Llama", "Lynx",
    "Macaque",  "Marten", "Manatee", "Mink", "Mole", "Mongoose", "Monkey", "Moose", "Mouse", "Marmot", "Mammoth",
    "Opossum", "Orca", "Otter",
    "Panda", "Panther", "Pig", "Platypus", "Polar bear", "Porcupine", "Pudu", 
    "Rabbit", "Racoon", "Rhino", 
    "Sable", "Shrew", "Skunk", "Squirrel", "Sloth", "Seal", "Sheep",
    "Tamandua", "Tiger", "Turtle", "Tapir", "Takin", "Tahr",
    "Vampire",
    "Walrus", "Warthog", "Weasel", "Whale", "Wisent", "Wombat", "Wolf", "Wolverine",
    "Yak",
    "Zebra",
    None}

LandWidget *desktop

static def construct_menu() -> LandWidget *:
    int index[26]
    int i, j
    for i = 0 while i < 26 with i++:
        for j = 0 while data[j] with j++:
            if data[j][0] == 'A' + i: break

        index[i] = j

    LandWidget *menu = land_widget_menu_new(desktop,
        land_mouse_x(), land_mouse_y(), 10, 10)
    for i = 0 while i < 10 with i++:
        char name[256]
        int h = land_rand(0, 25)
        name[0] = 'A' + h
        name[1] = '\0'
        LandWidget *submenu = land_widget_menu_new(desktop, 0, 0, 10, 10)
        for j = 0 while  data[index[h] + j] and data[index[h] + j][0] == 'A' + h with j++:
            land_widget_menuitem_new(submenu, data[index[h] + j], NULL)

        land_widget_hide(submenu)
        land_widget_submenuitem_new(menu, name, submenu)

    return menu

static def my_mouse_tick(LandWidget *self):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)

    land_widget_container_mouse_tick(self)

    if not container->mouse:
        if (land_mouse_b() & 2) and (land_mouse_delta_b() & 2):
            land_widget_container_set_mouse_focus(self, construct_menu())

static def on_quit(LandWidget *self):
    printf("Quit!\n")

static def on_copy(LandWidget *self):
    printf("Copy!\n")

static def on_paste(LandWidget *self):
    printf("Paste!\n")

static def on_button(LandWidget *self):
    printf("Button!\n")

static def on_new(LandWidget *self):
    printf("New!\n")

static def on_clear(LandWidget *self):
    printf("Clear!\n")

def _init(LandRunner *self):
    land_find_data_prefix("data/")
    land_font_load("galaxy.ttf", 12)

    land_widget_theme_set_default(land_widget_theme_new("classic.cfg"))
    desktop = land_widget_board_new(None, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandWidget *vbox = land_widget_vbox_new(desktop, 100, 100, 200, 100)
    LandWidget *menubar = land_widget_menubar_new(vbox, 0, 0, 10, 10)

    LandWidget *recentmenu = land_widget_menu_new(desktop, 0, 0, 10, 10)
    land_widget_menuitem_new(recentmenu, "Clear", on_clear)
    land_widget_hide(recentmenu)

    LandWidget *filemenu = land_widget_menu_new(desktop, 0, 0, 10, 10)
    land_widget_menuitem_new(filemenu, "New", on_new)
    land_widget_submenuitem_new(filemenu, "Recent", recentmenu)
    land_widget_menuitem_new(filemenu, "Quit", on_quit)

    LandWidget *editmenu = land_widget_menu_new(desktop, 0, 0, 10, 10)
    land_widget_menuitem_new(editmenu, "Copy", on_copy)
    land_widget_menuitem_new(editmenu, "Paste", on_paste)

    land_widget_menubutton_new(menubar, "File", filemenu, 0, 0, 1, 1)
    land_widget_hide(filemenu)

    land_widget_menubutton_new(menubar, "Edit", editmenu, 0, 0, 1, 1)
    land_widget_hide(editmenu)

    land_widget_box_new(vbox, 0, 0, 10, 10)

    land_widget_button_new(desktop, "Button", on_button, 300, 100, 20, 20)

    desktop->vt->mouse_tick = my_mouse_tick

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_widget_draw(desktop)

    LandWidget *widget

    land_text_pos(10, 10)
    land_color(0, 0, 0, 1)
    land_print("mouse focus")
    widget = desktop
    while True:
        land_print("%s[%p]", widget->vt->name, widget)
        if not land_widget_is(widget, LAND_WIDGET_ID_CONTAINER): break
        LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
        if not container->mouse: break
        widget = container->mouse

    land_text_pos(330, 10)
    land_color(0, 0, 0, 1)
    land_print("keyboard focus")
    widget = desktop
    while True:
        land_print("%s[%p]", widget->vt->name, widget)
        if not land_widget_is(widget, LAND_WIDGET_ID_CONTAINER): break
        LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
        if not container->keyboard: break
        widget = container->keyboard

def _done(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
