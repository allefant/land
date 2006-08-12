static import global setjmp, stdio, stdarg, stdlib

static jmp_buf exception
static char exception_string[1024]
global int (*land_exception_handler)(char const *str)
static int init = 1

int def land_default_exception_handler(char const *str):
    fprintf(stderr, "%s\n", str)
    return 1

def land_exception_handler_init():
    label again
    if setjmp(exception):
        int r = land_exception_handler(exception_string)
        if !r: goto again
        abort()


def land_exception_handler_set(int (*handler)(char const *str)):
    if init:
        land_exception_handler_init()
        init = 1

    land_exception_handler = handler

#__attribute__((noreturn))
def land_exception(char const *template, ...):
    va_list args
    va_start(args, template)
    vsnprintf(exception_string, 1024, template, args)
    va_end(args)
    
    fprintf(stderr, "%s", exception_string)
    
    # for now, let's not use longjmp
    int r = land_exception_handler(exception_string)
    if r: abort()
    #longjmp(exception, 1)