import global land.land
import test_util

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

def test_yml:
    test(yaml1)
    test(yaml2)
    test(yaml3)
    test(yaml4)
    test(yaml5)
    test(yaml6)
