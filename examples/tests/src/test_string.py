import global land.land
import test_util

def test_string:
    test(insert)
    test(insert2)
    test(insert3)
    test(lowercase)
    test(prepend)
    test(prepend2)

def _test_insert:
    char* s = land_strdup("")
    s = land_utf8_realloc_insert(s, 0, L'€')
    assert_equals(s, "€")
    s = land_utf8_realloc_insert(s, 0, L' ')
    assert_equals(s, " €")
    s = land_utf8_realloc_insert(s, -1, L'x')
    assert_equals(s, " €x")

def _test_insert2:
    char* s = land_strdup("")
    int c = 'A'
    for int i in range(5):
        s = land_utf8_realloc_insert(s, -1, c++)
        s = land_utf8_realloc_insert(s, 0, c++)
    assert_equals(s, "JHFDBACEGI")

def _test_insert3:
    char* s = land_strdup("")
    int c = 0x1000
    for int i in range(5):
        s = land_utf8_realloc_insert(s, -1, c++)
        s = land_utf8_realloc_insert(s, 0, c++)
    assert_equals(s, "\u1009\u1007\u1005\u1003\u1001\u1000\u1002\u1004\u1006\u1008")

def _test_lowercase:
    char* s = land_strdup("ABC")
    char* t = land_lowercase_copy(s)
    assert_equals(t, "abc")

def _test_prepend:
    char* s = land_strdup("abcd")
    land_prepend(&s, "ef")
    assert_equals(s, "efabcd")

def _test_prepend2:
    char* s = land_strdup("mouth\",\"eye\",\"antler\"}")
    land_prepend(&s, "{\"")
    assert_equals(s, "{\"mouth\",\"eye\",\"antler\"}")
