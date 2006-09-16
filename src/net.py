# This is a simple sockets/TCP wrapper, to exchange bytes between programs.

import global land, unistd

#ifdef WINDOWS
static import global winsock
#endif

static import global sys/time, sys/socket, sys/ioctl, errno, arpa/inet, netdb,\
    signal

# Pseudocode for server:
# 
# land_net_new
# land_net_buffer
# land_net_listen
# while 1:
#     land_net_accept
#     land_net_flush
#     land_net_send
#     land_net_poll
# land_net_disconnect
# land_net_del
#
# Pseudocode for client:
# 
# land_net_new
# land_net_buffer
# land_net_connect
# while 1:
#     land_net_flush
#     land_net_send
#     land_net_poll
# land_net_disconnect
# land_net_del
#

enum LandNetState:
    LAND_NET_INVALID
    LAND_NET_LISTENING
    LAND_NET_CONNECTING
    LAND_NET_OK

class LandNet:
    int sock

    LandNetState state
    char *local_address
    char *remote_address

    LandNet *accepted

    # New data are appended to the buffer (in land_net_poll), until it is full.
    # If you read data, start with byte 0, and then call land_net_flush with
    # the amount of data read to make room in the buffer again.
    char *buffer
    size_t size
    size_t full

static macro D(_) _

# #define DEBUG_BYTES

#ifdef WINDOWS
static int once = 1
static def cleanup():
    WSACleanup()
#else
static macro closesocket close
#endif

static int def nonblocking(LandNet *self):
    int r
    # Make non-blocking.
    #if defined WINDOWS
    u_long a = 1
    r = ioctlsocket (self->sock, FIONBIO, &a)
    #else
    u_long a = 1
    r = ioctl (self->sock, FIONBIO, &a)
    #endif

    if r:
        perror ("ioctl")
        closesocket (self->sock)
        return -1

    return 0

static def split_address(char const *address, char **host, int *port):
    char *colon = strrchr (address, ':')
    if colon:
        *host = malloc (colon - address + 1)
        strncpy (*host, address, colon - address)
        (*host)[colon - address] = '\0'
        *port = atoi (colon + 1)
    else:
        *host = strdup (address)
        *port = 0

static char *def land_net_get_address(LandNet *self, int remote):
    int s
    static char address[256]
    struct sockaddr_in sock_addr
    size_t addrlength = sizeof sock_addr
    char *ip
    s = (remote ? getpeername : getsockname)(self->sock,
        (struct sockaddr *)&sock_addr, &addrlength)
    if s == 0:
        if sock_addr.sin_addr.s_addr == INADDR_ANY:
            sprintf (address, "*.*.*.*")

        else:
            ip = (char *)&sock_addr.sin_addr.s_addr
            sprintf(address, "%d.%d.%d.%d", (unsigned char)ip[0],
                (unsigned char)ip[1], (unsigned char)ip[2],
                (unsigned char)ip[3])

        sprintf(address + strlen (address), ":%d", ntohs(sock_addr.sin_port))

    else:
        sprintf(address, "?:?")
    return address

LandNet *def land_net_new():
    LandNet *self
    land_alloc(self)
    static int once = 1

    if once:
        #ifdef WINDOWS
        WORD wVersionRequested
        WSADATA wsaData
        int err

        wVersionRequested = MAKEWORD (1, 0)
        err = WSAStartup (wVersionRequested, &wsaData)
        if err != 0:
            return NULL
        land_exit_function(cleanup)
        #else
        struct sigaction sa
        sigset_t mask
        sigemptyset (&mask)
        sa.sa_handler = SIG_IGN
        sa.sa_mask = mask
        sa.sa_flags = 0
        sigaction (SIGPIPE, &sa, NULL)
        #endif

        once = 0

    # Open socket. 
    if (self->sock = socket (PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0:
        perror("socket")
        return self

    nonblocking (self)

    return self

def land_net_listen(LandNet *self, char const *address):
    int r
    struct sockaddr_in sock_address
    char *host
    int port

    if self->state != LAND_NET_INVALID:
        return

    self->local_address = strdup (address)
    split_address(address, &host, &port)

    # Resolve hostname. 
    struct hostent *hostinfo

    if not (hostinfo = gethostbyname (host)):
        free (host)
        perror("gethostbyname")
        return

    free (host)
    
    int a = 1
    setsockopt(self->sock, IPPROTO_TCP, SO_REUSEADDR, &a, sizeof(a))

    # Address to listen on. 
    sock_address.sin_family = AF_INET
    # Fill in IP (returned in network byte order by gethostbyname). 
    sock_address.sin_addr = *(struct in_addr *) hostinfo->h_addr
    # Fill in port (and convert to network byte order). 
    sock_address.sin_port = htons (port)

    r = bind(self->sock, (struct sockaddr *) &sock_address, sizeof sock_address)
    if r < 0:
        perror ("bind")
        return

    r = listen (self->sock, SOMAXCONN)
    if r < 0:
        perror ("listen")
        return

    self->state = LAND_NET_LISTENING

    D(land_log_message ("Listening on host %s port %d (%s).\n", host, port,
        land_net_get_address (self, 0)))

static def land_net_poll_accept(LandNet *self):
    int r
    struct sockaddr_in address
    socklen_t address_length = sizeof address

    if self->accepted:
        return

    r = accept (self->sock, (struct sockaddr *) &address, &address_length)
    if r < 0:
        #if defined LINUX
        if errno == EINTR or errno == EWOULDBLOCK or errno == EAGAIN:
        #elif defined WINDOWS
        if WSAGetLastError () == WSAEINTR or\
            WSAGetLastError () == WSAEWOULDBLOCK:
        #endif
            return

        perror ("accept")
        return

    self->accepted = calloc (1, sizeof *self->accepted)
    self->accepted->sock = r
    nonblocking (self->accepted)
    self->accepted->state = LAND_NET_OK

    D(land_log_message ("Accepted connection (%s ->",
        land_net_get_address(self->accepted, 0)))
    D(land_log_message_nostamp (" %s).\n",
        land_net_get_address(self->accepted, 1)))

LandNet *def land_net_accept(LandNet *self):
    if self->state == LAND_NET_LISTENING and self->accepted:
        LandNet *accepted = self->accepted
        self->accepted = NULL
        return accepted

    return NULL

def land_net_connect(LandNet *self, char const *address):
    struct sockaddr_in sock_address
    char *host
    int port

    # Resolve hostname. 
    struct hostent *hostinfo

    if self->state != LAND_NET_INVALID:
        return

    self->remote_address = strdup (address)
    split_address (address, &host, &port)

    if not (hostinfo = gethostbyname (host)):
        free (host)
        perror ("gethostbyname")
        return

    # Address to connect to. 
    sock_address.sin_family = AF_INET
    # Fill in IP (returned in network byte order by gethostbyname). 
    sock_address.sin_addr = *(struct in_addr *) hostinfo->h_addr
    # Fill in port (and convert to network byte order). 
    sock_address.sin_port = htons (port)

    # Connect to the server. 
    if connect(self->sock, (struct sockaddr *) &sock_address,
        sizeof sock_address):
        #if defined WINDOWS
        if WSAGetLastError () != WSAEINPROGRESS:
        #else
        if errno != EINPROGRESS:
        #endif
            perror ("connect")
            closesocket (self->sock)
            free (host)
            return


    self->state = LAND_NET_CONNECTING

    D(land_log_message("Connecting to host %s port %d (from %s).\n", host, port,
        land_net_get_address(self, 0)))

    free (host)

static def land_net_poll_connect(LandNet *self):
    int r
    struct timeval tv
    fd_set ds

    FD_ZERO (&ds)
    FD_SET (self->sock, &ds)
    tv.tv_sec = 0
    tv.tv_usec = 0

    # TODO: on Windows, need to check exception descriptors to know if connection failed? 
    r = select (FD_SETSIZE, NULL, &ds, NULL, &tv)
    if r > 0:
        unsigned int a, as = sizeof a
        if getsockopt (self->sock, SOL_SOCKET, SO_ERROR, &a, &as) == 0:
            if a != 0:
                errno = a
                self->state = LAND_NET_INVALID
                perror ("select(connect)")
                return


        self->state = LAND_NET_OK
        D(land_log_message("Connected (%s ->",
            land_net_get_address (self, 0)))
        D(land_log_message_nostamp(" %s).\n",
            land_net_get_address (self, 1)))
        return

    #if defined WINDOWS
    if WSAGetLastError () != WSAEINTR:
    #else
    if r < 0 && errno != EINTR:
    #endif
        perror ("select")
        closesocket (self->sock)
        return

def land_net_send (LandNet *self, char const *buffer, size_t size):
    size_t bytes = 0
    int r = 0

    if self->state != LAND_NET_OK:
        return

    # TODO: hackish? 
    while 1:
        r = send (self->sock, buffer + bytes, size - bytes, 0)

        if r < 0:
            #if defined WINDOWS
            if WSAGetLastError () == WSAEINTR or\
                WSAGetLastError () == WSAEWOULDBLOCK:
                r = 0
            else:
                perror ("send")
                return
            #else
            if errno == EINTR or errno == EWOULDBLOCK or errno == EAGAIN:
                r = 0
            else:
                perror ("send")
                return
            #endif

        bytes += r

        if bytes < size:
            continue

        break

    #ifdef DEBUG_BYTES
    land_log_message("Sent %d bytes: ", size)
    int i
    for i = 0; i < r; i++:
        int c = (unsigned char)buffer[i];
        land_log_message_nostamp("%d[%c],", c, c >= 32 && c <= 127 ? c : '.')
    land_log_message_nostamp("\n")
    #endif

def land_net_buffer(LandNet *self, char *buffer, size_t size):
    self->buffer = buffer
    self->size = size
    self->full = 0

# Call this to discard an amount of bytes from the back of the receive queue.
def land_net_flush(LandNet *self, size_t size):
    if size == 0:
        self->full = 0
    else:
        if self->full > size:
            memmove (self->buffer, self->buffer + size, self->full - size)
        self->full -= size

# Call this to add bytes to the front of the receive queue.
static def land_net_poll_recv(LandNet *self):
    int r

    if self->size == 0 or self->full == self->size:
        return

    r = recv (self->sock, self->buffer + self->full, self->size - self->full, 0)

    if r < 0:
        #if defined WINDOWS
        if WSAGetLastError () != WSAEINTR &&
            WSAGetLastError () != WSAEWOULDBLOCK:
        #else
        if errno != EINTR && errno != EWOULDBLOCK && errno != EAGAIN:
        #endif
            perror ("recv")
            return

        return

    if r == 0: # Remote shut down.
        self->state = LAND_NET_INVALID

    self->full += r

    #ifdef DEBUG_BYTES
    land_log_message("Received %d bytes: ", r)
    int i
    for i = 0; i < r; i++:
        int c = (unsigned char)self->buffer[self->full - r + i]
        land_log_message_nostamp ("%d[%c],", c, c >= 32 && c <= 128 ? c : '.')
    land_log_message_nostamp("\n")
    #endif

def land_net_disconnect(LandNet *self):
    if self->state == LAND_NET_INVALID:
        return

    # Shutdown connection. 
    if shutdown (self->sock, SHUT_RDWR):
        perror ("shutdown")
        return

    self->state = LAND_NET_INVALID

def land_net_del(LandNet *self):
    land_net_disconnect(self)

    # Close socket. 
    if closesocket (self->sock):
        perror ("close"); 

    land_free(self)

def land_net_poll(LandNet *self):
    switch(self->state):
        case LAND_NET_INVALID: break
        case LAND_NET_LISTENING: land_net_poll_accept(self); break
        case LAND_NET_CONNECTING: land_net_poll_connect(self); break
        case LAND_NET_OK: land_net_poll_recv(self); break