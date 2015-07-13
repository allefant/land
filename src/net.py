*** "ifndef" LAND_NO_NET
# This is a simple sockets/TCP wrapper, to exchange bytes between programs.

*** "ifdef" WINDOWS
static import global winsock2
static import global ws2tcpip
static macro SHUT_RDWR SD_BOTH
*** "else"
static import global stdlib, string, signal
static import global sys/time, sys/socket, sys/ioctl, errno, arpa/inet
static import global netdb
*** "endif"

import global unistd, stdbool
static import global stdlib, stdio
static import land.random, land.mem, land.log, land.main

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
    int sockd

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

    double timestamp
    int rate_control
    int max_rate # bytes received / second
    void *lag_simulator

static macro D(_) _

# macro DEBUG_BYTES

*** "ifdef" WINDOWS
static def cleanup():
    WSACleanup()

static def sockerror(char const *name):
    int err = WSAGetLastError()
    char const *what = "unknown"
    switch err:
        case WSAEINTR: what = "WSAEINTR"; break
        case WSAEBADF: what = "WSAEBADF"; break
        case WSAEACCES: what = "WSAEACCES"; break
        case WSAEFAULT: what = "WSAEFAULT"; break
        case WSAEINVAL: what = "WSAEINVAL"; break
        case WSAEMFILE: what = "WSAEMFILE"; break
        case WSAEWOULDBLOCK: what = "WSAEWOULDBLOCK"; break
        case WSAEINPROGRESS: what = "WSAEINPROGRESS"; break
        case WSAEALREADY: what = "WSAEALREADY"; break
        case WSAENOTSOCK: what = "WSAENOTSOCK"; break
    fprintf(stderr, "%s: %s [%d]\n", name, what, err)
*** "else"
static macro closesocket close
static macro sockerror perror
*** "endif"

static def nonblocking(LandNet *self) -> int:
    int r
    # Make non-blocking.
    *** "if" defined(WINDOWS)
    u_long a = 1
    r = ioctlsocket(self.sock, FIONBIO, &a)
    *** "else"
    int a = 1
    r = ioctl(self.sock, FIONBIO, &a)
    *** "endif"

    if r:
        sockerror("ioctl")
        closesocket(self.sock)
        return -1

    return 0

static def split_address(char const *address, char **host, int *port):
    char *colon = strrchr(address, ':')
    if colon:
        *host = land_calloc(colon - address + 1)
        strncpy(*host, address, colon - address)
        (*host)[colon - address] = '\0'
        *port = atoi(colon + 1)
    else:
        *host = land_strdup(address)
        *port = 0

static def _get_address(struct sockaddr_in sock_addr, char *address):
    if sock_addr.sin_addr.s_addr == INADDR_ANY:
            sprintf(address, "*.*.*.*")
    else:
        char *ip = (char *)&sock_addr.sin_addr.s_addr
        sprintf(address, "%d.%d.%d.%d", (unsigned char)ip[0],
            (unsigned char)ip[1], (unsigned char)ip[2],
            (unsigned char)ip[3])

    sprintf(address + strlen(address), ":%d", ntohs(sock_addr.sin_port))

def land_net_get_address(LandNet *self, int remote) -> char *:
    """
    Return either the local or remote address of the connection.
    """
    int s
    static char address[256]
    struct sockaddr_in sock_addr
    socklen_t addrlength = sizeof sock_addr

    s = (remote ? getpeername : getsockname)(self.sock,
        (struct sockaddr *)&sock_addr, &addrlength)
    if s == 0:
        _get_address(sock_addr, address)
    else:
        sprintf(address, "?:?")
    return address

def land_net_new() -> LandNet *:
    LandNet *self
    land_alloc(self)
    static int once = 1

    if once:
        *** "ifdef" WINDOWS
        WORD wVersionRequested
        WSADATA wsaData
        int err

        wVersionRequested = MAKEWORD(1, 0)
        err = WSAStartup(wVersionRequested, &wsaData)
        if err != 0:
            return NULL
        land_exit_function(cleanup)
        *** "else"
        struct sigaction sa
        sigset_t mask
        sigemptyset(&mask)
        sa.sa_handler = SIG_IGN
        sa.sa_mask = mask
        sa.sa_flags = 0
        sigaction(SIGPIPE, &sa, NULL)
        *** "endif"

        once = 0

    # Open socket. 
    if (self.sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0:
        sockerror("socket")
        return self

    nonblocking(self)

    return self

def land_net_listen(LandNet *self, char const *address):
    int r
    struct sockaddr_in sock_address
    char *host
    int port

    if self.state != LAND_NET_INVALID:
        return

    self.local_address = land_strdup(address)
    split_address(address, &host, &port)

    # Resolve hostname. 
    struct hostent *hostinfo

    if not (hostinfo = gethostbyname(host)):
        sockerror("gethostbyname")
        land_free(host)
        return

    *** "ifdef" WINDOWS
    char a = 1;
    *** "else"
    int a = 1
    *** "endif"
    setsockopt(self.sock, IPPROTO_TCP, SO_REUSEADDR, &a, sizeof(a))

    # Address to listen on. 
    sock_address.sin_family = AF_INET
    # Fill in IP (returned in network byte order by gethostbyname). 
    sock_address.sin_addr = *(struct in_addr *) hostinfo->h_addr
    # Fill in port (and convert to network byte order). 
    sock_address.sin_port = htons(port)

    r = bind(self.sock, (struct sockaddr *) &sock_address, sizeof sock_address)
    if r < 0:
        sockerror("bind")
        land_free(host)
        return

    r = listen(self.sock, SOMAXCONN)
    if r < 0:
        sockerror("listen")
        land_free(host)
        return

    self.state = LAND_NET_LISTENING

    D(land_log_message("Listening on host %s port %d (%s).\n", host, port,
        land_net_get_address(self, 0)))

    land_free(host)

static def land_net_poll_accept(LandNet *self):
    int r
    struct sockaddr_in address
    socklen_t address_length = sizeof address

    if self.accepted:
        return

    r = accept(self.sock, (struct sockaddr *) &address, &address_length)
    if r < 0:
        *** "if" defined(LINUX)
        if errno == EINTR or errno == EWOULDBLOCK or errno == EAGAIN:
            return
        *** "elif" defined(WINDOWS)
        if WSAGetLastError() == WSAEINTR or\
            WSAGetLastError() == WSAEWOULDBLOCK:
            return
        *** "endif"

        sockerror("accept")
        return

    self.accepted = land_calloc(sizeof *self->accepted)
    self.accepted->sock = r
    nonblocking(self.accepted)
    self.accepted->state = LAND_NET_OK

    D(land_log_message("Accepted connection (%s ->",
        land_net_get_address(self.accepted, 0)))
    D(land_log_message_nostamp(" %s).\n",
        land_net_get_address(self.accepted, 1)))

def land_net_accept(LandNet *self) -> LandNet *:
    if self.state == LAND_NET_LISTENING and self->accepted:
        LandNet *accepted = self.accepted
        self.accepted = NULL
        return accepted

    return NULL

def land_net_connect(LandNet *self, char const *address):
    struct sockaddr_in sock_address
    char *host
    int port

    # Resolve hostname. 
    struct hostent *hostinfo

    if self.state != LAND_NET_INVALID:
        return

    self.remote_address = land_strdup(address)
    split_address(address, &host, &port)

    if not (hostinfo = gethostbyname(host)):
        sockerror("gethostbyname")
        land_free(host)
        return

    # Address to connect to. 
    sock_address.sin_family = AF_INET
    # Fill in IP (returned in network byte order by gethostbyname). 
    sock_address.sin_addr = *(struct in_addr *) hostinfo->h_addr
    # Fill in port (and convert to network byte order). 
    sock_address.sin_port = htons(port)

    # Connect to the server. 
    if connect(self.sock, (struct sockaddr *) &sock_address,
        sizeof sock_address):
        bool err
        *** "if" defined(WINDOWS)
        err = WSAGetLastError() != WSAEINPROGRESS and\
            WSAGetLastError() != WSAEWOULDBLOCK
        *** "else"
        err = errno != EINPROGRESS
        *** "endif"
        if err:
            sockerror("connect")
            closesocket(self.sock)
            land_free(host)
            return


    self.state = LAND_NET_CONNECTING

    D(land_log_message("Connecting to host %s port %d (from %s).\n", host, port,
        land_net_get_address(self, 0)))

    land_free(host)

static def land_net_poll_connect(LandNet *self):
    int r
    struct timeval tv
    fd_set ds

    FD_ZERO(&ds)
    FD_SET((unsigned)self->sock, &ds)
    tv.tv_sec = 0
    tv.tv_usec = 0

    # TODO: on Windows, need to check exception descriptors to know if connection failed? 
    r = select(FD_SETSIZE, NULL, &ds, NULL, &tv)
    if r > 0:
        *** "ifdef" WINDOWS
        char a;
        int as = sizeof a
        *** "else"
        socklen_t a, as = sizeof a
        *** "endif"
        if getsockopt(self.sock, SOL_SOCKET, SO_ERROR, &a, &as) == 0:
            if a != 0:
                errno = a
                self.state = LAND_NET_INVALID
                sockerror("select(connect)")
                return


        self.state = LAND_NET_OK
        D(land_log_message("Connected (%s ->",
            land_net_get_address(self, 0)))
        D(land_log_message_nostamp(" %s).\n",
            land_net_get_address(self, 1)))
        return

    bool err
    *** "if" defined WINDOWS
    err = WSAGetLastError() != WSAEINTR
    *** "else"
    err = r < 0 and errno != EINTR
    *** "endif"
    if err:
        sockerror("select")
        closesocket(self.sock)
        return

*** "ifdef" DEBUG_BYTES
static def debug_packet(char const *buffer, int size):
    land_log_message("Sent %d bytes: ", size)
    int i
    for i = 0 while i < size with i++:
        int c = (unsigned char)buffer[i];
        land_log_message_nostamp("%d[%c],", c, c >= 32 and c <= 127 ? c : '.')
    land_log_message_nostamp("\n")
*** "endif"

# FIXME: this is unfinished, it has to use a proper dynamic data structure to
# hold the packets
static class LagSimulator:
    int ringpos
    int ringpos2
    char packets[256 * 256]
    int size[256]
    double t[256]
    double delay
    double jitter
    
static def lag_simulator_new(double delay, double jitter) -> LagSimulator *:
    LagSimulator *self
    land_alloc(self)
    self.delay = delay
    self.jitter = jitter
    return self

static def lag_simulator_add(LandNet *net, char const *packet, int size):
    LagSimulator *self = net->lag_simulator
    double t = land_get_time()
    if packet:
        memcpy(self.packets + self->ringpos * 256, packet, size)
        self.size[self->ringpos] = size
        self.t[self->ringpos] = t + land_rnd(-self->jitter, self->jitter)
        self.ringpos++
        if self.ringpos == 256: self->ringpos = 0
    while self.ringpos2 != self->ringpos:
        int i = self.ringpos2
        if t >= self.t[i] + self->delay:
            # Oldest packet should get sent
            self.ringpos2++
            if self.ringpos2 == 256: self->ringpos2 = 0
            net->lag_simulator = None # avoid recursion
            packet = self.packets + i * 256
            size = self.size[i]
            land_net_send(net, packet, size)
            net->lag_simulator = self
        else:
            break

def land_net_lag_simulator(LandNet *self, double delay, double jitter):
    self.lag_simulator = lag_simulator_new(delay, jitter)

def land_net_limit_receive_rate(LandNet *self, int rate):
    self.max_rate = rate

static def _create_datagram_socket(LandNet *self) -> int:
    # Create socket
    if not self.sockd:
        int r
        r = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP)
        if r >= 0:
            self.sockd = r
        else:
            return 1

        *** "if" defined(WINDOWS)
        u_long b = 1
        r = ioctlsocket(self.sockd, FIONBIO, &b)
        *** "else"
        int b = 1
        r = ioctl(self.sockd, FIONBIO, &b)
        *** "endif"
        if r < 0:
            sockerror("ioctl")

        *** "ifdef" WINDOWS
        char a = 1;
        *** "else"
        int a = 1
        *** "endif"
        r = setsockopt(self.sockd, SOL_SOCKET, SO_BROADCAST, &a, sizeof(a))
        if r < 0:
            sockerror("setsockopt")

    return 0


static def _send_datagram(LandNet *self, char const *address, *packet, int size) -> int:

    # Resolve hostname.
    char *host
    int port
    split_address(address, &host, &port)
    struct hostent *hostinfo = gethostbyname(host)
    if not hostinfo:
        land_free(host)
        return 0

    struct sockaddr_in sock_address
    # Address to connect to. 
    sock_address.sin_family = AF_INET
    # Fill in IP (returned in network byte order by gethostbyname). 
    sock_address.sin_addr = *(struct in_addr *) hostinfo->h_addr
    # Fill in port (and convert to network byte order). 
    sock_address.sin_port = htons(port)

    int r = sendto(self.sockd, packet, size, 0,
        (struct sockaddr *) &sock_address, sizeof sock_address);

    land_free(host)
    return r

def land_net_send_datagram(LandNet *self, char const *address, *packet,
    int size) -> int:
    """
    [experimental]
    This is to directly send a datagram to some address. This is an experimental
    feature and for now, you should use land_net_send when possible.
    """
    _create_datagram_socket(self)

    return _send_datagram(self, address, packet, size)

def land_net_recv_datagram(LandNet *self, int port,
    char **address, *packet, int size) -> int:
    """
    [experimental]
    Receives a datagram. Returns the number of received bytes (less than or
    equal to size), or 0 if there's no datagram to be received. If address is
    not None and the return value is > 0, it will point to a static buffer
    containing the source address. (If you need that address for anything,
    copy it to your own buffer immediately.)
    """
    _create_datagram_socket(self)

    if port:
        struct sockaddr_in laddr
        laddr.sin_family = AF_INET
        laddr.sin_port = htons(port)
        laddr.sin_addr.s_addr = INADDR_ANY

        bind(self.sockd, (struct sockaddr *)&laddr, sizeof laddr)

    struct sockaddr_in sock_address
    socklen_t addrsize = sizeof sock_address
    int r = recvfrom(self.sockd, packet, size, 0,
        (struct sockaddr *) &sock_address, &addrsize);

    if r > 0:
        if address:
            static char static_address[256]
            _get_address(sock_address, static_address)
            *address = static_address
        return r

    return 0

# FIXME: for big sends (say, some MB), this will spinloop
def land_net_send(LandNet *self, char const *buffer, size_t size):
    size_t bytes = 0
    int r = 0

    if self.state != LAND_NET_OK:
        return
        
    if self.lag_simulator:
        lag_simulator_add(self, buffer, size)
        return

    # TODO: hackish? 
    while 1:
        r = send(self.sock, buffer + bytes, size - bytes, 0)

        if r < 0:
            *** "if" defined WINDOWS
            if WSAGetLastError() == WSAEINTR or\
                WSAGetLastError() == WSAEWOULDBLOCK:
                r = 0
            else:
                sockerror("send")
                return
            *** "else"
            if errno == EINTR or errno == EWOULDBLOCK or errno == EAGAIN:
                r = 0
            else:
                sockerror("send")
                return
            *** "endif"

        bytes += r

        if bytes < size:
            continue

        break

    *** "ifdef" DEBUG_BYTES
    debug_packet(buffer, size)
    *** "endif"

def land_net_buffer(LandNet *self, char *buffer, size_t size):
    """
    Assign a networking buffer to use. This buffer keeps being owned by you,
    Land will never delete it on its own.
    """
    self.buffer = buffer
    self.size = size
    self.full = 0

# Call this to discard an amount of bytes from the back of the receive queue.
def land_net_flush(LandNet *self, size_t size):
    if size == 0:
        self.full = 0
    else:
        if self.full >= size:
            memmove(self.buffer, self->buffer + size, self->full - size)
        self.full -= size

# Call this to add bytes to the front of the receive queue.
static def land_net_poll_recv(LandNet *self):
    int r

    if self.size == 0 or self->full == self->size:
        return

    int max = self.size - self->full
    if self.max_rate:
        double t = land_get_time()
        double dt = t - self.timestamp
        if dt > 1: dt = 1
        if max > self.max_rate * dt:
            max = self.max_rate * dt
        self.timestamp = t
        if max == 0: return

    r = recv(self.sock, self->buffer + self->full, max, 0)

    if r < 0:
        *** "if" defined WINDOWS
        bool err = WSAGetLastError() != WSAEINTR and\
            WSAGetLastError() != WSAEWOULDBLOCK
        *** "else"
        bool err = errno != EINTR and errno != EWOULDBLOCK and errno != EAGAIN
        *** "endif"
        if err:
            sockerror("recv")
            return

        return

    if r == 0: # Remote shut down.
        self.state = LAND_NET_INVALID

    self.full += r

    *** "ifdef" DEBUG_BYTES
    land_log_message("Received %d bytes: ", r)
    int i
    for i = 0 while i < r with i++:
        int c = (unsigned char)self.buffer[self->full - r + i]
        land_log_message_nostamp("%d[%c],", c, c >= 32 and c <= 128 ? c : '.')
    land_log_message_nostamp("\n")
    *** "endif"

def land_net_disconnect(LandNet *self):
    if self.state == LAND_NET_INVALID:
        return

    # Shutdown connection. 
    if shutdown(self.sock, SHUT_RDWR):
        sockerror("shutdown")
        return

    self.state = LAND_NET_INVALID

def land_net_del(LandNet *self):
    """
    Deletes a connection. Make sure to reclaim any buffers you have assigned
    to it first.
    """
    land_net_disconnect(self)

    # Close socket. 
    if closesocket(self.sock):
        sockerror("close");

    if self.local_address: land_free(self->local_address)
    if self.remote_address: land_free(self->remote_address)

    land_free(self)

def land_net_poll(LandNet *self):
    switch(self.state):
        case LAND_NET_INVALID: break
        case LAND_NET_LISTENING: land_net_poll_accept(self); break
        case LAND_NET_CONNECTING: land_net_poll_connect(self); break
        case LAND_NET_OK:
            if self.lag_simulator: lag_simulator_add(self, None, 0)
            land_net_poll_recv(self);
            break
*** "endif"
