import land

class LandArgumentParser:
    LandArray *arguments
    LandArray *remain

class LandArgument:
    char *long_name
    char *short_name
    char *default_value
    bool is_flag
    char *value

LandArgumentParser *_g_argp

def _init:
    if _g_argp: return
    land_alloc(_g_argp)
    _g_argp.arguments = land_array_new()
    _g_argp.remain = land_array_new()

def land_add_argument(str long_name, short_name, default_value, bool is_flag):
    _init()
    LandArgument *a; land_alloc(a)
    a.long_name = land_strdup(long_name)
    if short_name: a.short_name = land_strdup(short_name)
    if default_value:
        a.default_value = land_strdup(default_value)
    a.is_flag = is_flag
    land_array_add(_g_argp.arguments, a)

def land_argument(str long_name, short_name):
    land_add_argument(long_name, short_name, None, False)

def land_add_flag(str long_name, short_name):
    land_add_argument(long_name, short_name, None, True)

def land_argument_default(str long_name, short_name, default_value):
    land_add_argument(long_name, short_name, default_value, False)

def _find_long(str name) -> LandArgument*:
    for LandArgument *a in LandArray *_g_argp.arguments:
        if land_equals(name, a.long_name):
            return a
    return None

def _find_short(str name) -> LandArgument*:
    for LandArgument *a in LandArray *_g_argp.arguments:
        if a.short_name and land_equals(name, a.short_name):
            return a
    return None

def land_arguments_parse:
    LandArgument *take_value = None
    for int i in range(1, land_argc):
        str arg = land_argv[i]
        if take_value:
            take_value.value = land_strdup(arg)
            take_value = None
            continue
        if land_starts_with(arg, "-"):
            LandArgument *a
            if land_starts_with(arg, "--"):
                a = _find_long(arg + 2)
            else:
                a = _find_short(arg + 1)
            take_value = None
            if a:
                if a.is_flag:
                    a.value = "set"
                else:
                    take_value = a
            else:
                print("Unknown argument", arg)
            continue
        land_array_add(_g_argp.remain, land_strdup(arg))
    if take_value:
        print("Missing value for %s", take_value.long_name)
    for LandArgument *a in LandArray *_g_argp.arguments:
        if a.default_value and not a.value:
            a.value = a.default_value

def land_arg(str name) -> str:
    for LandArgument *a in LandArray *_g_argp.arguments:
        if land_equals(a.long_name, name):
            return a.value
    return None

def land_arg_remain(int i) -> str:
    return land_array_get_or_none(_g_argp.remain, i)

def land_arg_remain_all -> LandArray*:
    return _g_argp.remain
