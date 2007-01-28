macro land_method(_returntype, _name, _params) _returntype (*_name)_params
macro land_call_method(self, method, params) if (self->vt->method) self->vt->method params

static import global land

char *def land_read_text(char const *filename):
    PACKFILE *pf = pack_fopen(filename, "r")
    int s = 1
    char *buf = land_malloc(s)
    int n = 0
    while 1:
        int c = pack_getc(pf)
        if c <= 0: break
        buf[n] = c
        n++
        if n >= s:
            s *= 2
            buf = land_realloc(buf, s)
    buf[n] = 0
    n++
    buf = land_realloc(buf, n)
    return buf
    