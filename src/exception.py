static import global setjmp, stdio, stdarg, stdlib
import land.common
static import land.allegro5.a5_misc

static jmp_buf exception
static char exception_string[1024]
global int (*land_exception_handler)(char const *str)
static int init = 1

def land_default_exception_handler(char const *str) -> int:
    fprintf(stderr, "%s\n", str)
    return 1

def land_exception_handler_init():
    label again
    if setjmp(exception):
        int r = land_exception_handler(exception_string)
        if not r: goto again
        abort()

def land_exception_handler_set(int (*handler)(char const *str)):
    if init:
        land_exception_handler_init()
        init = 0

    land_exception_handler = handler

#__attribute__((noreturn))
def land_exception(char const *format, ...):
    va_list args
    va_start(args, format)
    vsnprintf(exception_string, 1024, format, args)
    va_end(args)
    
    fprintf(stderr, "%s", exception_string)
    
    # for now, let's not use longjmp
    int r = land_exception_handler(exception_string)
    if r: abort()
    #longjmp(exception, 1)

def land_popup(str title, str message):
    platform_popup(title, message)
