static import global stdio, stdarg, stdlib, string, allegro, time, sys/time
static import memory

static char *logname = NULL

def land_log_overwrite(char const *name):
    FILE *f
    if logname: land_free(logname)
    logname = land_strdup(name)
    f = fopen(logname, "w")
    if f:
        fclose(f)

def land_log_set(char const *name):
    if logname: land_free(logname)
    logname = land_strdup(name)

def land_log_del():
    if logname: land_free(logname)
    logname = NULL

def land_log_new(char const *base, int unique):
    static int once = 0
    FILE *f
    int i = 0
    if logname: land_free(logname)

    logname = land_malloc(strlen(base) + 10)

    if not once:
        atexit(land_log_del)
        once++

    if unique:
        do:
            sprintf(logname, "%s%04d.log", base, i)
            f = fopen(logname, "r")
            if f: fclose(f)
            i++
        while (f)
    else:
        sprintf(logname, "%s.log", base)

    f = fopen(logname, "w")
    if f:
        fprintf(f, "******* new log *******\n")
        fclose(f)


def land_log_message_nostamp (char const *template, ...):
    if !logname: land_log_new("land", 0)
    FILE *logfile
    va_list va_args
    va_start(va_args, template)
    logfile = fopen(logname, "a")
    vfprintf(logfile, template, va_args)
    fclose(logfile)
    #vprintf(template, va_args)
    va_end(va_args)

def land_log_message(char const *template, ...):
    if !logname: land_log_new("land", 0)
    FILE *logfile
    va_list va_args
    va_start(va_args, template)
    logfile = fopen(logname, "a")
    struct timeval tv
    #ifdef ALLEGRO_WINDOWS
    tv.tv_usec = 0
    #else
    gettimeofday(&tv, NULL)
    #endif
    time_t t
    struct tm tm
    time(&t)
    tm = *gmtime(&t)
    fprintf(logfile, "%04d/%02d/%02d %02d:%02d:%02d.%06ld ",
        tm.tm_year + 1900,
        tm.tm_mon + 1,
        tm.tm_mday,
        tm.tm_hour,
        tm.tm_min,
        tm.tm_sec,
        tv.tv_usec)
    vfprintf(logfile, template, va_args)
    fclose(logfile)
    //vprintf(template, va_args)
    va_end(va_args)
