#ifdef _PROTOTYPE_
#endif /* _PROTOTYPE_ */

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>

#include "log.h"

static char *logname = NULL;

void
land_log_overwrite(char const *name)
{
    FILE *f;
    if (logname)
        free(logname);
    logname = strdup(name);
    f = fopen(logname, "w");
    if (f)
    {
        fclose(f);
    }
}

void
land_log_set(char const *name)
{
    if (logname)
        free(logname);
    logname = strdup(name);
}

void
land_log_new(char const *base, int unique)
{
    FILE *f;
    int i = 0;
    if (logname)
        free(logname);

    logname = malloc(strlen(base) + 10);
    if (unique)
    {
        do
        {
            sprintf(logname, "%s%04d.log", base, i);
            f = fopen(logname, "r");
            if (f)
                fclose(f);
            i++;
        }
        while (f);
    }
    else
    {
        sprintf(logname, "%s.log", base);
    }
    f = fopen(logname, "w");
    if (f)
    {
        fprintf(f, "******* new log *******\n");
        fclose(f);
    }
}

void
land_log_msg_nostamp (char const *template, ...)
{
     if (!logname)
        land_log_new("land", 0);
    FILE *logfile;
    va_list va_args;
    va_start(va_args, template);
    logfile = fopen(logname, "a");
    vfprintf(logfile, template, va_args);
    fclose(logfile);
    //vprintf(template, va_args);
    va_end(va_args);
}

void
land_log_msg (char const *template, ...)
{
    if (!logname)
        land_log_new("land", 0);
    FILE *logfile;
    va_list va_args;
    va_start(va_args, template);
    logfile = fopen(logname, "a");
    struct timeval tv;
    gettimeofday(&tv, NULL);
    time_t t;
    struct tm tm;
    time(&t);
    gmtime_r(&t, &tm);
    fprintf(logfile, "%04d/%02d/%02d %02d:%02d:%02d.%06ld ",
        tm.tm_year + 1900,
        tm.tm_mon + 1,
        tm.tm_mday,
        tm.tm_hour,
        tm.tm_min,
        tm.tm_sec,
        tv.tv_usec);
    vfprintf(logfile, template, va_args);
    fclose(logfile);
    //vprintf(template, va_args);
    va_end(va_args);
}

