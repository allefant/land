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

def compile(char const *input, char const *output):
    fprintf(stderr, "Compiling %s.\n", input)
    Tokenizer *t = tokenizer_new_from_file(input)
    if not t:
        fprintf(stderr, "Cannot read %s.\n", input)
        land_set_exitcode(1)
        return

    tokenizer_tokenize(t)

    SyntaxAnalyzer *sa = syntax_analyzer_new_from_tokenizer(t)
    syntax_analyzer_parse(sa)
    syntax_analyzer_analyze(sa)

    LM_Compiler *c = lm_compiler_new_from_syntax_analyzer(sa)
    lm_compiler_compile(c)

    if output:
        PACKFILE *f = pack_fopen(output, "wb")
        lm_compiler_output(c, f)
        pack_fclose(f)

    lm_compiler_destroy(c)

def execute(char const *input):

    LM_Machine *m

    if not strcmp(input + strlen(input) - 6, ".spell"):
        # TODO: Compare md5 sum to see if we need to recompile at all. Need to
        # also store the md5 sum of the source in the compiled version, to have
        # something to compare against.
        char output[strlen(input) - 1 + 1]
        strncpy(output, input, strlen(input) - 6)
        strcpy(output + strlen(input) - 6, ".code")
        compile(input, output)
        m = lm_machine_new_from_file(output)
    else:
        m = lm_machine_new_from_file(input)

    fprintf(stderr, "Executing %s.\n", input)

    lm_machine_debug(m, stderr)

    lm_machine_use(m, "test", test)
    lm_machine_reset(m)
    lm_machine_continue(m)

    lm_machine_destroy_completely(m)

def usage():
    fprintf(stderr, "usage:\n")
    fprintf(stderr, "spell compile input.spell [output.code]\n")
    fprintf(stderr, "spell execute input.spell|input.code\n")
    land_set_exitcode(-1)

def start():
    land_init()
    if land_argc >= 2:
        if not ustrcmp(land_argv[1], "compile") or\
            not ustrcmp(land_argv[1], "com") or\
            not ustrcmp(land_argv[1], "c"):
            if land_argc == 3:
                compile(land_argv[2], None)
            elif land_argc == 4:
                compile(land_argv[2], land_argv[3])
            else:
                usage()
        elif not ustrcmp(land_argv[1], "execute") or\
            not ustrcmp(land_argv[1], "exe") or\
            not ustrcmp(land_argv[1], "e"):
            if land_argc == 3:
                execute(land_argv[2])
            else:
                usage()
        else:
            usage()
    else:
        usage()

land_use_main(start)