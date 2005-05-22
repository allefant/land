#include <setjmp.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

#ifdef _PROTOTYPE_

#endif /* _PROTOTYPE_ */

#include "exception.h"

static jmp_buf exception;
static char exception_string[1024];
int (*land_exception_handler)(char const *str);
static int init = 1;

int land_default_exception_handler(char const *str)
{
    fprintf(stderr, "%s\n", str);
    return 1;
}

void land_exception_handler_init(void)
{
again:
    if (setjmp(exception))
    {
        int r = land_exception_handler(exception_string);
        if (!r)
            goto again;
        abort();
    }
}

void land_exception_handler_set(int (*handler)(char const *str))
{
    if (init)
    {
        land_exception_handler_init();
        init = 1;
    }
    land_exception_handler = handler;
}

void __attribute__((noreturn)) land_exception(char const *template, ...)
{
    va_list args;
    va_start(args, template);
    vsnprintf(exception_string, 1024, template, args);
    va_end(args);
    longjmp(exception, 1);
}

