#ifdef _PROTOTYPE_

#include <stdlib.h>
#include <string.h>

#ifndef LAND_MEMLOG

 void *land_malloc(int size);
 void *land_calloc(int size);
 void *land_realloc(void *ptr, int size);
 char *land_strdup(char const *str);
 void land_free(void *ptr);

#endif

#ifdef LAND_MEMLOG

#define land_malloc(x) land_malloc_memlog(x, __FILE__, __LINE__)
#define land_calloc(x) land_calloc_memlog(x, __FILE__, __LINE__)
#define land_free(x) land_free_memlog(x, __FILE__, __LINE__)
#define land_realloc(x,y) land_realloc_memlog(x, y ,__FILE__, __LINE__)
#define land_strdup(x) land_strdup_memlog(x, __FILE__, __LINE__)

#endif

#define land_alloc(self); self = land_calloc(sizeof *self);

#endif /* _PROTOTYPE_ */

#include <stdio.h>

//#define LOGALL

#include "memory.h"
#include "log.h"

#ifdef LAND_MEMLOG

#define LOGFILE "memlog.log"

#define MAX_BLOCKS 1024 * 1024

struct LandMemBlockInfo
{
    void *ptr;
    char const *id;
    const char *file;
    int line;
    int size;
};

static int installed = 0;

static struct LandMemBlockInfo not_freed[MAX_BLOCKS];

static int _num = 0;
static int _size = 0;
static int _maxnum = 0;
static int _maxsize = 0;

static void done(void);

static void install(void)
{
    installed++;
    if (installed == 1)
    {
        atexit(done);
        {
            FILE *lf = fopen(LOGFILE, "w");
            fprintf(lf, "Land MemLog\n");
            fclose(lf);
        }
    }
}

static void done(void)
{
    /* This function is called from atexit, so don't rely on Land still being
     * installed, e.g. logging facility.
     */
    int n;
    FILE *lf = fopen(LOGFILE, "a");
    {
        fprintf(lf, "Memory statistics:\n");
        fprintf(lf, "Maximum number of simultanously allocated blocks: %d\n",
                _maxnum);
        fprintf(lf, "Maximum number of simultanously allocated bytes: %d\n",
                _maxsize);
    }
    fprintf(lf, "Memory leaks: %d\n", _num);
    for (n = 0; n < _num; n++)
    {
        fprintf(lf, "%s: %d: %d bytes [%s] not freed: %p\n",
                not_freed[n].file, not_freed[n].line,
                not_freed[n].size, not_freed[n].id, not_freed[n].ptr);
    }
}

void land_memory_add(void *ptr, char const *id, int size, const char *f, int l)
{
    if (!installed)
        install();
    if (!ptr)
    {
        if (size)
        {
            FILE *lf = fopen(LOGFILE, "a");
            fprintf(lf, "%s: %d: allocation of %d bytes [%s] failed\n", f, l,
                size, id);
            fclose(lf);
        }
        return;
    }
    not_freed[_num].ptr = ptr;
    not_freed[_num].file = f;
    not_freed[_num].line = l;
    not_freed[_num].id = id;
    not_freed[_num].size = size;
    _num++;
    _size += size;
    if (_num > _maxnum)
        _maxnum = _num;
    if (_size > _maxsize)
        _maxsize = _size;
#ifdef LOGALL
    {
        FILE *lf = fopen(LOGFILE, "a");
        fprintf(lf, "%s: %d: allocated: %d bytes [%s] at %p\n",
            f, l, size, id, ptr);
        fclose(lf);
    }
#endif
}

void land_memory_remove(void *ptr, char const *id, int re, const char *f, int l)
{
    int n;
    if (!installed)
        install();
    if (!ptr)
    {
        if (re)
        {
#ifdef LOGALL
            {
                FILE *lf = fopen(LOGFILE, "a");
                fprintf(lf, "%s: %d: reallocated: %p [%s]\n", f, l, ptr, id);
                fclose(lf);
            }
#endif 
            return;
        }
        {
            FILE *lf = fopen(LOGFILE, "a");
            fprintf(lf, "%s: %d: freed 0 pointer [%s]\n", f, l, id);
            fclose(lf);
        }
        return;
    }
    for (n = 0; n < _num; n++)
    {
        if (not_freed[n].ptr == ptr)
        {
#ifdef LOGALL
            {
                FILE *lf = fopen(LOGFILE, "a");
                fprintf(lf, "%s: %d: freed: %d bytes [%s] at %p\n",
                        f, l, not_freed[n].size, id, ptr);
                fclose(lf);
            }
#endif
            _size -= not_freed[n].size;
            not_freed[n] = not_freed[_num - 1];
            _num--;
            return;
        }
    }
    {
        FILE *lf = fopen(LOGFILE, "a");
        fprintf(lf, "%s: %d: double freed or never allocated: %p [%s]\n", f,
                l, ptr, id);
        fclose(lf);
    }
}

void *land_malloc_memlog(int size, char const *f, int l)
{
    void *ptr = malloc(size);
    land_memory_add(ptr, "", size, f, l);
    return ptr;
}

void *land_calloc_memlog(int size, char const *f, int l)
{
    void *ptr = calloc(1, size);
    land_memory_add(ptr, "", size, f, l);
    return ptr;
}

void *land_realloc_memlog(void *ptr, int size, char const *f, int l)
{
    void *p = realloc(ptr, size);
    land_memory_remove(ptr, "", 1, f, l);
    land_memory_add(p, "", size, f, l);
    return p;
}

char *land_strdup_memlog(char const *str, char const *f, int l)
{
    void *p = strdup(str);
    land_memory_add(p, "", strlen(p), f, l);
    return p;
}

void land_free_memlog(void *ptr, char const *f, int l)
{
    free(ptr);
    land_memory_remove(ptr, "", 0, f, l);
}

#else

 void *land_malloc(int size)
{
    return malloc(size);
}

 void *land_calloc(int size)
{
    return calloc(1, size);
}

 void *land_realloc(void *ptr, int size)
{
    return realloc(ptr, size);
}

 char *land_strdup(char const *str)
{
    return strdup(str);
}

 void land_free(void *ptr)
{
    free(ptr);
}

#endif
