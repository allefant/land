import land.land

LandNet *net
char const *address = "allefant.com:80"
LandBuffer *text
char buffer[1024]
bool connected

def _init(LandRunner *self):
    if land_argc > 1:
        address = land_argv[1]

    land_font_load("../../data/DejaVuSans.ttf", 10)
    
    net = land_net_new()
    land_net_buffer(net, buffer, sizeof buffer)
    land_net_connect(net, address) 
    
    text = land_buffer_new()
    land_buffer_cat(text, "initialized\n")

def _tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

    land_net_poll(net)
    if net->state == LAND_NET_OK:
        if not connected:
            connected = True
            land_buffer_cat(text, "connected\n")
            land_net_send(net, "GET /feed\r\n\r\n", 9 + 4)
    if net->full > 0:
        land_buffer_add(text, buffer, net->full)
        land_net_flush(net, net->full)

def _draw(LandRunner *self):
    land_clear(1, 1, 1, 1)
    land_buffer_add(text, "", 1)
    LandArray *lines = land_wordwrap_text(land_display_width(),
        land_display_height(), text->buffer)
    land_buffer_shorten(text, 1)
    land_text_pos(0, 0)
    land_color(0, 0, 0, 1)
    land_print_lines(lines, 0)
    land_text_destroy_lines(lines)

def _done(LandRunner *self):
    pass

def _config():
    land_set_display_parameters(512, 512,
        LAND_WINDOWED | LAND_OPENGL)
    land_set_fps(6)
land_example(_config, _init, _tick, _draw, _done)
