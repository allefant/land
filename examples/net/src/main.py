import global land/land

macro FPS 60

macro MSG_TICK MSG_USER

macro MAX_PACKET_SIZE 256

macro ID_JOIN 1
macro ID_WHO  2
macro ID_PING 3

class MyWidget:
    LandWidget widget
    int state
    int id

enum State:
    LISTEN
    LISTENING
    CONNECT
    CONNECTING
    CONNECTED
    FREE
    TAKEN
    NOTHING
    SELF
    ANOTHER

char const *state_strings[] = {
    "Listen          ",
    "Listening       ",
    "Connect         ",
    "Connecting      ",
    "Disconnect      ",
    "Free            ",
    "Kick            ",
    "~~~~~~~~~~~~~~~~",
    "Self            ",
    "Another         ",
    NULL
}

LandNet *conn_listen
LandNet *conn_out

LandNet *conn_server[8]

int ping_out
int ping_server[8]

LandWidget *desktop
LandWidget *listen_widget
LandWidget *connect_widget
LandWidget *clients[16]

char const *address = "localhost:7778"

int ticks

static def client_clear_others (void):
    int i
    for i = 0; i < 8; i++:
        MyWidget *my = (MyWidget *)clients[i * 2 + 1]
        if my->state == ANOTHER or my->state == SELF:
            my->state = FREE

static def server_notify_lost (int who):
    int j
    char packet[12]
    int *idata = (int *)packet

    for j = 0; j < 8; j++:
        # part message to all remaining 
        if conn_server[j]:
            idata[0] = ID_JOIN
            idata[1] = who
            idata[2] = 1
            land_net_send(conn_server[j], packet, 12)

def clicked(LandWidget *self):
    MyWidget *my = (MyWidget *)self

    switch my->state:
        case LISTEN:
            conn_listen = land_net_new()
            land_net_listen(conn_listen, address)
            if conn_listen->state == LAND_NET_LISTENING:
                my->state = LISTENING
            else:
                land_net_del(conn_listen)
                conn_listen = NULL
            break

        case CONNECT:
            conn_out = land_net_new()
            land_net_connect(conn_out, address)
            if conn_out->state == LAND_NET_CONNECTING:
                my->state = CONNECTING
            else:
                land_net_del (conn_listen)
                conn_listen = NULL
            break

        case CONNECTED:
            land_net_del(conn_out)
            conn_out = NULL
            my->state = CONNECT
            client_clear_others()
            break

        case LISTENING:
            land_net_del(conn_listen)
            conn_listen = NULL
            my->state = LISTEN
            break

        case TAKEN:
            land_net_del(conn_server[my->id])
            conn_server[my->id] = NULL

           server_notify_lost(my->id)
           my->state = FREE
           break

def my_mouse_tick(LandWidget *self):
    if land_mouse_delta_b() & 1:
        if land_mouse_b() & 1:
            clicked(self)

def my_tick(LandWidget *self):
    MyWidget *my = (MyWidget *)self
    switch my->state:
        case LISTENING:
            LandNet *newconn

            land_net_poll(conn_listen)

            newconn = land_net_accept(conn_listen)
            if newconn:
                int i
                for i = 0; i < 8; i++:
                    # go through connected clients (left pane) to find free one
                    MyWidget *client = (MyWidget *)clients[i * 2]
                    if client->state == FREE:
                        int j
                        char packet[MAX_PACKET_SIZE]
                        int *idata = (int *)packet

                        conn_server[i] = newconn
                        conn_server[i]->buffer = land_malloc (MAX_PACKET_SIZE)
                        conn_server[i]->size = MAX_PACKET_SIZE

                        for j = 0; j < 8; j++:
                            MyWidget *other = (MyWidget *)clients[j * 2]
                            # send join messages for all already connected
                            # clients to new one
                            if other->state == TAKEN:
                                idata[0] = ID_JOIN
                                idata[1] = j
                                idata[2] = 0
                                land_net_send(conn_server[i], packet, 12)

                            # send the join message of the new one to all
                            # connected clients (including itself)
                            if conn_server[j]:
                                idata[0] = ID_JOIN
                                idata[1] = i
                                idata[2] = 0
                                land_net_send(conn_server[j], packet, 12)

                        client->state = TAKEN

                        # send who message to newly connected client
                        idata[0] = ID_WHO
                        idata[1] = i
                        land_net_send(conn_server[i], packet, 8)

                        break

                if i == 8:
                    # refuse connection (TODO better way to do this?) 
                    land_net_del(newconn)

            break
        case CONNECTING:
            land_net_poll(conn_out)
            if conn_out->state == LAND_NET_OK:
                my->state = CONNECTED
                conn_out->buffer = land_malloc(MAX_PACKET_SIZE)
                conn_out->size = MAX_PACKET_SIZE
            if conn_out->state == LAND_NET_INVALID:
                if conn_out->buffer: land_free(conn_out->buffer)
                my->state = CONNECT
                land_net_del(conn_out)
                conn_out = NULL
            break
        case CONNECTED:
            int *idata = (int *)conn_out->buffer
            int id = 0
            int got_data

            do:
                got_data = 0
                land_net_poll(conn_out)

                if conn_out->full >= 4:
                    id = idata[0]

                if id == ID_WHO && conn_out->full >= 8:
                    MyWidget *client = (MyWidget *)clients[idata[1] * 2 + 1]
                    client->state = SELF
                    land_net_flush (conn_out, 8)
                    got_data = 1

                if id == ID_JOIN && conn_out->full >= 12:
                    MyWidget *client = (MyWidget *)clients[idata[1] * 2 + 1]
                    if idata[2]:
                        client->state = FREE
                    else:
                        client->state = ANOTHER

                    land_net_flush (conn_out, 12)
                    got_data = 1

                if id == ID_PING && conn_out->full >= 16:
                    ping_out = idata[3]
                    land_net_send(conn_out, conn_out->buffer, 16)
                    land_net_flush(conn_out, 16)
                    got_data = 1

                if conn_out->state != LAND_NET_OK:
                    free(conn_out->buffer)
                    land_net_del (conn_out)
                    conn_out = NULL
                    my->state = CONNECT
                    client_clear_others()
                    break
            while (got_data)

            break

        case TAKEN:
            int *idata = (int *)conn_server[my->id]->buffer
            int id = 0
            int got_data

            do:
                got_data = 0
                land_net_poll(conn_server[my->id])
                if conn_server[my->id]->full >= 4:
                    id = idata[0]

                if id == ID_PING && conn_server[my->id]->full >= 16:
                    ping_server[my->id] = ticks - idata[2]
                    land_net_flush(conn_server[my->id], 16)
                    got_data = 1
            while (got_data)

            char packet[MAX_PACKET_SIZE]

            idata = (int *) packet
            idata[0] = ID_PING
            idata[1] = my->id
            idata[2] = ticks
            idata[3] = ping_server[my->id]
            land_net_send(conn_server[my->id], packet, 16)

            # Lost a connection 
            if conn_server[my->id]->state != LAND_NET_OK:
                free (conn_server[my->id]->buffer)
                land_net_del(conn_server[my->id])
                conn_server[my->id] = NULL
                my->state = FREE
                server_notify_lost(my->id)
            break

def my_draw(LandWidget *self):
    MyWidget *my = (MyWidget *)self

    float x, y, w, h;
    land_widget_inner(self, &x, &y, &w, &h)

    if my->state == NOTHING:
        land_text_pos(x, y)
        land_color(0, 0, 0, 1)
        land_print("%s", address)
    else:
        land_widget_theme_draw(self)
        land_text_pos(x, y)
        land_color(0, 0, 0, 1)
        land_print("%s", state_strings[my->state])

    if my->state == TAKEN:
        land_text_pos(self->box.x + self->box.w, y)
        land_color(1, 0, 0, 1)
        land_print_right("%d",  ping_server[my->id])

    if my->state == CONNECTED:
        land_text_pos(self->box.x + self->box.w, y)
        land_color(1, 0, 0, 1)
        land_print_right("%d",  ping_out)

#static def closebutton():
    #simulate_keypress ((LandKeyEscape << 8) + 27)
#    pass

LandWidgetInterface *vt

LandWidget *def my_widget_new(LandWidget *parent, int state, id):
    if not vt:
        land_widget_button_interface_initialize()
        vt = land_widget_copy_interface(land_widget_base_interface, "button")
        vt->draw = my_draw
        vt->mouse_tick = my_mouse_tick
    MyWidget *self
    land_alloc(self)
    LandWidget *widget = (LandWidget *)self
    land_widget_base_initialize(widget, parent, 0, 0, 0, 0)
    ((LandWidget *)self)->vt = vt
    self->state = state
    self->id = id

    land_widget_theme_set_minimum_size_for_text(widget, "X")
    land_widget_layout_set_expanding(widget, 1, 0)
    land_widget_theme_initialize(widget)

    return (LandWidget *)self

def create_gui():
    int w = land_display_width()
    int h = land_display_height()
    land_widget_theme_set_default(land_widget_theme_new("data/classic.cfg"))
    desktop = land_widget_panel_new(None, 0, 0, w, h)
    land_widget_reference(desktop)
    land_widget_theme_initialize(desktop)
    LandWidget *vbox = land_widget_vbox_new(desktop, 10, 10, 10, 10)
    land_widget_vbox_set_columns(vbox, 2)
    listen_widget = my_widget_new(vbox, LISTEN, 0)
    connect_widget = my_widget_new(vbox, CONNECT, 0)
    my_widget_new(vbox, NOTHING, 0)
    my_widget_new(vbox, NOTHING, 0)
    int i
    for i = 0; i < 16; i++:
        clients[i] = my_widget_new(vbox, FREE, i / 2)
    land_widget_layout(desktop)

def init(LandRunner *self):
    if land_argc > 1:
        address = land_argv[1]

    land_font_default()

    create_gui()

def tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape): land_quit()
    if land_closebutton(): land_quit()
    land_widget_tick(desktop)

    int i
    my_tick(listen_widget)
    my_tick(connect_widget)
    for i = 0; i < 16; i++:
        my_tick(clients[i])

    ticks++

def draw(LandRunner *self):
    land_widget_draw(desktop)

def done(LandRunner *self):
    int i

    for i = 0; i < 8; i++:
        if conn_server[i]:
            land_net_del(conn_server[i])

    if conn_out:
        land_net_del (conn_out)

    if conn_listen:
        land_net_del (conn_listen)

def my_main():
    land_init()
    land_set_display_parameters(320, 240,
        LAND_WINDOWED | LAND_OPENGL)
    LandRunner *runner = land_runner_new("main", init, None, tick, draw, None,
        done)
    land_set_fps(6)
    land_set_initial_runner(runner)
    land_mainloop()

land_use_main(my_main)
