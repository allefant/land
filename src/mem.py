import global stdlib, string

macro land_alloc(self) self = land_calloc(sizeof *self)

static import global stdio

#static macro LOGALL

static import log

*** "ifndef" WINDOWS
static import execinfo
*** "endif"

*** "ifdef" LAND_MEMLOG

static char const *LOGFILE = "memlog.log"

static macro MAX_BLOCKS 1024 * 1024
enum: LAND_MEMBLOCK_INFO_MAX_STACK = 32

class LandMemBlockInfo:
    void *ptr
    char const *id
    const char *file
    int line
    int size
    
    int trace_depth
    void *trace[LAND_MEMBLOCK_INFO_MAX_STACK]

static int installed = 0

static struct LandMemBlockInfo not_freed[MAX_BLOCKS]

static int _num = 0
static int _size = 0
static int _maxnum = 0
static int _maxsize = 0

static def done():
    # This function is called from atexit, so don't rely on Land still being
    # installed, e.g. logging facility.
    int n
    FILE *lf = fopen(LOGFILE, "a")
    fprintf(lf, "Memory statistics:\n")
    fprintf(lf, "Maximum number of simultanously allocated blocks: %d\n",
            _maxnum)
    fprintf(lf, "Maximum number of simultanously allocated elements: %d\n",
            _maxsize)

    fprintf(lf, "Memory leaks: %d\n", _num)
    for n = 0 while n < _num with n++:
        fprintf(lf, "%s: %d: %d elements [%s] not freed: %p\n",
                not_freed[n].file, not_freed[n].line,
                not_freed[n].size, not_freed[n].id, not_freed[n].ptr)
        fflush(lf)
        backtrace_symbols_fd(not_freed[n].trace, not_freed[n].trace_depth, fileno(lf))
        
        if not strcmp(not_freed[n].id, ""):
            fprintf(lf, "    first bytes: [")
            for int i = 0 while i < 16 with i++:
                if i >= not_freed[n].size: break
                int c = *((unsigned char *)(not_freed[n].ptr) + i)
                if c >= 32 and c <= 127:
                    fprintf(lf, "%c", c)
                else:
                    fprintf(lf, "«%d»", c)
            fprintf(lf, "]\n")
    fclose(lf);

static def install():
    installed++
    if installed == 1:
        atexit(done)

        FILE *lf = fopen(LOGFILE, "w")
        fprintf(lf, "Land MemLog\n")
        fclose(lf)

def land_memory_add(void *ptr, char const *id, int size, const char *f, int l):
    if not installed: install()
    if not ptr:
        if size:
            FILE *lf = fopen(LOGFILE, "a")
            fprintf(lf, "%s: %d: allocation of %d elements [%s] failed\n", f, l,
                size, id)
            fclose(lf)

        return

    if _num >= MAX_BLOCKS: return

    not_freed[_num].ptr = ptr
    not_freed[_num].file = f
    not_freed[_num].line = l
    not_freed[_num].id = id
    not_freed[_num].size = size

    not_freed[_num].trace_depth = backtrace(not_freed[_num].trace, LAND_MEMBLOCK_INFO_MAX_STACK)

    _num++
    _size += size
    if _num > _maxnum: _maxnum = _num
    if _size > _maxsize: _maxsize = _size
    *** "ifdef" LOGALL
    FILE *lf = fopen(LOGFILE, "a")
    fprintf(lf, "%s: %d: allocated: %d elements [%s] at %p\n",
        f, l, size, id, ptr)
    fclose(lf)
    *** "endif"
    pass

def land_memory_remove(void *ptr, char const *id, int re, const char *f, int l):
    int n
    if not installed: install()
    if not ptr:
        if re:
            *** "ifdef" LOGALL
            FILE *lf = fopen(LOGFILE, "a")
            fprintf(lf, "%s: %d: reallocated: %p [%s]\n", f, l, ptr, id)
            fclose(lf)
            *** "endif"
            return
        
        FILE *lf = fopen(LOGFILE, "a")
        fprintf(lf, "%s: %d: freed 0 pointer [%s]\n", f, l, id)
        fclose(lf)
        abort()

        return

    for n = 0 while n < _num with n++:
        if not_freed[n].ptr == ptr:
            *** "ifdef" LOGALL
            FILE *lf = fopen(LOGFILE, "a")
            fprintf(lf, "%s: %d: freed: %d elements [%s] at %p\n",
                f, l, not_freed[n].size, id, ptr)
            fclose(lf)
            *** "endif"
            _size -= not_freed[n].size
            not_freed[n] = not_freed[_num - 1]
            _num--
            return

    
    FILE *lf = fopen(LOGFILE, "a")
    fprintf(lf, "%s: %d: double freed or never allocated: %p [%s]\n", f,
        l, ptr, id)
    fclose(lf)
    
    abort()

void *def land_malloc_memlog(int size, char const *f, int l):
    void *ptr = malloc(size)
    land_memory_add(ptr, "", size, f, l)
    return ptr

void *def land_calloc_memlog(int size, char const *f, int l):
    void *ptr = calloc(1, size)
    land_memory_add(ptr, "", size, f, l)
    return ptr

void *def land_realloc_memlog(void *ptr, int size, char const *f, int l):
    void *p = realloc(ptr, size)
    land_memory_remove(ptr, "", 1, f, l)
    land_memory_add(p, "", size, f, l)
    return p

char *def land_strdup_memlog(char const *str, char const *f, int l):
    void *p = strdup(str)
    land_memory_add(p, "", strlen(p), f, l)
    return p

def land_free_memlog(void *ptr, char const *f, int l):
    land_memory_remove(ptr, "", 0, f, l)
    free(ptr)

*** "else" # LAND_MEMLOG

void *def land_malloc(int size):
    return malloc(size)

void *def land_calloc(int size):
    return calloc(1, size)

void *def land_realloc(void *ptr, int size):
    return realloc(ptr, size)

char *def land_strdup(char const *str):
    return strdup(str)

def land_free(void *ptr):
    free(ptr)

*** "endif"

global *** "ifdef" LAND_MEMLOG
macro land_malloc(x) land_malloc_memlog(x, __FILE__, __LINE__)
macro land_calloc(x) land_calloc_memlog(x, __FILE__, __LINE__)
macro land_free(x) land_free_memlog(x, __FILE__, __LINE__)
macro land_realloc(x,y) land_realloc_memlog(x, y ,__FILE__, __LINE__)
macro land_strdup(x) land_strdup_memlog(x, __FILE__, __LINE__)
global *** "endif"
