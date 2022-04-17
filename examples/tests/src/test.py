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

# argument is either * to run all tests or name of a single test to run
def main(int argc, char** argv) -> int:
    land_argc = argc
    land_argv = argv
    land_init()

    test_camera()
    test_random()
    test_yml()
    test_collision()
    test_widget()
    test_string()
    test_csg()
    test_util2d()

    return 0
