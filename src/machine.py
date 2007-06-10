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
    TYPE_NON
    TYPE_BOO
    TYPE_INT
    TYPE_NUM # A number.
    TYPE_DAT
    TYPE_STR
    TYPE_DEF # A definition.
    TYPE_FUN # A frame.
    TYPE_ARR
    TYPE_LIS
    TYPE_DIC # A dictionary.
    TYPE_QUE
    TYPE_USE # A user provided object.

# x y z is registers (1..127), constants (-128..-1), or None (0)
# A B C is inline values
#
enum LM_Opcode:
    # miscellaneous
    OPCODE_NOP # NOP ? ? ? does nothing
    OPCODE_USE # USE x y C Calls a user callback named x (y and C like FUN)
    OPCODE_END # END ? ? ? stops the virtual machine

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
    OPCODE_HOP # HOP x <B> do a relative jump
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

class LM_ObjectHeader:
    LM_DataType type
    int garbage : 1

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

class LM_Machine:
    # An array of all known functions.
    LandArray *functions
    # A mapping of names of external function to C function pointers.
    LandHash *external
    # An array of all currently allocated objects
    LandArray *objects

    LM_Frame *current
    int error

static macro OB_STR(com, obh) {
    if (obh->type != TYPE_STR) {
        machine_error(self, com ": String expected");
        return;
    }
}
static macro OB_NUM(com, obh) {
    if (obh->type != TYPE_NUM) {
        machine_error(self, com ": Number expected");
        return;
    }
}

LM_Object *def lm_machine_alloc(LM_Machine *self):
    """Allocate a new object."""
    LM_Object *x
    land_alloc(x)
    land_array_add(self->objects, x)
    return x

LM_Object *def lm_machine_alloc_dic(LM_Machine *self):
    LM_Object *o
    land_alloc(o)
    o->header.type = TYPE_DIC
    o->value.pointer = land_hash_new()
    land_array_add(self->objects, o)
    return o

LM_Definition *def lm_machine_alloc_def(LM_Machine *self):
    LM_Definition *d
    land_alloc(d)
    d->header.type = TYPE_DEF
    land_array_add(self->objects, d)
    return d

LM_Frame *def lm_machine_alloc_frame(LM_Machine *self):
    LM_Frame *f
    land_alloc(f)
    f->header.type = TYPE_FUN
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
    void (*cb)(LM_Machine *, int a, int b)):
    land_hash_insert(self->external, name, cb)

static def machine_opcode_use(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *ob = lm_machine_get_value(self, a)
    OB_STR("USE", ob)
    char const *name = ((LM_Object *)ob)->value.pointer
    void (*cb)(LM_Machine *, int, int) = land_hash_get(self->external, name)
    if cb:
        cb(self, b, c)
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

static def machine_opcode_def(LM_Machine *self, int a, b, c):
    
    LM_Definition *d = lm_machine_alloc_def(self)

    d->function = self->functions->data[b]
    d->parent = self->current
  
    self->current->locals->data[a] = d

static def machine_opcode_new(LM_Machine *self, int a, b, c):
    LM_Object *o = lm_machine_alloc_dic(self)
    lm_machine_set_value(self, a, &o->header)

static def machine_opcode_dot(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    if ob->type != TYPE_DIC:
        machine_error(self, "DOT: Dictionary expected")
        return
    LandHash *dict = ((LM_Object *)ob)->value.pointer

    LM_ObjectHeader *oc = lm_machine_get_value(self, c)
    if oc->type != TYPE_STR:
        machine_error(self, "DOT: String expected")
        return
    char const *keyname = ((LM_Object *)oc)->value.pointer

    LM_ObjectHeader *o = land_hash_get(dict, keyname)
    if o:
        lm_machine_set_value(self, a, o)
    else:
        machine_error(self, "DOT: Attribute not found")

static def machine_opcode_set(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *oa = lm_machine_get_value(self, a)
    if oa->type != TYPE_DIC:
        machine_error(self, "SET: Dictionary expected")
        return
    LandHash *dict = ((LM_Object *)oa)->value.pointer

    LM_ObjectHeader *ob = lm_machine_get_value(self, b)
    if ob->type != TYPE_STR:
        machine_error(self, "SET: String expected")
        return
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
    if o->type == TYPE_NUM:
        return ((LM_Object *)o)->value.num
    if o->type == TYPE_STR:
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
    if a == 0: return # Calling none does.. nothing
    if a < 0:
        machine_error(self, "Cannot call a constant.")
        return
    LM_ObjectHeader *defob = self->current->locals->data[a]
    if defob->type != TYPE_DEF:
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
    LM_Object *oa = lm_machine_alloc(self)
    oa->header.type = TYPE_NUM
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

    LM_Frame *f = self->current
    while f:
        int *i = land_hash_get(f->definition->function->variables, name)
        if i:
            self->current->locals->data[a] = f->locals->data[*i]
            # The previous value of the variable eventually will go to the GC.
            break
        f = f->definition->parent

static def machine_opcode_put(LM_Machine *self, int a, b, c):
    LM_ObjectHeader *oa = lm_machine_get_value(self, a)

    # FIXME
    if oa->type != TYPE_STR:
        machine_error(self, "FIXME: Only string lookup supported right now.")
        return

    char const *name = ((LM_Object *)oa)->value.pointer

    LM_Frame *f = self->current
    while f:
        int *i = land_hash_get(f->definition->function->variables, name)
        if i:
            LM_ObjectHeader *ob = lm_machine_get_value(self, b)
            f->locals->data[*i] = ob
            # The previous value of the variable eventually will go to the GC.
            break
        f = f->definition->parent

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
    if oh->type == TYPE_NUM:
        LM_Object *o = (void *)oh
        int integer = o->value.num
        if fabs(o->value.num - integer) < 0.00001:
            printf("%d", integer)
        else:
            printf("%f", o->value.num)
    elif oh->type == TYPE_STR:
        LM_Object *o = (void *)oh
        printf("%s", (char *)o->value.pointer)
    elif oh->type == TYPE_DIC:
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

static def debug_object(LM_Machine *self, LM_ObjectHeader *obh):
    if not obh:
        printf("<missing>")
    else:
        LM_Object *ob = (void *)obh
        if obh->type == TYPE_NON:
            printf("none")
        elif obh->type == TYPE_STR:
            printf("%s", (char *)ob->value.pointer)
        elif obh->type == TYPE_NUM:
            printf("%f", ob->value.num)
        elif obh->type == TYPE_DEF:
            printf("def[%p]", ob)
        elif obh->type == TYPE_FUN:
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
        D(RET)
        D(END)
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
        default: fprintf(out, " ??? ")
    unsigned char *b = (unsigned char *)buffer
    fprintf(out, "%d %d %d\n", b[1], b[2], b[3])

static def object_reachable(LM_Machine *self, LM_ObjectHeader *o):
    if not o: return
    # Prevent infinite recursion
    if not o->garbage: return
    o->garbage = 0

    if o->type == TYPE_DIC:
        # If the dictionary is reachable, so are all of the data in it.
        LandHash *hash = ((LM_Object *)o)->value.pointer
        for int i = 0; i < hash->size; i++:
            LandHashEntry *entry = hash->entries[i]
            if entry:
                int n = entry->n
                for int j = 0; j < n; j++:
                    object_reachable(self, entry[j].data)
    elif o->type == TYPE_DEF:
        # If the definition is reachable, so is the frame it was defined in.
        LM_Definition *d = (void *)o
        object_reachable(self, &d->parent->header)
    elif o->type == TYPE_FUN:
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
        h->garbage = 1

    # Then, recursively unmark reachable objects.
    object_reachable(self, &self->current->header)

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
                if not frame->parent: return
                machine_opcode_ret(self, a, b, c)
                frame = self->current
                code = frame->definition->function->code
                break
            case OPCODE_END: return
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
            case OPCODE_GET: machine_opcode_get(self, a, b, c); break
            case OPCODE_PUT: machine_opcode_put(self, a, b, c); break
            case OPCODE_NEW: machine_opcode_new(self, a, b, c); break
            case OPCODE_DOT: machine_opcode_dot(self, a, b, c); break
            case OPCODE_SET: machine_opcode_set(self, a, b, c); break

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
            if obh->type == TYPE_NUM:
                fprintf(out, "  %d: number: %f\n", 128 + j, ob->value.num)
            if obh->type == TYPE_STR:
                fprintf(out, "  %d: string: %s\n", 128 + j, (char *)ob->value.pointer)

        LandArray *keys = land_hash_keys(f->variables)
        fprintf(out, " variables: %d\n", keys->count)
        for int j = 0; j < keys->count; j++:
            int *val = land_hash_get(f->variables, keys->data[j])
            fprintf(out, "  %s: %d\n", (char *)keys->data[j], *val)
        land_array_destroy(keys)

        fprintf(out, " code:\n")
        lm_machine_debug_code(f->code, f->code_length, "  ", out)

static char const *def read_name(PACKFILE *pf):
    static char blah[1024]
    int i
    for i = 0; i < (int)sizeof(blah) - 1; i++:
        int c = pack_getc(pf)
        if c <= 0: break
        blah[i] = c
    blah[i] = 0
    return blah  

LM_Machine *def lm_machine_new_machine():
    LM_Machine *self
    land_alloc(self)
    self->external = land_hash_new()
    self->objects = land_array_new()
    return self

LM_Machine *def lm_machine_new_from_packfile(PACKFILE *pf):
    """
    Create a new machine by reading compiled code from a packfile.
    """
    LM_Machine *self = lm_machine_new_machine()

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
            char const *name = read_name(pf)
            int *val
            land_alloc(val)
            *val = pack_igetl(pf)
            land_hash_insert(f->variables, name, val)

        # Read constants.
        f->constants = land_array_new()
        n = pack_igetl(pf)
        for int i = 0; i < n; i++:
            #LM_Object *ob = lm_machine_alloc(self)
            # We do not want constants to appear in the garbage collector
            LM_Object *ob
            land_alloc(ob)
            int t = ob->header.type = pack_igetl(pf)
            if t == TYPE_NUM: ob->value.num = pack_igetl(pf)
            if t == TYPE_STR: ob->value.pointer = land_strdup(read_name(pf))
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
