import syntax, machine

class LM_Compiler:
    SyntaxAnalyzer *sa

    LandHash *using
    LandArray *functions
    LM_CompilerFunction *global_function

    LM_CompilerFunction *current

    LandArray *resolve

class LM_CompilerFunction:
    int is_global

    int locals_count # How many locals are currently in use.
    int temporaries_count # How many of the above locals are temporary.

    LM_CompilerFunction *parent # A function inside a function has a parent.

    LandArray *parameters # An array with the parameter names.

    int locals_needed # How many locals need to be reserved at runtime, when
    # calling this function.

    LandHash *locals # A mapping of parameter names to indices.
    LandArray *constants
    LandBuffer *code

static class JumpResolve:
    int codepos
    int tag

macro JUMP_YES 1
macro JUMP_NO 2
macro JUMP_OUT 3
macro JUMP_WHILE 4
macro JUMP_BARRIER 5
macro JUMP_BREAK 6

static void compile_or(LM_Compiler *c, Node *n);
static void compile_and(LM_Compiler *c, Node *n);

int def new_constant(LM_Compiler *c):
    LM_Object *val
    land_alloc(val)

    land_array_add(c->current->constants, val)
    return (c->current->constants->count - 1)

LM_CompilerFunction *def function_new(LM_CompilerFunction *parent):
    LM_CompilerFunction *self
    land_alloc(self)

    self->parameters = land_array_new()
    self->constants = land_array_new()
    self->code = land_buffer_new()
    self->locals = land_hash_new()
    self->parent = parent

    # TODO: Hm, main reason is so a return of 0 always can mean failure. Maybe
    # we can use this for 0 always meaning None when used as operand.
    # always reserve slot 0
    self->locals_needed = 1
    self->locals_count = 1

    return self

LM_Compiler *def lm_compiler_new_from_syntax_analyzer(SyntaxAnalyzer *sa):
    LM_Compiler *self
    land_alloc(self)
    self->sa = sa

    self->functions = land_array_new()
    self->using = land_hash_new()

    return self

LM_Compiler *def lm_compiler_new_from_file(char const *filename):

    Tokenizer *t = tokenizer_new_from_file(filename)
    tokenizer_tokenize(t)

    SyntaxAnalyzer *sa = syntax_analyzer_new_from_tokenizer(t)
    syntax_analyzer_parse(sa)
    syntax_analyzer_analyze(sa)

    LM_Compiler *c = lm_compiler_new_from_syntax_analyzer(sa)

    return c

int def add_string_constant(LM_Compiler *c, char const *string):
    int i = new_constant(c)
    LM_Object *val = c->current->constants->data[i]
    val->header.type = LM_TYPE_STR
    val->value.pointer = land_strdup(string)
    return i | 128

int def add_constant(LM_Compiler *c, Token *token, LM_DataType type):
    int i = new_constant(c)
    LM_Object *val = c->current->constants->data[i]

    val->header.type = type
    if type == LM_TYPE_NUM:
        val->value.num = ustrtod(token->string, NULL)
    else:
        val->value.pointer = land_strdup(token->string)

    return i | 128

static def add_code(LM_Compiler *c, int opcode, op1, op2, op3):
    char code[4]
    code[0] = opcode
    code[1] = op1
    code[2] = op2
    code[3] = op3
    land_buffer_add(c->current->code, code, 4)

static int def create_new_local(LM_Compiler *c):
    """
    Allocate a new local in the current function.
    """
    c->current->locals_count++
    if c->current->locals_count > c->current->locals_needed:
        c->current->locals_needed = c->current->locals_count
    return c->current->locals_count - 1

static int def create_new_temporary(LM_Compiler *c):
    """
    Allocate a temporary local in the current function. It will not be valid
    after the end of the current statement.
    """
    c->current->temporaries_count++
    return create_new_local(c)

static int def get_global_variable(LM_Compiler *c, char const *string):
    # FIXME: clarify that slot 0 is never used
    int *num = land_hash_get(c->global_function->locals, string)
    if not num: return 0
    return *num

static int def get_local_variable(LM_Compiler *c, char const *string):
    # FIXME: clarify that slot 0 is never used
    int *num = land_hash_get(c->current->locals, string)
    if not num: return 0
    return *num

static int def find_or_create_local(LM_Compiler *c, char const *string):
    int *num = land_hash_get(c->current->locals, string)
    if num: # A local variable.
        return *num

    # add a new named local
    land_alloc(num)
    *num = create_new_local(c)
    land_hash_insert(c->current->locals, string, num)

    return  *num

static int def find_or_create_global(LM_Compiler *c, char const *string):
    return find_or_create_local(c, string)

static int def compile_named_variable_lookup(LM_Compiler *c, char const *string):
    int constant = add_string_constant(c, string)
    int result = create_new_temporary(c)
    add_code(c, OPCODE_GET, result, constant, 0)
    return result

static int def get_variable(LM_Compiler *c, char const *string):
    """
    Compile code to get a named variable into a register and return that
    register.
    """
    # Maybe it's a parent or global variable?
    LM_CompilerFunction *f = c->current->parent
    while f:
        int *num = land_hash_get(f->locals, string)
        if num:
            return compile_named_variable_lookup(c, string)
        f = f->parent

    # Or maybe a local variable?
    int i = get_local_variable(c, string)
    if i: return i

    # Dang. The script to be compiled accesses a variable which we cannot find.

    return 0

static int def compile_dot(LM_Compiler *c, Node *n, int set, what):
    """
    Compile code to get the attribute of a variable into a register.
    """
    Node *left = n->first
    Token *ltoken = left->data
    int parent = get_variable(c, ltoken->string)
    int result = create_new_temporary(c)

    while True:
        Node *right = left->next
        Token *token
        int attribute
        if right->type == NODE_OPERAND:
            token = right->data
            if set:
                attribute = add_constant(c, token, LM_TYPE_STR)
                add_code(c, OPCODE_SET, parent, attribute, what)
                return what
            else:
                left = None
        else:
            left = right->first
            token = left->data
        attribute = add_constant(c, token, LM_TYPE_STR)
        add_code(c, OPCODE_DOT, result, parent, attribute)
        if not left: return result
        parent = result

static int def prepare_assignement(LM_Compiler *c, char const *string, int *what):
    """
    Prepares for assigning to a variable given by name.
    """
    # First: Assign to an existing global variable?
    int glob = get_global_variable(c, string)
    # Second: Create a new global variable?
    if not glob and c->current->is_global:
        glob = find_or_create_global(c, string)
    if glob:
        *what = add_string_constant(c, string)
        return 0
    # Third: Assign to an existing parent local?
    LM_CompilerFunction *f = c->current->parent
    while f:
        int *num = land_hash_get(f->locals, string)
        if num:
            *what = add_string_constant(c, string)
            return 0
        f = f->parent
    # Fourth: Assign to an existing local variable.
    # Fifth: Create a new local.
    *what = find_or_create_local(c, string)
    if *what == c->current->locals_count - 1:
        # just work on top free local
        c->current->locals_count--
        return 1
    return 2

static def finish_assignement(LM_Compiler *c, int *what, int slot, target):
    if target == 0:
        add_code(c, OPCODE_PUT, *what, slot, 0)
        return
    elif target == 1:
        c->current->locals_count++
    if *what != slot: add_code(c, OPCODE_ASS, *what, slot, 0)

static int def compile_binary_operation(LM_Compiler *c, Node *n, int opcode):
    int result = create_new_temporary(c)
    int temps = c->current->temporaries_count
    c->current->locals_count-- # can re-use the target temp
    int op1 = compile_node(c, n->first)
    int op2 = compile_node(c, n->first->next)
    c->current->locals_count = result + 1
    c->current->temporaries_count = temps
    add_code(c, opcode, result, op1, op2)
    return result

static int def is_parenthesis(LM_Compiler *c, Node *n):
    if n->type == NODE_OPERATION:
        Token *t = n->data
        if not strcmp(t->string, "("):
            return True
    return False

static int def is_or(LM_Compiler *c, Node *n):
    if n->type == NODE_OPERATION:
        Token *t = n->data
        if not strcmp(t->string, "or"):
            return True
    return False

static int def is_and(LM_Compiler *c, Node *n):
    if n->type == NODE_OPERATION:
        Token *t = n->data
        if not strcmp(t->string, "and"):
            return True
    return False

static def to_be_resolved(LM_Compiler *c, int tag):
    """
    Mark the current position to be later resolved as a forward jump.
    """
    JumpResolve *r
    land_alloc(r)
    r->codepos = c->current->code->n - 2
    r->tag = tag
    land_array_add(c->resolve, r)

static def resolve_to_here(LM_Compiler *c, int tag, int stop):
    """
    Resolve earlier forward jumps to the current position.
    """
    for int i = c->resolve->count - 1; i >= 0; i--:
        JumpResolve *r = land_array_get_nth(c->resolve, i)
        if r->tag == stop: return
        if r->tag == tag:
            int offset = c->current->code->n - r->codepos - 2
            c->current->code->buffer[r->codepos] = offset
            void *last = land_array_pop(c->resolve)
            if i < c->resolve->count:
                land_array_replace_nth(c->resolve, i, last)

static def remember_here(LM_Compiler *c, int tag):
    """
    Remember the current position for a later backward jump.
    """
    JumpResolve *r
    land_alloc(r)
    r->codepos = c->current->code->n
    r->tag = tag
    land_array_add(c->resolve, r)

static def resolve_to(LM_Compiler *c, int tag):
    """
    Resolve a backward jump.
    """
    for int i = 0; i < c->resolve->count; i++:
        JumpResolve *r = land_array_get_nth(c->resolve, i)
        if r->tag == tag:
            int offset = r->codepos - c->current->code->n
            c->current->code->buffer[c->current->code->n - 2] = offset
            return

static def resolve_remove_last(LM_Compiler *c, int tag):
    for int i = c->resolve->count - 1; i >= 0; i--:
        JumpResolve *r = land_array_get_nth(c->resolve, i)
        if r->tag == tag:
            void *last = land_array_pop(c->resolve)
            if i < c->resolve->count:
                land_array_replace_nth(c->resolve, i, last)
            return

static def compile_or_child(LM_Compiler *c, Node *n):
    while is_parenthesis(c, n):
        n = n->first
    if is_or(c, n):
        compile_or(c, n)
        # At this point, there should be some BRA codes jumping to the
        # yes point. We will simply add our own from the right operand
        # to that, for the case none of the branches is done at runtime.
    elif is_and(c, n):
        compile_and(c, n)
        # At this point, there should be some AND codes jumping to the
        # no point. We must resolve this no point to our right operand,
        # and do a jump to the yes point if the code got through to here,
        # at runtime.
        add_code(c, OPCODE_HOP, 0, 0, 0)
        to_be_resolved(c, JUMP_YES)
        resolve_to_here(c, JUMP_NO, JUMP_BARRIER)
    else:
        # Compile the expression.
        int result = compile_node(c, n)
        add_code(c, OPCODE_BRA, result, 0, 0)
        to_be_resolved(c, JUMP_YES)

        c->current->locals_count -= c->current->temporaries_count
        c->current->temporaries_count = 0

static def compile_and_child(LM_Compiler *c, Node *n):
    while is_parenthesis(c, n):
        n = n->first
    if is_or(c, n):
        compile_or(c, n)

        add_code(c, OPCODE_HOP, 0, 0, 0)
        to_be_resolved(c, JUMP_NO)

        resolve_to_here(c, JUMP_YES, JUMP_BARRIER)
    elif is_and(c, n):
        compile_and(c, n)
    else:
        # Compile the expression.
        int result = compile_node(c, n)
        add_code(c, OPCODE_AND, result, 0, 0)
        to_be_resolved(c, JUMP_NO)

        c->current->locals_count -= c->current->temporaries_count
        c->current->temporaries_count = 0

static def compile_and(LM_Compiler *c, Node *n):
    """
    Compiles an and. If a condition is not met, branches. If it runs through,
    all conditions have been met.
    """
    compile_and_child(c, n->first)
    compile_and_child(c, n->first->next)

static def compile_or(LM_Compiler *c, Node *n):
    """
    Compiles an or. This will compile code to do a branch if any condition is
    true. The code compiled directly afterwards is executed if no condition
    was true.
    """
    compile_or_child(c, n->first)
    compile_or_child(c, n->first->next)

static def compile_if(LM_Compiler *c, Node *n):
    Node *opnode = n->first
    while is_parenthesis(c, opnode):
        opnode = opnode->first
    if is_and(c, opnode):
        compile_and(c, opnode)
    elif is_or(c, opnode):
        compile_or(c, opnode)
        add_code(c, OPCODE_HOP, 0, 0, 0)
        to_be_resolved(c, JUMP_NO)
        resolve_to_here(c, JUMP_YES, JUMP_BARRIER)
    else: # assume an expression with the result used as truth value
        int result = compile_node(c, opnode)
        add_code(c, OPCODE_AND, result, 0, 0)
        to_be_resolved(c, JUMP_NO)
        c->current->locals_count -= c->current->temporaries_count
        c->current->temporaries_count = 0

    Node *block = n->first->next
    if block->type == NODE_BLOCK:
        compile_node(c, block)

static int def compile_conditional(LM_Compiler *c, Node *n):

    remember_here(c, JUMP_BARRIER)

    Node *ifnode = n->first
    while ifnode:
        if ifnode->type != NODE_OPERATION:
            fprintf(stderr, "Hu? need if/else/elif here..\n")
            ifnode = ifnode->next
            continue
        Token *token = ifnode->data
        if not strcmp(token->string, "if"):
            compile_if(c, ifnode)
            # Any else or elif following?
            if ifnode->next:
                add_code(c, OPCODE_HOP, 0, 0, 0)
                to_be_resolved(c, JUMP_OUT)
        if not strcmp(token->string, "while"):
            remember_here(c, JUMP_WHILE)
            compile_if(c, ifnode)
            add_code(c, OPCODE_HOP, 0, 0, 0)
            resolve_to(c, JUMP_WHILE)
            resolve_to_here(c, JUMP_BREAK, JUMP_WHILE)
            resolve_remove_last(c, JUMP_WHILE)

        elif not strcmp(token->string, "elif"):
            resolve_to_here(c, JUMP_NO, JUMP_BARRIER)
            compile_if(c, ifnode)
            # Any else or elif following?
            if ifnode->next:
                add_code(c, OPCODE_HOP, 0, 0, 0)
                to_be_resolved(c, JUMP_OUT) 
        elif not strcmp(token->string, "else"):
            resolve_to_here(c, JUMP_NO, JUMP_BARRIER)
            compile_node(c, ifnode->first)
            
        ifnode = ifnode->next

    resolve_to_here(c, JUMP_NO, JUMP_BARRIER)

    resolve_to_here(c, JUMP_OUT, JUMP_BARRIER)

    resolve_remove_last(c, JUMP_BARRIER)

    return 0   

static int def parse_function_call_parameters(LM_Compiler *c, Node *n,
    int *first, LandArray *paramnames):
    # TODO: Clarify if we want a limit of 256 params
    Token *t = n->data
    int params[256]
    int got_required[256]
    if paramnames:
        for int i = 0; i < 256; i++:
            got_required[i] = 0
    Node *param = n->first
    int nparams = 0
    int got_named = 0
    # What we do is, we compile all the parameter expressions and remember
    # into which local variables the resulting values go.
    while param:
        int positional = 1
        if param->type == NODE_OPERATION:
            Token *ptoken = param->data
            if not strcmp(ptoken->string, ","):
                param = param->first
                continue
            if not strcmp(ptoken->string, "("):
                param = param->first
                continue
            # An assignement here means a named parameter
            if not strcmp(ptoken->string, "="):
                Node *name = param->first
                Token *token = name->data
                int i = 0
                if paramnames:
                    for i = 0; i < paramnames->count; i++:
                        char const *str = land_array_get_nth(paramnames, i)
                        if not ustrcmp(token->string, str):
                            params[i] = compile_node(c, name->next)
                            got_required[i] = 1
                            if i + 1 > nparams:
                                nparams = i + 1
                            got_named++
                            break
                    if i == paramnames->count:
                        i = 0
                if i == 0:
                    pass
                    # TODO: additional named parameters
                positional = 0

        if positional:
            if got_named:
                fprintf(stderr, "Error: "
                    "Cannot use positional parameters after named parametes.\n")
            int result = compile_node(c, param)
            params[nparams] = result
            if paramnames and nparams < paramnames->count:
                got_required[nparams] = 1
            nparams++

        Node *parent = param->parent
        param = param->next
        while not param:
            if parent and parent != n:
                param = parent
                parent = param->parent
                param = param->next
            else:
                break

    if paramnames and nparams < paramnames->count:
        fprintf(stderr, "Error: "
            "Function \"%s\" has %d required parameters, "
            "but only %d of them %s provided!\n", t->string, paramnames->count,
            nparams, nparams == 1 ? "is" : "are")

    # Check if the arguments already are in the right order for passing on.
    int need_args = 0
    *first = params[0]
    for int i = 0; i < nparams; i++:
        if paramnames and i < paramnames->count and not got_required[i]:
            fprintf(stderr, "Error: "
                "Missing required parameter for index %d!\n", i)
        if params[i] < 1 or params[i] > 127 or params[i] != *first + i:
            need_args = 1
            break

    # If not, assign them all to consecutive locals.
    if need_args:
        *first = c->current->locals_count
        for int i = 0; i < nparams; i++:
            int num = create_new_temporary(c)
            add_code(c, OPCODE_ARG, num, params[i], 0)

    return nparams

static int def compile_operation(LM_Compiler *c, Node *n):
    """
    Compile an operation, and return the local which has the result, or
    0 if none.
    """
    Token *token = n->data

    if not strcmp(token->string, "+"):
        return compile_binary_operation(c, n, OPCODE_ADD)
    elif not strcmp(token->string, "-"):
        return compile_binary_operation(c, n, OPCODE_SUB)
    elif not strcmp(token->string, "*"):
        return compile_binary_operation(c, n, OPCODE_MUL)
    elif not strcmp(token->string, "/"):
        return compile_binary_operation(c, n, OPCODE_DIV)
    elif not strcmp(token->string, "<"):
        return compile_binary_operation(c, n, OPCODE_LOW)
    elif not strcmp(token->string, ">"):
        return compile_binary_operation(c, n, OPCODE_BIG)
    elif not strcmp(token->string, "=="):
        return compile_binary_operation(c, n, OPCODE_SAM)
    elif not strcmp(token->string, "."):
        return compile_dot(c, n, 0, 0)

    elif not strcmp(token->string, "="):
        Token *target = n->first->data
        if not strcmp(target->string, "."):
            # This is not an assignement to a variable, but to an attribute
            # thereof.
            int slot = compile_node(c, n->first->next)
            compile_dot(c, n->first, 1, slot)
            return slot
        else:
            int what
            int where = prepare_assignement(c, target->string, &what)
            int slot = compile_node(c, n->first->next)
            finish_assignement(c, &what, slot, where)
            return what

    elif not strcmp(token->string, ","):
        # FIXME
        return 0

    elif not strcmp(token->string, "("):
        if not n->first: return 0
        return compile_node(c, n->first)
    elif not strcmp(token->string, "continue"):
        add_code(c, OPCODE_HOP, 0, 0, 0)
        resolve_to(c, JUMP_WHILE)
        return 0
    elif not strcmp(token->string, "break"):
        add_code(c, OPCODE_HOP, 0, 0, 0)
        to_be_resolved(c, JUMP_BREAK)
        return 0
    elif not strcmp(token->string, "use"):
        Node *param = n->first
        while param:
            if param->type == NODE_OPERAND:
                static int used = 1
                Token *paramtoken = param->data
                land_hash_insert(c->using, paramtoken->string, &used)
                printf("Now using %s.\n", paramtoken->string)
                param = param->next
            else:
                param = param->first
        return 0
    elif not strcmp(token->string, "return"):
        int result = 0
        if n->first:
            result = compile_node(c, n->first)
        add_code(c, OPCODE_RET, result, 0, 0)
        return 0
    else: # function call
        int first, nparams

        if not strcmp(token->string, "print"):
            nparams = parse_function_call_parameters(c, n, &first, None)
            add_code(c, OPCODE_FLU, first, nparams, 0)
        else:
            int *using = land_hash_get(c->using, token->string)
            if using:
                nparams = parse_function_call_parameters(c, n, &first, None)
                int constant = add_string_constant(c, token->string)
                add_code(c, OPCODE_USE, constant, first, nparams)
                return 0

            n->type = NODE_OPERAND
            int result = compile_node(c, n)
            if not result:
                token_err(c->sa->tokenizer, token,
                    "Could not compile call to unknown function \"%s\".\n",
                    token->string)
            LM_CompilerFunction *f = land_array_get_nth(c->functions,  result)
            nparams = parse_function_call_parameters(c, n, &first, f->parameters)
            add_code(c, OPCODE_FUN, result, first, nparams)
            return 0
    return 0

static int def compile_statement(LM_Compiler *c, Node *n):
    if n->first:
        compile_node(c, n->first)
        c->current->locals_count -= c->current->temporaries_count
        c->current->temporaries_count = 0
    return 0

static int def compile_function(LM_Compiler *c, Node *n):
    LM_CompilerFunction *current = c->current

    Node *name = n->first
    Token *nametoken = name->data

    int what
    int where = prepare_assignement(c, nametoken->string, &what)

    int id = land_array_count(c->functions)
    int slot = create_new_temporary(c)
    add_code(c, OPCODE_DEF, slot, id, 0)

    finish_assignement(c, &what, slot, where)

    c->current = function_new(current)
    # The first constant in every frame is always None.
    new_constant(c)
    land_array_add(c->functions, c->current)

    # Add parameters as named locals.
    Node *n2 = name->next
    while n2 and n2->type == NODE_TOKEN:
        Token *token = n2->data
        if token->type != TOKEN_SYMBOL:
            find_or_create_local(c, token->string)
            land_array_add(c->current->parameters, land_strdup(token->string))
        n2 = n2->next

    if n2->type == NODE_BLOCK:
        compile_node(c, n2)

    # If no possible codepath can reach here (most commonly because there is
    # an unconditional return-with-value statement just before), we could
    # leave this out.
    # Constant 128 is perpetual nothingness (None).
    add_code(c, OPCODE_RET, 128, 0, 0)

    c->current = current

    c->current->locals_count -= c->current->temporaries_count
    c->current->temporaries_count = 0

    return slot

static int def compile_block(LM_Compiler *c, Node *n):
    Node *n2 = n->first
    while n2:
        compile_node(c, n2)
        n2 = n2->next
    return 0

static int def compile_operand(LM_Compiler *c, Node *n):
    Token *token = n->data
    if token->type == TOKEN_ALPHANUM:
        if token->string[0] >= '0' and token->string[0] <= '9':
            return add_constant(c, token, LM_TYPE_NUM)
        else:
            int result = get_variable(c, token->string)
            if not result:
                fprintf(stderr, "%s: %d: %d: ", c->sa->tokenizer->filename,
                    token->line, token->column)
                fprintf(stderr, "Variable %s treated as None.\n", token->string)
            return result
    elif token->type == TOKEN_STRING:
        return add_constant(c, token, LM_TYPE_STR)
    elif token->type == TOKEN_SYMBOL:
        if not strcmp(token->string, "{"):
            int x = create_new_local(c)
            add_code(c, OPCODE_NEW, x, 0, 0)
            return x
    return 0

int def compile_node(LM_Compiler *c, Node *n):
    if n->type == NODE_BLOCK:
        return compile_block(c, n)
    elif n->type == NODE_STATEMENT:
        return compile_statement(c, n)
    elif n->type == NODE_STATEMENT_CONDITIONAL:
        return compile_conditional(c, n)
    elif n->type == NODE_FUNCTION:
        return compile_function(c, n)
    elif n->type == NODE_OPERATION:
        return compile_operation(c, n)
    elif n->type == NODE_OPERAND:
        return compile_operand(c, n)
    return 0

def lm_compiler_debug(LM_Compiler *c, FILE *out):
    for int i = 0; i < c->functions->count; i++:
        LM_CompilerFunction *f = c->functions->data[i]
        fprintf(out, "function %d (%d locals, %d constants):\n", i, f->locals_needed,
            f->constants->count)

        fprintf(out, " parameters:")
        for int j = 0; j < f->parameters->count; j++:
            char const *str = land_array_get_nth(f->parameters, j)
            fprintf(out, " %s", str)
        fprintf(out, "\n")

        LandArray *keys = land_hash_keys(f->locals)
        for int j = 0; j < f->locals_needed; j++:
            fprintf(out, " local %d: ", j)
            for int k = 0; k < keys->count; k++:
                char *ke = land_array_get_nth(keys, k)
                if ke:
                    int *data = land_hash_get(f->locals, ke)
                    if data and *data == j:
                        fprintf(out, "%s\n", ke)
                        goto found
            fprintf(out, "[internal]\n")
            label found
        land_array_destroy(keys)

        for int j = 0; j < f->constants->count; j++:
            fprintf(out, " constant %d: ", j | 128)
            LM_Object *val = f->constants->data[j]
            if (val->header.type == LM_TYPE_NUM) fprintf(out, "%.1f", val->value.num)
            if (val->header.type == LM_TYPE_STR) fprintf(out, "%s", (char *)val->value.pointer)
            printf("\n")

        fprintf(out, " code:\n")
        lm_machine_debug_code(f->code->buffer, f->code->n, " ", out)

def lm_compiler_output(LM_Compiler *c, PACKFILE *out):
    for int i = 0; i < c->functions->count; i++:
        LM_CompilerFunction *f = c->functions->data[i]
        # write required memory
        pack_iputl(f->locals_needed, out)

        # write variable names
        LandArray *keys = land_hash_keys(f->locals)
        pack_iputl(keys->count, out)
        for int j = 0; j < keys->count; j++:
            char *ke = land_array_get_nth(keys, j)
            int *data = land_hash_get(f->locals, ke)
            pack_fwrite(ke, strlen(ke) + 1, out)
            pack_iputl(*data, out)

        # write constants
        pack_iputl(f->constants->count, out)
        for int j = 0; j < f->constants->count; j++:
            LM_Object *val = f->constants->data[j]
            pack_iputl(val->header.type, out)
            if val->header.type == LM_TYPE_NUM: pack_iputl(val->value.num, out)
            if val->header.type == LM_TYPE_STR: pack_fwrite(val->value.pointer,
                strlen(val->value.pointer) + 1, out)
        land_array_destroy(keys)

        # write code
        pack_iputl(f->code->n, out)
        for int j = 0; j < f->code->n; j++:
            char opcode = f->code->buffer[j]
            pack_putc(opcode, out)

def lm_compiler_compile(LM_Compiler *c):
    """
    Given a syntax tree, produce machine code.
    """

    c->resolve = land_array_new()
    c->current = function_new(None)
    # The first constant in every frame is always None.
    new_constant(c)
    c->current->is_global = 1
    land_array_add(c->functions, c->current)
    c->global_function = c->current

    compile_node(c, c->sa->root)
    add_code(c, OPCODE_END, 0, 0, 0)

    lm_compiler_debug(c, stderr)