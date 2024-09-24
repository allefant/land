import global land.land
import global land.yaml

import test_collision
import test_widget
import test_string
import test_yaml
import test_util
import test_camera
import test_csg
import test_random
import test_util2d
import test_file
import test_misc
import test_buffer
import test_threadpool

LandArray *suites

class TestSuite:
    char *name
    void *callback

def add_suite(char *name, void *callback) -> TestSuite*:
    TestSuite *self; land_alloc(self)
    self.name = land_strdup(name)
    self.callback = callback
    land_array_add(suites, self)
    return self

macro test_suite(name):
    for int i in range(1):
        add_suite(***name, test_******name)

def run_all:
    for TestSuite *s in suites:
        if test_want_suite(s.name):
            print("Running %s tests", s.name)
            suite_name = s.name
            ((void (*)())s.callback)()

def _print_all:
    for TestSuite *s in suites:
        print("%s", s.name)

# argument is either * to run all tests or name of a single test to run
def _com:
    land_find_data_prefix("data/")
    suites = land_array_new()

    test_suite(camera)
    test_suite(random)
    test_suite(yml)
    test_suite(collision)
    test_suite(widget)
    test_suite(string)
    test_suite(csg)
    test_suite(util2d)
    test_suite(file)
    test_suite(misc)
    test_suite(buffer)
    test_suite(threadpool)

    if land_equals(land_argv[1], "-h"):
        _print_all()
        return

    print("running tests")

    run_all()

    if tests_failed:
        print("%d/%d failed", tests_failed, tests_count)
    else:
        print("all %d succeeded", tests_count)

    land_set_exitcode(tests_failed == 0 ? 0 : 1)

land_commandline_example()
