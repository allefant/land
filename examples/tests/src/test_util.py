import land.land

def test_want(str name) -> bool:
    if land_argc == 1:
        return True
    for int i in range(1, land_argc):
        str key = land_argv[i]
        if land_ends_with(key, "*"):
            char k[strlen(key) + 1]
            strcpy(k, key)
            k[strlen(key) - 1] = 0
            if land_starts_with(name, k):
                return True
        else:
            if land_equals(name, key):
                return True
    return False

str _test_name
bool _test_failed
void (*_before_cb)() = None
void (*_after_cb)() = None

macro test(name):
    if test_want(***name):
        test_do_before(***name)
        _test_******name()
        test_do_after()

def test_current -> str:
    return _test_name

def test_do_before(str name):
    _test_name = name
    _test_failed = False
    if _before_cb:
        _before_cb()

def test_failed():
    _test_failed = True

def test_do_after:
    if _after_cb:
        _after_cb()

    if _test_failed:
        printf("%-20s %sFAIL%s\n", _test_name, land_color_bash("red"),
            land_color_bash(""))
    else:
        printf("%-20s %sPASS%s\n", _test_name, land_color_bash("green"),
            land_color_bash(""))

def assert_equals(str actual, str expected):
    _test_failed = not land_equals(actual, expected)
    if _test_failed:
        printf("actual: '%s'\n", actual)
        printf("expected: '%s'\n", expected)

def assert_bool(bool actual, expected, str explanation):
    _test_failed = actual != expected
    if _test_failed:
        print("%s is %i but should be %i", explanation, actual, expected)

def assert_int(int actual, expected, str explanation):
    _test_failed = actual != expected
    if _test_failed:
        print("%s is %i but should be %i", explanation, actual, expected)

def assert_string(str value, str expected):
    if not land_equals(value, expected): _test_failed = True
    
def assert_length(LandArray* value, int expected):
    if land_array_count(value) != expected: _test_failed = True

def assert_entries(LandHash* value, int expected):
    if land_hash_count(value) != expected: _test_failed = True

def assert_files_identical(str a, b):
    LandBuffer* ba = land_buffer_read_from_file(a)
    LandBuffer* bb = land_buffer_read_from_file(b)
    if land_buffer_compare(ba, bb) != 0: _test_failed = True

def test_before(void *cb):
    _before_cb = cb

def test_after(void *cb):
    _after_cb = cb