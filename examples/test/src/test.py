import global land.land
import global land.yaml

def test_shuffle:
    for int i in range(100):
        int a[25]
        land_shuffle(a, 25)
        for int j in range(25):
            if a[j] == 0: printf("%s", land_color_bash("red"))
            if a[j] == 12: printf("%s", land_color_bash("green"))
            if a[j] == 24: printf("%s", land_color_bash("blue"))
            printf("%2d ", a[j])
            printf("%s", land_color_bash("end"))
        printf("\n")

def test_yaml1:
    LandYaml *y = land_yaml_new("test1.yaml")
    land_yaml_add_scalar(y, "a b c")
    land_yaml_save(y)
    land_yaml_destroy(y)

    LandYaml *y2 = land_yaml_load("test1.yaml")
    land_yaml_dump(y2)

def test_yaml2:
    LandYaml *y = land_yaml_new("test2.yaml")
    land_yaml_add_sequence(y)
    for int i in range(9):
        land_yaml_add_scalar_f(y, "entry %d", i)
    land_yaml_done(y)
    land_yaml_save(y)

    LandYaml *y2 = land_yaml_load("test2.yaml")
    land_yaml_dump(y2)

def test_yaml3:
    LandYaml *y = land_yaml_new("test3.yaml")
    land_yaml_add_mapping(y)
    for int i in range(9):
        land_yaml_add_scalar_f(y, "key %d", i)
        land_yaml_add_scalar_f(y, "value %d", i)
    land_yaml_done(y)
    land_yaml_save(y)

    LandYaml *y2 = land_yaml_load("test3.yaml")
    land_yaml_dump(y2)

def test_yaml4:
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
    land_yaml_dump(y2)

def main() -> int:
    land_init()

    #test_shuffle()
    test_yaml1()
    test_yaml2()
    test_yaml3()
    test_yaml4()

    return 0
