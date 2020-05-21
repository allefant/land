import global land.land
import global land.yaml

import collision
import test_widget
import test_string

macro _test(name):
    if _want_test(***name):
        _test_before(***name)
        _test_******name()
        _test_after()

str test_name
bool test_failed

def _test_before(str name):
    test_name = name
    test_failed = False

def _test_after:
    if test_failed:
        printf("%-20s %sFAIL%s\n", test_name, land_color_bash("red"),
            land_color_bash(""))
    else:
        printf("%-20s %sPASS%s\n", test_name, land_color_bash("green"),
            land_color_bash(""))

def assert_string(str value, str expected):
    if not land_equals(value, expected): test_failed = True
    
def assert_length(LandArray* value, int expected):
    if land_array_count(value) != expected: test_failed = True

def assert_entries(LandHash* value, int expected):
    if land_hash_count(value) != expected: test_failed = True

def assert_files_identical(str a, b):
    LandBuffer* ba = land_buffer_read_from_file(a)
    LandBuffer* bb = land_buffer_read_from_file(b)
    if land_buffer_compare(ba, bb) != 0: test_failed = True

def _test_shuffle:
    for int i in range(100):
        int a[25]
        land_shuffle(a, 25)
        int found = 0
        for int j in range(25):
            for int k in range(25):
                if a[k] == j:
                    found++
                    break
        if found != 25:
            test_failed = True
            break
        #    if a[j] == 0: printf("%s", land_color_bash("red"))
        #    if a[j] == 12: printf("%s", land_color_bash("green"))
        #    if a[j] == 24: printf("%s", land_color_bash("blue"))
        #    printf("%2d ", a[j])
        #    printf("%s", land_color_bash("end"))
        #printf("\n")

def _test_yaml1:
    LandYaml *y = land_yaml_new("test1.yaml")
    land_yaml_add_scalar(y, "a b c")
    land_yaml_save(y)
    land_yaml_destroy(y)

    LandYaml *y2 = land_yaml_load("test1.yaml")
    assert_string(land_yaml_get_scalar(y2.root), "a b c")

def _test_yaml2:
    LandYaml *y = land_yaml_new("test2.yaml")
    land_yaml_add_sequence(y)
    for int i in range(20):
        land_yaml_add_scalar_f(y, "entry %d", i)
    land_yaml_done(y)
    land_yaml_save(y)

    LandYaml *y2 = land_yaml_load("test2.yaml")
    assert_length(land_yaml_get_sequence(y2.root), 20)

def _test_yaml3:
    LandYaml *y = land_yaml_new("test3.yaml")
    land_yaml_add_mapping(y)
    for int i in range(20):
        land_yaml_add_scalar_f(y, "key %d", i)
        land_yaml_add_scalar_f(y, "value %d", i)
    land_yaml_done(y)
    land_yaml_save(y)

    LandYaml *y2 = land_yaml_load("test3.yaml")
    #land_yaml_dump(y2)
    assert_entries(land_yaml_get_mapping(y2.root), 20)

def _test_yaml4:
    LandYaml *y = land_yaml_new("test4.yaml")
    land_yaml_add_mapping(y)
    for int i in range(3):
        land_yaml_add_scalar_f(y, "key %d", i)
        land_yaml_add_sequence(y)
        for int j in range(5):
            land_yaml_add_scalar_f(y, "item %d", j)
        land_yaml_done(y)
    land_yaml_done(y)
    land_yaml_save(y)

    LandYaml *y2 = land_yaml_load("test4.yaml")
    #land_yaml_dump(y2)
    assert_entries(land_yaml_get_mapping(y2.root), 3)

def _test_yaml5:
    # read XML into our internal structure
    LandYaml *y = land_yaml_load_xml("../../data/test.xml")

    # write it out as .yaml
    land_yaml_rename(y, "test5.yaml")
    land_yaml_save(y)
    
    # and write it out as .xml
    land_yaml_rename(y, "test5.yaml.xml")
    land_yaml_save_xml(y)

    # load that xml and write it again
    LandYaml *y2 = land_yaml_load_xml("test5.yaml.xml")
    land_yaml_rename(y2, "test5b.yaml")
    land_yaml_save(y2)

    assert_files_identical("test5.yaml", "test5.yaml")

def _test_yaml6:
    LandYaml *y = land_yaml_new("test6.xml")
    land_yaml_xml_tag(y, "html")
    land_yaml_xml_tag(y, "body")
    land_yaml_xml_tag(y, "table")
    for int i in range(3):
        land_yaml_xml_tag(y, "tr")
        for int j in range(3):
            land_yaml_xml_tag(y, "td")
            char s[1024]
            sprintf(s, "%dx%d", i, j)
            land_yaml_xml_content(y, s)
            land_yaml_xml_end(y)
        land_yaml_xml_end(y)
    land_yaml_xml_end(y) # table
    land_yaml_xml_end(y) # body
    land_yaml_xml_end(y) # html
    land_yaml_save_xml(y)

def _test_camera:
    land_camera_tests()
    
def _test_collision:
    test_collision()
    
def _test_widget:
    test_widget()
    
def _test_string:
    test_string()

def _want_test(str name) -> bool:
    return land_equals(name, "string")

def main() -> int:
    land_init()

    _test(camera)
    _test(shuffle)
    _test(yaml1)
    _test(yaml2)
    _test(yaml3)
    _test(yaml4)
    _test(yaml5)
    _test(yaml6)
    _test(collision)
    _test(widget)
    _test(string)

    return 0
