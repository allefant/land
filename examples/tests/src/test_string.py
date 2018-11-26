import global land.land

str test_name
bool test_failed

static macro _test(name):
    _test_before(***name)
    _test_******name()
    _test_after()

def _test_before(str name):
    test_name = name
    test_failed = False

def _test_after:
    _done()

def _done:
    if test_failed:
        printf("%-20s %sFAIL%s\n", test_name, land_color_bash("red"),
            land_color_bash(""))
    else:
        printf("%-20s %sPASS%s\n", test_name, land_color_bash("green"),
            land_color_bash(""))

def _assert_equals(str actual, str expected):
    test_failed = not land_equals(actual, expected)
    if test_failed:
        printf("actual: '%s'\n", actual)
        printf("expected: '%s'\n", expected)

def _debug_print(char *s):
    printf("\"")
    while True:
        int c = land_utf8_char(&s)
        if not c: break
        printf("\\u%04x", c)
    printf("\"")

def test_string:
    _test(insert)
    _test(insert2)
    _test(insert3)
    _test(lowercase)

def _test_insert:
    char* s = land_strdup("")
    s = land_utf8_realloc_insert(s, 0, L'€')
    _assert_equals(s, "€")
    s = land_utf8_realloc_insert(s, 0, L' ')
    _assert_equals(s, " €")
    s = land_utf8_realloc_insert(s, -1, L'x')
    _assert_equals(s, " €x")

def _test_insert2:
    char* s = land_strdup("")
    int c = 'A'
    for int i in range(5):
        s = land_utf8_realloc_insert(s, -1, c++)
        s = land_utf8_realloc_insert(s, 0, c++)
    _assert_equals(s, "JHFDBACEGI")

def _test_insert3:
    char* s = land_strdup("")
    int c = 0x1000
    for int i in range(5):
        s = land_utf8_realloc_insert(s, -1, c++)
        s = land_utf8_realloc_insert(s, 0, c++)
    _assert_equals(s, "\u1009\u1007\u1005\u1003\u1001\u1000\u1002\u1004\u1006\u1008")

def _test_lowercase:
    char* s = land_strdup("ABC")
    char* t = land_lowercase_copy(s)
    _assert_equals(t, "abc")
