import global land
import token, parser, syntax, compiler

def test(LM_Machine *m):
    int first = m->param_first
    int count = m->param_count
    printf("test")
    for int i = 0; i < count; i++:
        printf(" ")
        LM_ObjectHeader *o = lm_machine_get_value(m, first + i)
        lm_machine_output(m, o)
    printf("\n")

def userdict(LM_Machine *m):
    LM_Object *name = (void *)m->name
    LM_Object *value = (void *)m->value
    if m->set:
        printf("set %s %s\n",
            (char *)name->value.pointer,
            (char *)value->value.pointer)
    else:
        printf("get %s\n", (char *)name->value.pointer)

def compile(char const *input, char const *output, int debug):
    fprintf(stderr, "Compiling %s.\n", input)
    LM_Tokenizer *t = tokenizer_new_from_file(input)
    if not t:
        fprintf(stderr, "Cannot read %s.\n", input)
        land_set_exitcode(1)
        return

    tokenizer_tokenize(t, debug)

    SyntaxAnalyzer *sa = syntax_analyzer_new_from_tokenizer(t)
    syntax_analyzer_parse(sa, debug)
    syntax_analyzer_analyze(sa, debug)

    LM_Compiler *c = lm_compiler_new_from_syntax_analyzer(sa)
    lm_compiler_compile(c, debug)

    if output:
        PACKFILE *f = pack_fopen(output, "wb")
        lm_compiler_output(c, f)
        pack_fclose(f)

    lm_compiler_destroy(c)

static def run_machine(LM_Machine *m):
    lm_machine_debug(m, m->main_module, stderr)

    lm_machine_use(m, "userdict", userdict)
    lm_machine_use(m, "test", test)
    lm_machine_reset(m)
    lm_machine_continue(m)

def execute(char const *input, int debug):

    LM_Machine *m

    if not strcmp(input + strlen(input) - 6, ".spell"):
        # TODO: Compare md5 sum to see if we need to recompile at all. Need to
        # also store the md5 sum of the source in the compiled version, to have
        # something to compare against.
        char output[strlen(input) - 1 + 1]
        strncpy(output, input, strlen(input) - 6)
        strcpy(output + strlen(input) - 6, ".code")
        compile(input, output, debug)
        m = lm_machine_new_from_file(output)
    else:
        m = lm_machine_new_from_file(input)

    fprintf(stderr, "Executing %s.\n", input)
    run_machine(m)

    lm_machine_destroy(m)

def interpret(char const *input, int debug):
    fprintf(stderr, "Interpreting %s.\n", input)

    LM_Compiler *c = lm_compiler_new_from_file(input, debug)
    if not c:
        fprintf(stderr, "Cannot compile %s.\n", input)
        land_set_exitcode(1)
        return

    lm_compiler_compile(c, debug)
    LandBuffer *buffer = land_buffer_new()
    PACKFILE *pf = land_buffer_write_packfile(buffer)
    lm_compiler_output(c, pf)
    pack_fclose(pf)

    lm_compiler_destroy(c)

    printf("Bytecode size: %d\n", buffer->n)

    land_buffer_write_to_file(buffer, "test.dump")

    LM_Machine *m = lm_machine_new_from_buffer(buffer)
    land_buffer_del(buffer)

    run_machine(m)

    lm_machine_destroy(m)


def usage():
    fprintf(stderr, "usage:\n")
    fprintf(stderr, "spell c[ompile] input.spell [output.code]\n")
    fprintf(stderr, "spell e[xecute] input.spell|input.code\n")
    fprintf(stderr, "spell i[nterpret] input.spell\n")
    land_set_exitcode(-1)

def start():
    land_init()
    int debug = 1
    if land_argc >= 2:
        if not ustrcmp(land_argv[1], "compile") or\
            not ustrcmp(land_argv[1], "com") or\
            not ustrcmp(land_argv[1], "co") or\
            not ustrcmp(land_argv[1], "c"):
            if land_argc == 3:
                compile(land_argv[2], None, debug)
            elif land_argc == 4:
                compile(land_argv[2], land_argv[3], debug)
            else:
                usage()
        elif not ustrcmp(land_argv[1], "execute") or\
            not ustrcmp(land_argv[1], "exe") or\
            not ustrcmp(land_argv[1], "ex") or\
            not ustrcmp(land_argv[1], "e"):
            if land_argc == 3:
                execute(land_argv[2], debug)
            else:
                usage()
        elif not ustrcmp(land_argv[1], "interpret") or\
            not ustrcmp(land_argv[1], "int") or\
            not ustrcmp(land_argv[1], "in") or\
            not ustrcmp(land_argv[1], "i"):
            if land_argc == 3:
                interpret(land_argv[2], debug)
            else:
                usage()
        else:
            usage()
    else:
        usage()

land_use_main(start)