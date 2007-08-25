import land

"""
= Land Magic =

== Variables ==

There are four possibilities where a value comes from:
- A global variable. This is accessed at runtime by specifying its name.
- A local variable. This is a register accessed by its index (usually 0..127)
  relative to the function.
- A parent variable. This is a local variable from the scope of the function
  inside which the current one was defined, or a recursive parent thereof. It
  is accessed by name, like a global.
- A constant. It is accessed by its index (usually 128..255) in the current
  function.

== Function ==

When calling a function, a new call frame is created for it. Each function
records the number of locals it needs, so that's how much are allocated. It
also keeps a reference to the parent frame.

When defining a function, a function object is created. This will reference
the static function definition with the code as output by the compiler, but
also add a reference to the current call frame. This allows access to
local variables within this frame for functions inside other functions
(closures).

What this also means is, when a function returns, we cannot necessarily destroy
its call frame, as it may be referenced by some function object.

For garbage collection, the following could be done from time to time:
- Go through all objects and mark them as unreachable.
- Go through all currently visible variables and mark the objects as reachable,
  then go through all objects referenced by them and recursively mark them
  reachable as well.
- Go through all objects again, finalize the ones marked as unreachable.

"""

enum LM_DataType:
    LM_TYPE_NON
    LM_TYPE_BOO
    LM_TYPE_INT
    LM_TYPE_NUM # A number.
    LM_TYPE_DAT
    LM_TYPE_STR # A string.
    LM_TYPE_DEF # A definition.
    LM_TYPE_FUN # A frame.
    LM_TYPE_ARR
    LM_TYPE_LIS
    LM_TYPE_DIC # A dictionary.
    LM_TYPE_QUE
    LM_TYPE_USE # A user provided object. When a user object is garbage
                # collected, there is currently no mechanism to call a
                # user provided destructor, so for now use this only to pass
                # in static data.

# x y z is registers (0..127) or constants (-128..-1)
#       Note: 0 is reserved as return-register, -128 as none constant.
# A B C is inline values
#
enum LM_Opcode:
    # miscellaneous
    OPCODE_NOP # NOP ? ? ? does nothing
    OPCODE_USE # USE x y C Calls a user callback named x (y and C like FUN)
    OPCODE_GEU # SEU x y z Set x.y to z, where x names a user callback
    OPCODE_SEU # GEU x y z Set x to y.z, where y names a user callback
    OPCODE_END # END ? ? ? stops the virtual machine
    OPCODE_PAU # PAU ? ? ? pauses the virtual machine

    # output
    OPCODE_OUT # OUT x ? ? outputs x
    OPCODE_FLU # OUT x ? ? outputs x and a newline

    # variables/objects
    OPCODE_GET # GET x y ? read value of global variable named y into x
    OPCODE_PUT # PUT x y ? global variable named x gets the value of y
    OPCODE_ASS # ASS x y ? copy the value of y to x (same as ARG)
    OPCODE_ARG # ARG x y ? push y as parameter into x (same as ASS)
    OPCODE_SET # SET x y z set x.y to z
    OPCODE_DOT # DOT x y z set x to y.z
    OPCODE_DEF # DEF x B ? put definition B into x
    OPCODE_NEW # NEW x ? ? create a new dictionay and put it into x

    # jumps
    OPCODE_HOP # HOP ? <B> do a relative jump
    OPCODE_BRA # BRA x <B> do a relative jump if x is true
    OPCODE_AND # AND x <B> do a relative jump if x is false
    OPCODE_FUN # FUN x y C calls function in x with C parameters, first is y
    OPCODE_RET # RET x ? ? return from the current function, with value x

    # binary operations
    OPCODE_ADD # ADD x y z does x = y + z
    OPCODE_SUB
    OPCODE_MUL
    OPCODE_DIV
    OPCODE_MOD
    OPCODE_POW
    OPCODE_BOR
    OPCODE_XOR
    OPCODE_BAN
    OPCODE_MAX
    OPCODE_MIN
    OPCODE_LOW
    OPCODE_BIG
    OPCODE_SAM

    # unary operations
    OPCODE_NEG # NEG x y ? does x = -y
    OPCODE_NOT
    OPCODE_BIN
    OPCODE_ABS
    OPCODE_SGN

    # conversion
    OPCODE_STR # STR x y ? put new string initialized from y into x

class LM_ObjectHeader:
    LM_DataType type
    unsigned int garbage : 1
    # FIXME: permanent is dangerous, as things references by a permanent object
    # still are garbage collected. What is this used for anyway?
    unsigned int permanent : 1

class LM_Object:
    """
    Each value understood by the scripting language has to be wrapped into an
    object.
    """
    LM_ObjectHeader header
    union value:
        double num
        void *pointer

class LM_Function:
    """
    A function. This is a static object, which holds the binary code, a number
    of constants, and a mapping of variable names to index positions.
    """
    int locals_count
    LandArray *constants
    LandHash *variables
    int code_length
    char *code

class LM_Definition:
    """
    A definition. This is a function as defined at runtime. For global
    functions, it's the same as LM_Function, but with functions defined
    inside functions, there's the possibility of defining multiple copies of
    the same function.
    """
    LM_ObjectHeader header
    LM_Function *function
    LM_Frame *parent

class LM_Frame:
    """
    An execution frame. It consists of the definition currently executed, the
    current locals, and the instruction pointer.
    """
    LM_ObjectHeader header
    LM_Definition *definition
    # Local 0 is the return value register, and usually not used for anything
    # else.
    LandArray *locals
    int ip
    LM_Frame *parent
    int noreturn

class LM_Machine:
    # An array of all known functions. Functions are global and shared by all
    # instances of the virtual machine. Basically, an LM_Function is the static
    # aspect of a function, and shared among all instances. LM_Definition is
    # the dynamic part, owned by each individual instance.
    LandArray *functions

    # A mapping of names of external functions to C function pointers. This
    # also is shared by everyone.
    LandHash *external

    # An array of all currently allocated objects. This is not shared, each copy
    # of an LM_Machine will allocate its own objects.
    LandArray *objects
    # An array of objects used from the outside (so the GC won't collect
    # anything references by them)
    LandArray *used

    LM_Frame *current
    int error

    # Do these belong to the frame? (think multi-threading, where our machine
    # has multiple threads, which run on multiple OS threads..)
    # For user callbacks:
    int param_first # Number of local for first parameter.
    int param_count # Number of consecutive locals being parameters.
    int set # Whether to set or get.
    int target # The target register to assign the retrieved value to.
    LM_ObjectHeader *name # Name of named parameter (for setter/getter)
    LM_ObjectHeader *value # Value of named parameter (for setter/getter)

    int stats_objects_allocated
    int stats_objects_destroyed

static macro OB_STR(com, obh) {
    if (obh->type != LM_TYPE_STR) {
        machine_error(self, com ": String expected");
        return;
    }
}
static macro OB_NUM(com, obh) {
    if (obh->type != LM_TYPE_NUM) {
        machine_error(self, com ": Number expected");
        return;
    }
}
static macro OB_DIC(com, obh) {
    if (obh->type != LM_TYPE_DIC) {
        machine_error(self, com ": Dictionary expected");
        return;
    }
}

LM_Object *def lm_machine_allocate_object(LM_Machine *self):
    """Allocate a new object."""
    LM_Object *x
    land_alloc(x)
    land_array_add(self->objects, x)
    self->stats_objects_allocated++
    return x

def lm_machine_destroy_object(LM_Machine *self, LM_ObjectHeader *h):
    LM_Object *o = (void *)h
    switch h->type:
        case LM_TYPE_NUM:
            break
        case LM_TYPE_STR:
            land_free(o->value.pointer)
            break
        case LM_TYPE_DIC:
            # We do not care about the contained data.
            land_hash_destroy(o->value.pointer)
            break
        case LM_TYPE_DEF:
            break
        case LM_TYPE_FUN:
            LM_Frame *f = (void *)h
            # We do not care about the individual objects references by locals -
            # those are garbage collected on an individual basis.
            land_array_destroy(f->locals)
            break
        case LM_TYPE_NON:
            # Oh yes. Let's destroy the global none value. Very good idea.
            break
        case LM_TYPE_USE:
            # TODO: Likely, we should have a way to call a user supplied
            # destructor for the data of the user object here. For now, we
            # ask the user to keep track of those data themselves.
            break
        default:
            fprintf(stderr, "Fatal: Don't know how to destroy %p (%d).\n", h,
                h->type)
            return
    land_free(h)
    if self: self->stats_objects_destroyed++

LM_Object *def lm_machine_alloc_permanent(LM_Machine *self):
    """Like lm_machine_allocate_object, but the object is not added to the list of
    objects, and the objcet is marked as permanent. This means that even if
    some variable references the object and then goes out of scope, the
    object won't be destroyed.
    """
    LM_Object *x
    land_alloc(x)
    x->header.permanent = 1
    return x

LM_Object *def lm_machine_alloc_str(LM_Machine *self, char const *val):
    LM_Object *o = lm_machine_allocate_object(self)
    o->header.type = LM_TYPE_STR
    o->value.pointer = land_strdup(val)
    return o

LM_Object *def lm_machine_alloc_num(LM_Machine *self, double val):
    LM_Object *o = lm_machine_allocate_object(self)
    o->header.type = LM_TYPE_NUM
    o->value.num = val
    return o

LM_Object *def lm_machine_alloc_dic(LM_Machine *self):
    LM_Object *o
    land_alloc(o)
    o->header.type = LM_TYPE_DIC
    o->value.pointer = land_hash_new()
    land_array_add(self->objects, o)
    return o

LM_Definition *def lm_machine_alloc_def(LM_Machine *self):
    LM_Definition *d
    land_alloc(d)
    d->header.type = LM_TYPE_DEF
    land_array_add(self->objects, d)
    return d

LM_Frame *def lm_machine_alloc_frame(LM_Machine *self):
    LM_Frame *f
    land_alloc(f)
    f->header.type = LM_TYPE_FUN
    land_array_add(self->objects, f)
    return f

static def machine_error(LM_Machine *self, char const *blah, ...):
    char err[1024]
    va_list args
    va_start(args, blah)
    vsprintf(err, blah, args)
    va_end(args)
    fprintf(stderr, "Error: %s\n", err)
    self->error = 1

def lm_machine_use(LM_Machine *self, char const *name,
    void (*cb)(LM_Machine *)):
    land_hash_insert(self->external, name, cb)

static def machine_opcode_use(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    char const *name = ((LM_Object *)oa)->value.pointer
    void (*cb)(LM_Machine *) = land_hash_get(self->external, name)
    self->param_first = b
    self->param_count = c
    if cb:
        cb(self)
    else:
        machine_error(self, "Cannot call %s.", name)

static def machine_opcode_seu(LM_Machine *self, int a, b, c):

    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    OB_STR("SEU", oa)
    char const *name = ((LM_Object *)oa)->value.pointer
    void (*cb)(LM_Machine *) = land_hash_get(self->external, name)

    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    LM_ObjectHeader *oc = lm_machine_get_value(self, c)
    self->name = ob
    self->value = oc
    self->set = 1
    self->target = c # should not be used, the index we assign from

    if cb:
        cb(self)
    else:
        machine_error(self, "Cannot call %s.", name)

static def machine_opcode_geu(LM_Machine *self, int a, b, c):

    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    OB_STR("GEU", ob)
    char const *name = ((LM_Object *)ob)->value.pointer
    void (*cb)(LM_Machine *) = land_hash_get(self->external, name)

    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    LM_ObjectHeader *oc = lm_machine_get_value(self, c)
    self->name = oc
    self->value = oa # should not be used, the value we overwrite
    self->set = 0
    self->target = a

    if cb:
        cb(self)
    else:
        machine_error(self, "Cannot call %s.", name)

static def machine_opcode_nop(LM_Machine *self):
    pass

LM_ObjectHeader *def lm_machine_get_value(LM_Machine *self, int i):
    LM_ObjectHeader *o
    if i >= 0:
        o = self->current->locals->data[i]
    else:
        o = self->current->definition->function->constants->data[128 + i]
    return o

def lm_machine_set_value(LM_Machine *self, int i, LM_ObjectHeader *o):
    if i < 0: return # Cannot modify constants
    # The previous value (if any) will be dealt with by the GC.
    self->current->locals->data[i] = o

LM_ObjectHeader *def lm_machine_get_variable(LM_Machine *self, char const *name):
    LM_Frame *f = self->current
    while f:
        int *i = land_hash_get(f->definition->function->variables, name)
        if i:
            return f->locals->data[*i]
        f = f->definition->parent
    return None

def lm_machine_put_variable(LM_Machine *self, char const *name,
    LM_ObjectHeader *v):

    LM_Frame *f = self->current
    while f:
        int *i = land_hash_get(f->definition->function->variables, name)
        if i:
            f->locals->data[*i] = v
            return
        f = f->definition->parent

static def machine_opcode_def(LM_Machine *self, int a, b, c):
    
    LM_Definition *d = lm_machine_alloc_def(self)

    d->function = self->functions->data[b]
    d->parent = self->current

    self->current->locals->data[a] = d

static def machine_opcode_new(LM_Machine *self, int a, b, c):
    LM_Object *o = lm_machine_alloc_dic(self)
    lm_machine_set_value(self, a, &o->header)

static def machine_opcode_str(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *obh = lm_machine_get_value(self, b)
    LM_Object *ret
    if obh->type == LM_TYPE_NUM:
        LM_Object *ob = (void *)obh
        int integer = ob->value.num
        char str[256]
        if fabs(ob->value.num - integer) < 0.00001:
            snprintf(str, 256, "%d", integer)
        else:
            snprintf(str, 256, "%f", ob->value.num)
        ret = lm_machine_alloc_str(self, str)
    elif obh->type == LM_TYPE_STR:
        LM_Object *ob = (void *)obh
        ret = lm_machine_alloc_str(self, ob->value.pointer)
    lm_machine_set_value(self, a, &ret->header)

static def machine_opcode_dot(LM_Machine *self, int a, b, c):

    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    OB_DIC("DOT", ob)
    LandHash *dict = ((LM_Object *)ob)->value.pointer

    LM_ObjectHeader *oc = lm_machine_get_value(self, c)
    OB_STR("DOT", oc)
    char const *keyname = ((LM_Object *)oc)->value.pointer

    LM_ObjectHeader *o = land_hash_get(dict, keyname)
    if o:
        lm_machine_set_value(self, a, o)
    else:
        machine_error(self, "DOT: Attribute not found")

static def machine_opcode_set(LM_Machine *self, int a, b, c):

    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    OB_DIC("SET", oa)
    LandHash *dict = ((LM_Object *)oa)->value.pointer

    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    OB_STR("SET", ob)
    char const *keyname = ((LM_Object *)ob)->value.pointer

    LM_ObjectHeader *oc = lm_machine_get_value(self, c)

    # We ignore the existing value under that key if any, it will get garbage
    # collected eventually.
    land_hash_replace(dict, keyname, oc)

int def lm_machine_get_integer(LM_Machine *self, int i):
    if i == 0: return 0
    LM_ObjectHeader *o
    if i > 0:
        o = self->current->locals->data[i]
    else:
        o = self->current->definition->function->constants->data[128 + i]
    if o->type == LM_TYPE_NUM:
        return ((LM_Object *)o)->value.num
    if o->type == LM_TYPE_STR:
        return ustrtod(((LM_Object *)o)->value.pointer, None)
    return 0

static def machine_call(LM_Machine *self, LM_Definition *definition, int b, c):
    # TODO: We can re-use an old frame. Locals need not be initialized as the
    # compiler will never create code to access a local before it was assigned
    # to.
    LM_Frame *frame = lm_machine_alloc_frame(self)

    int count = c

    frame->definition = definition
    frame->locals = land_array_new()
    land_array_add(frame->locals, None) # TODO: what about the 0 position?
    # Function call arguments.
    for int i = 0; i < count; i++:
        LM_ObjectHeader *ob = lm_machine_get_value(self, b + i)
        land_array_add(frame->locals, ob)
    # Initialize locals to None.
    for int i = 1 + count; i < definition->function->locals_count; i++:
        land_array_add(frame->locals, None)

    frame->parent = self->current
    frame->ip = 0
    self->current = frame

static def machine_opcode_fun(LM_Machine *self, int a, b, c):
    if a < 0:
        machine_error(self, "Cannot call a constant.")
        return
    LM_ObjectHeader *defob = self->current->locals->data[a]
    if defob->type != LM_TYPE_DEF:
        machine_error(self, "Can only call a function.")
        return

    LM_Definition *definition = (LM_Definition *)defob

    machine_call(self, definition, b, c)

static def machine_opcode_arg(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    lm_machine_set_value(self, a, ob)
    # The previous value eventually will go to the GC.

static def machine_opcode_ass(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    lm_machine_set_value(self, a, ob)

static def machine_opcode_ret(LM_Machine *self, int a, b, c):
    # TODO: If no definitions were made during executing the frame, we can
    # drop it (and possibly re-use on next call of the function). If any
    # definitions were made, we just leave it to GC to eventually drop it.
    LM_ObjectHeader *ob = None

    ob = lm_machine_get_value(self, a)

    self->current = self->current->parent

    # We do write the return value to the 0 register of the caller.

    lm_machine_set_value(self, 0, ob)

static def machine_binary_op(LM_Machine *self, int a, b, c,
    double (*cb)(double x, double y)):
    LM_Object *oa = lm_machine_allocate_object(self)
    oa->header.type = LM_TYPE_NUM
    LM_ObjectHeader *obh = lm_machine_get_value(self, b)
    LM_ObjectHeader *och = lm_machine_get_value(self, c)
    # FIXME: Check type
    LM_Object *ob = (LM_Object *)obh
    LM_Object *oc = (LM_Object *)och
    oa->value.num = cb(ob->value.num, oc->value.num)
    lm_machine_set_value(self, a, &oa->header)

static double def add_cb(double x, y):
    return x + y
static double def sub_cb(double x, y):
    return x - y
static double def mul_cb(double x, y):
    return x * y
static double def div_cb(double x, y):
    return x / y
static double def low_cb(double x, y):
    return x < y
static double def big_cb(double x, y):
    return x > y
static double def sam_cb(double x, y):
    return x == y

static macro binop(name) static void machine_opcode_##name(
    LM_Machine *self, int a, int b, int c) {
    machine_binary_op(self, a, b, c, name##_cb);}

binop(add)
binop(sub)
binop(mul)
binop(div)
binop(low)
binop(big)
binop(sam)

static def machine_opcode_get(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    OB_STR("GET", ob)
    char const *name = ((LM_Object *)ob)->value.pointer

    LM_ObjectHeader *v = lm_machine_get_variable(self, name)
    self->current->locals->data[a] = v
    # The previous value of the variable eventually will go to the GC.

static def machine_opcode_put(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    LM_ObjectHeader *ob = lm_machine_get_value(self, b)

    # FIXME
    if oa->type != LM_TYPE_STR:
        machine_error(self, "FIXME: Only string lookup supported right now.")
        return

    char const *name = ((LM_Object *)oa)->value.pointer

    lm_machine_put_variable(self, name, ob)

static def machine_opcode_hop(LM_Machine *self, int a, b, c):
    self->current->ip += b

static def machine_opcode_bra(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    OB_NUM("BRA", oa)
    if ((LM_Object *)oa)->value.num:
        self->current->ip += b

static def machine_opcode_and(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    OB_NUM("AND", oa)
    if not ((LM_Object *)oa)->value.num:
        self->current->ip += b

def lm_machine_output(LM_Machine *self, LM_ObjectHeader *oh):
    if oh->type == LM_TYPE_NUM:
        LM_Object *o = (void *)oh
        int integer = o->value.num
        if fabs(o->value.num - integer) < 0.00001:
            printf("%d", integer)
        else:
            printf("%f", o->value.num)
    elif oh->type == LM_TYPE_STR:
        LM_Object *o = (void *)oh
        printf("%s", (char *)o->value.pointer)
    elif oh->type == LM_TYPE_DIC:
        LM_Object *o = (void *)oh
        LandHash *dict = o->value.pointer
        LandArray *keys = land_hash_keys(dict)
        land_array_sort_alphabetical(keys)
        printf("{")
        int n = land_array_count(keys)
        for int i = 0; i < n; i++:
            char const *name = land_array_get_nth(keys, i)
            printf("%s = ", name)
            LM_ObjectHeader *o2 = land_hash_get(dict, name)
            if o2: lm_machine_output(self, o2)
            if i < n - 1:
                printf(", ")
        printf("}")
        land_array_destroy(keys)

static def machine_opcode_out(LM_Machine *self, int a, b, c):
    for int i = 0; i < b; i++:
        LM_ObjectHeader *oa = lm_machine_get_value(self, a + i)

        if i:
            printf(" ")

        lm_machine_output(self, oa)

static def machine_opcode_flu(LM_Machine *self, int a, b, c):
    machine_opcode_out(self, a, b, c)
    printf("\n")

static def machine_opcode_end(LM_Machine *self, int a, b, c):
    self->current->ip = 0

static def machine_opcode_pau(LM_Machine *self, int a, b, c):
    pass

static def debug_object(LM_Machine *self, LM_ObjectHeader *obh):
    if not obh:
        printf("<missing>")
    else:
        LM_Object *ob = (void *)obh
        if obh->type == LM_TYPE_NON:
            printf("none")
        elif obh->type == LM_TYPE_STR:
            printf("%s", (char *)ob->value.pointer)
        elif obh->type == LM_TYPE_NUM:
            printf("%f", ob->value.num)
        elif obh->type == LM_TYPE_DEF:
            printf("def[%p]", ob)
        elif obh->type == LM_TYPE_FUN:
            printf("fun[%p]", ob)
        else:
            printf("0x%p(%d)", obh, obh->type)

static def print_variables(LM_Machine *self, LM_Frame *frame):
    LandArray *keys = land_hash_keys(frame->definition->function->variables)
    char const *names[frame->locals->count]
    for int i = 0; i < frame->locals->count; i++:
        names[i] = None
    for int i = 0; i < keys->count; i++:
        char const *k = keys->data[i]
        int *j = land_hash_get(frame->definition->function->variables, k)
        names[*j] = k

    for int i = 0; i < frame->locals->count; i++:
        if names[i]:
            printf(" %d(%s): ", i, names[i])
        else:
            printf(" %d: ", i)
        LM_ObjectHeader *ob = frame->locals->data[i]
        debug_object(self, ob)

    land_array_destroy(keys)

static macro D(x) case OPCODE_##x: fprintf(out, "%s%s ", indent, #x); break;
static def debug_code(char *buffer, char const *indent, FILE *out):
    char opcode = buffer[0]
    switch opcode:
        D(NOP)
        D(FUN)
        D(USE)
        D(SEU)
        D(GEU)
        D(RET)
        D(END)
        D(PAU)
        D(PUT)
        D(GET)
        D(OUT)
        D(FLU)
        D(ARG)
        D(DEF)
        D(NEW)

        D(HOP)
        D(BRA)
        D(AND)

        D(ASS)
        D(DOT)
        D(SET)

        D(ADD)
        D(SUB)
        D(MUL)
        D(DIV)
        D(BIG)
        D(LOW)
        D(SAM)
        D(STR)
        default: fprintf(out, " ??? ")
    unsigned char *b = (unsigned char *)buffer
    fprintf(out, "%d %d %d\n", b[1], b[2], b[3])

static def object_reachable(LM_Machine *self, LM_ObjectHeader *o):
    if not o: return
    # Prevent infinite recursion
    if not o->garbage: return
    o->garbage = 0

    if o->type == LM_TYPE_DIC:
        # If the dictionary is reachable, so are all of the data in it.
        LandHash *hash = ((LM_Object *)o)->value.pointer
        for int i = 0; i < hash->size; i++:
            LandHashEntry *entry = hash->entries[i]
            if entry:
                int n = entry->n
                for int j = 0; j < n; j++:
                    object_reachable(self, entry[j].data)
    elif o->type == LM_TYPE_DEF:
        # If the definition is reachable, so is the frame it was defined in.
        LM_Definition *d = (void *)o
        object_reachable(self, &d->parent->header)
    elif o->type == LM_TYPE_FUN:
        # If a frame is reachable, so are all its variables, its calling parent,
        # and its definition.
        # TODO: Explain why the definition is reachable - our caller must have
        # a reference, so that keeps it reachable? but not the fact we are still
        # running this frame (?), so why?

        LM_Frame *f = (void *)o
        for int i = 0; i < f->locals->count; i++:
            object_reachable(self, f->locals->data[i])
        object_reachable(self, &f->parent->header)
        object_reachable(self, &f->definition->header)

def lm_garbage_collector(LM_Machine *self):
    # First, mark everything as garbage.
    for int i = 0; i < self->objects->count; i++:
        LM_ObjectHeader *h = self->objects->data[i]
        if h->permanent: h->garbage = 0
        else: h->garbage = 1

    # Then, recursively unmark reachable objects.
    if self->current: object_reachable(self, &self->current->header)

    for int i = 0; i < self->used->count; i++:
        object_reachable(self, land_array_get_nth(self->used, i))

    # Finally, go through everything again and destroy objects who didn't get
    # unmarked.
    for int i = 0; i < self->objects->count; i++:
        LM_ObjectHeader *h = self->objects->data[i]
        if h->garbage:
            lm_machine_destroy_object(self, h)
            void *last = land_array_pop(self->objects)
            if last != h:
                land_array_replace_nth(self->objects, i, last)
                i--

    self->stats_objects_allocated = 0
    self->stats_objects_destroyed = 0

def lm_machine_consider_used(LM_Machine *self, LM_ObjectHeader *oh):
    land_array_add(self->used, oh)

def lm_machine_consider_unused(LM_Machine *self, LM_ObjectHeader *oh):
    int i = land_array_find(self->used, oh)
    if i >= 0:
        void *data = land_array_pop(self->used)
        if i < self->used->count:
            land_array_replace_nth(self->used, i, data)

def lm_machine_status(LM_Machine *self):

    LM_Frame *f = self->current
    while f->parent:
        printf("locals:")
        print_variables(self, f)
        printf("\n")
        f = f->parent
    printf("globals:")
    print_variables(self, f)
    printf("\n")

    printf("constants:")
    LandArray *constants = self->current->definition->function->constants
    for int i = 0; i < constants->count; i++:
        printf(" %d: ", 128 + i)
        debug_object(self, constants->data[i])
        
    printf("\n")

    lm_garbage_collector(self)

    printf("objects:")
    for int i = 0; i < self->objects->count; i++:
        printf(" ")
        LM_ObjectHeader *ob = land_array_get_nth(self->objects, i)
        debug_object(self, ob)
        printf("[%d]", ob->garbage)
    printf("\n")

def lm_machine_continue(LM_Machine *self):
    LM_Frame *frame = self->current
    char *code = frame->definition->function->code
    while not self->error:

        #lm_machine_status(self)
        #debug_code(code + frame->ip, "    ", stdout)

        char opcode = code[frame->ip++]
        char a = code[frame->ip++]
        char b = code[frame->ip++]
        char c = code[frame->ip++]
        switch opcode:
            case OPCODE_NOP: machine_opcode_nop(self); break
            case OPCODE_ADD: machine_opcode_add(self, a, b, c); break
            case OPCODE_SUB: machine_opcode_sub(self, a, b, c); break
            case OPCODE_MUL: machine_opcode_mul(self, a, b, c); break
            case OPCODE_DIV: machine_opcode_div(self, a, b, c); break
            case OPCODE_BIG: machine_opcode_big(self, a, b, c); break
            case OPCODE_LOW: machine_opcode_low(self, a, b, c); break
            case OPCODE_SAM: machine_opcode_sam(self, a, b, c); break
            case OPCODE_BRA: machine_opcode_bra(self, a, b, c); break
            case OPCODE_AND: machine_opcode_and(self, a, b, c); break
            case OPCODE_HOP: machine_opcode_hop(self, a, b, c); break
            case OPCODE_RET:
                machine_opcode_ret(self, a, b, c)
                if frame->noreturn:
                    lm_garbage_collector(self)
                    return
                frame = self->current
                code = frame->definition->function->code
                break
            case OPCODE_END:
                machine_opcode_end(self, a, b, c)
                lm_garbage_collector(self)
                return
            case OPCODE_PAU:
                machine_opcode_pau(self, a, b, c)
                lm_garbage_collector(self)
                return
            case OPCODE_OUT: machine_opcode_out(self, a, b, c); break
            case OPCODE_FLU: machine_opcode_flu(self, a, b, c); break
            case OPCODE_DEF: machine_opcode_def(self, a, b, c); break
            case OPCODE_ARG: machine_opcode_arg(self, a, b, c); break
            case OPCODE_ASS: machine_opcode_ass(self, a, b, c); break
            case OPCODE_FUN:
                machine_opcode_fun(self, a, b, c)
                frame = self->current
                code = frame->definition->function->code
                break
            case OPCODE_USE: machine_opcode_use(self, a, b, c); break
            case OPCODE_SEU: machine_opcode_seu(self, a, b, c); break
            case OPCODE_GEU: machine_opcode_geu(self, a, b, c); break
            case OPCODE_GET: machine_opcode_get(self, a, b, c); break
            case OPCODE_PUT: machine_opcode_put(self, a, b, c); break
            case OPCODE_NEW: machine_opcode_new(self, a, b, c); break
            case OPCODE_DOT: machine_opcode_dot(self, a, b, c); break
            case OPCODE_SET: machine_opcode_set(self, a, b, c); break
            case OPCODE_STR: machine_opcode_str(self, a, b, c); break

int def lm_machine_call_top(LM_Machine *self, char const *name):
    """
    Call a top-level funcion given by its name. Returns True on success, False
    if the named function cannot be found.
    """
    return lm_machine_call_top_params(self, name, 0)


def lm_machine_call_va(LM_Machine *self, LM_Definition *d, int n, va_list args):
    # Create the new frame to execute in.
    LM_Frame *frame = lm_machine_alloc_frame(self)
    frame->definition = d
    frame->locals = land_array_new()
    frame->noreturn = 1
    land_array_add(frame->locals, None) # TODO: what about the 0 position?

    # Function call arguments.
    for int i = 0; i < n; i++:
        LM_ObjectHeader *ob = va_arg(args, LM_ObjectHeader *)
        land_array_add(frame->locals, ob)

    # Initialize locals to None.
    for int i = 1 + n; i < d->function->locals_count; i++:
        land_array_add(frame->locals, None)

    frame->parent = self->current
    frame->ip = 0
    self->current = frame

def lm_machine_call_params(LM_Machine *self, LM_Definition *d, int n, ...):
    va_list args
    va_start(args, n)
    lm_machine_call_va(self, d, n, args)
    va_end(args)

int def lm_machine_call_top_params(LM_Machine *self, char const *name,
    int n, ...):
    # First go to topmost frame.
    # TODO: Is this really what should be done? If we are currently inside
    # some function, then maybe the call should be made from within..
    while self->current->parent:
        self->current = self->current->parent

    # Find the global variable holding the function.
    int *vi = land_hash_get(self->current->definition->function->variables, name)
    # TODO: Note: We still may have jumped to the topmost frame above.

    if not vi: return False
    LM_ObjectHeader *h = land_array_get_nth(self->current->locals, *vi)
    if h->type != LM_TYPE_DEF:
        return False
    LM_Definition *d = (void *)h

    va_list args
    va_start(args, n)
    lm_machine_call_va(self, d, n, args)
    va_end(args)

    return True

int def lm_machine_add_global(LM_Machine *self, char const *name):
    """
    Adds a new global variable. This must be called before executing the VM.
    """
    LM_Function *f = self->functions->data[0]
    int *val
    land_alloc(val)
    *val = f->locals_count
    f->locals_count++
    land_hash_insert(f->variables, name, val)
    return *val

def lm_machine_reset(LM_Machine *self):

    # Define the global function.
    LM_Definition *definition = lm_machine_alloc_def(self)

    definition->function = self->functions->data[0]
    definition->parent = None

    # And call it.
    machine_call(self, definition, 0, 0)

def lm_machine_debug_code(char *buffer, int n, char const *indent, FILE *out):
    for int j = 0; j < n; j++:
        debug_code(buffer + j, indent, out)
        j += 3

def lm_machine_debug(LM_Machine *self, FILE *out):
    for int i = 0; i < self->functions->count; i++:
        fprintf(out, "Function (%d/%d):\n", i, self->functions->count)
        LM_Function *f = land_array_get_nth(self->functions, i)
        fprintf(out, " locals: %d\n", f->locals_count)

        fprintf(out, " constants: %d\n", f->constants->count)
        for int j = 0; j < f->constants->count; j++:
            LM_ObjectHeader *obh = land_array_get_nth(f->constants, j)
            LM_Object *ob = (void *)obh
            fprintf(out, "  %d: ", 128 + j)
            if obh->type == LM_TYPE_NUM:
                fprintf(out, "number: %f\n", ob->value.num)
            elif obh->type == LM_TYPE_STR:
                fprintf(out, "string: %s\n", (char *)ob->value.pointer)
            elif obh->type == LM_TYPE_NON:
                fprintf(out, "none\n")
            else:
                fprintf(out, "?\n")

        LandArray *keys = land_hash_keys(f->variables)
        fprintf(out, " variables: %d\n", keys->count)
        for int j = 0; j < keys->count; j++:
            int *val = land_hash_get(f->variables, keys->data[j])
            fprintf(out, "  %s: %d\n", (char *)keys->data[j], *val)
        land_array_destroy(keys)

        fprintf(out, " code:\n")
        lm_machine_debug_code(f->code, f->code_length, "  ", out)

static char *def read_name(PACKFILE *pf):
    int s = 32
    char *blah = land_malloc(s)
    int i
    for i = 0; ; i++:
        int c = pack_getc(pf)
        if c <= 0: break
        if i >= s:
            s *= 2
            blah = land_realloc(blah, s)
        blah[i] = c
    blah[i] = 0
    blah = land_realloc(blah, i + 1)
    return blah  

LM_Machine *def lm_machine_new_machine():
    LM_Machine *self
    land_alloc(self)
    self->objects = land_array_new()
    self->used = land_array_new()
    return self

def lm_machine_destroy_instance(LM_Machine *self):
    """
    Completely destroys the virtual machine instance. Data which are possibly
    shared among other virtual machine instances are not destroyed, use
    lm_machine_destroy for that.
    """
    # Cut our reference to anything.
    self->current = None
    # Which should prompt the GC to collect everything.
    lm_garbage_collector(self)

    land_array_destroy(self->objects)
    land_array_destroy(self->used)

    land_free(self)

def lm_machine_destroy(LM_Machine *self):
    """
    Destroys the currently running machine with lm_machine_destroy_instance,
    and also destroys all static data like function definitions.
    """

    land_hash_destroy(self->external)

    # Destroy all the compiled code and static variable name mappings and
    # constants.
    for int i = 0; i < self->functions->count; i++:
        LM_Function *f = land_array_get_nth(self->functions, i)
        for int j = 0; j < f->constants->count; j++:
            LM_ObjectHeader *h = land_array_get_nth(f->constants, j)
            lm_machine_destroy_object(self, h)
        land_array_destroy(f->constants)

        LandArray *va = land_hash_data(f->variables)
        for int j = 0; j < va->count; j++: land_free(land_array_get_nth(va, j))
        land_array_destroy(va)
        land_hash_destroy(f->variables)

        land_free(f->code)

        land_free(f)
    land_array_destroy(self->functions)

    lm_machine_destroy_instance(self)

LM_Machine *def lm_machine_new_from_packfile(PACKFILE *pf):
    """
    Create a new machine by reading compiled code from a packfile.
    """
    LM_Machine *self = lm_machine_new_machine()

    self->external = land_hash_new()
    self->functions = land_array_new()

    while 1:
        int n = pack_igetl(pf)
        if n < 0: break

        LM_Function *f
        land_alloc(f)
        f->locals_count = n

        # Read named variables.
        f->variables = land_hash_new()
        n = pack_igetl(pf)
        for int i = 0; i < n; i++:
            char *name = read_name(pf)
            int *val
            land_alloc(val)
            *val = pack_igetl(pf)
            land_hash_insert(f->variables, name, val)
            land_free(name)

        # Read constants.
        f->constants = land_array_new()
        n = pack_igetl(pf)
        for int i = 0; i < n; i++:
            LM_Object *ob = lm_machine_alloc_permanent(self)
            int t = ob->header.type = pack_igetl(pf)
            if t == LM_TYPE_NUM: ob->value.num = pack_igetl(pf)
            if t == LM_TYPE_STR: ob->value.pointer = read_name(pf)
            land_array_add(f->constants, ob)

        f->code_length = n = pack_igetl(pf)
        f->code = land_malloc(n)
        for int i = 0; i < n; i++:
            f->code[i] = pack_getc(pf)

        land_array_add(self->functions, f)

    return self

LM_Machine *def lm_machine_new_from_file(char const *filename):
    """
    Create a new machine, with compiled code read out of the given file.
    """
    PACKFILE *pf = pack_fopen(filename, "rb")
    if not pf: return None

    LM_Machine *m = lm_machine_new_from_packfile(pf)
    pack_fclose(pf)
    return m

LM_Machine *def lm_machine_new_from_buffer(LandBuffer *buffer):
    """
    Create a new machine from code in a buffer.
    """
    PACKFILE *pf = land_buffer_read_packfile(buffer)
    LM_Machine *m = lm_machine_new_from_packfile(pf)
    pack_fclose(pf)
    return m

LM_Machine *def lm_machine_new_instance(LM_Machine *machine):
    """
    Create a new virtual machine, which shares static data with the given
    machine. Usually, you can just create a new machine from code, all this
    will do is safe a little time and memory in case you are making very many
    virtual machines sharing the same code.
    """
    LM_Machine *self = lm_machine_new_machine()
    self->external = machine->external
    self->functions = machine->functions
    return self