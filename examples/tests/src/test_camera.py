import global land.land
import test_util

def _test(LandCamera cam, double result, expected):
    _test2("", cam, result, expected)

def _test2(str name, LandCamera cam, double result, expected):
    double epsilon = 0.000001
    double differ = fabs(result - expected)
    if differ > epsilon:
        print("%s: expected %f but got %f", name, expected, result)
        print("p: % .3f % .3f % .3f", cam.p.x, cam.p.y, cam.p.z)
        print("x: % .3f % .3f % .3f", cam.x.x, cam.x.y, cam.x.z)
        print("y: % .3f % .3f % .3f", cam.y.x, cam.y.y, cam.y.z)
        print("z: % .3f % .3f % .3f", cam.z.x, cam.z.y, cam.z.z)
        test_failed()

LandCamera cam

def test_camera:
    print("roll and pitch etc.")
    test(pitch1)
    test(pitch2)
    test(pitch3)
    test(pitch4)
    test(pitch5)
    test(roll1)
    test(roll2)
    test(roll3)
    test(roll4)
    test(roll1b)
    test(roll2b)
    test(roll3b)
    test(yaw1)
    test(yaw2)
    test(pitch1_b)
    test(pitch2_b)
    test(pitch3_b)
    test(pitch4_b)
    test(pitch5_b)
    test(yaw2b)

def _test_pitch1:
    # identity matrix means z (back) is 0/0/1 so we look straight down
    # initially
    cam = land_camera_identity()
    _test(cam, land_camera_get_pitch(&cam), pi / 2)

def _test_pitch2:
    # we rotate up by pi / 2, therefore we are level
    cam = land_camera_identity()
    land_camera_change_freely(&cam, -pi / 2, 0, 0)
    _test(cam, land_camera_get_pitch(&cam), 0)

def _test_pitch3:
    # we rotate down by pi / 2, now we're upside down
    cam = land_camera_identity()
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    _test(cam, land_camera_get_pitch(&cam), -pi)

def _test_pitch4:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, pi * 1.5, 0, 0)
    _test(cam, land_camera_get_pitch(&cam), 0)

def _test_pitch5:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, pi * 3 / 4, 0, 0)
    _test(cam, land_camera_get_pitch(&cam), -pi * 3 / 4)

def _test_pitch1_b:
    # we rotate down pi / 2 to look down
    cam = land_camera_identity()
    cam.z_is_up = True
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    _test2("pitch1 B", cam, land_camera_get_pitch(&cam), pi / 2)

def _test_pitch2_b:
    cam = land_camera_identity()
    cam.z_is_up = True
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    land_camera_change_freely(&cam, -pi / 2, 0, 0)
    _test2("pitch1 B", cam, land_camera_get_pitch(&cam), 0)

def _test_pitch3_b:
    cam = land_camera_identity()
    cam.z_is_up = True
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    _test2("pitch3 B", cam, land_camera_get_pitch(&cam), -pi)

def _test_pitch4_b:
    cam = land_camera_identity()
    cam.z_is_up = True
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    land_camera_change_freely(&cam, pi * 1.5, 0, 0)
    _test2("pitch3 B", cam, land_camera_get_pitch(&cam), 0)

def _test_pitch5_b:
    cam = land_camera_identity()
    cam.z_is_up = True
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    land_camera_change_freely(&cam, pi * 0.75, 0, 0)
    _test2("pitch3 B", cam, land_camera_get_pitch(&cam), -pi * 0.75)

def _test_roll1:
    # we pitch up up pi / 2 first to look straight
    cam = land_camera_identity()
    land_camera_change_freely(&cam, -pi / 2, 0, 0)
    _test(cam, land_camera_get_roll(&cam), 0)

def _test_roll2:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, -pi / 2, 0, 0)
    land_camera_change_freely(&cam, 0, 0, pi / 2)
    _test(cam, land_camera_get_roll(&cam), -pi / 2)

def _test_roll3:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, -pi / 2, 0, 0)
    land_camera_change_freely(&cam, 0, 0, pi + pi / 2)
    _test(cam, land_camera_get_roll(&cam), pi / 2)

def _test_roll4:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, -pi / 2, 0, 0)
    land_camera_change_freely(&cam, 0, 0, pi + pi / 4)
    _test(cam, land_camera_get_roll(&cam), pi - pi / 4)

def _test_roll1b:
    cam = land_camera_identity()
    cam.z_is_up = True
    _test2("roll1 B", cam, land_camera_get_roll(&cam), 0)

def _test_roll2b:
    cam = land_camera_identity()
    cam.z_is_up = True
    land_camera_change_freely(&cam, 0, pi / 2, 0)
    _test2("roll2 B", cam, land_camera_get_roll(&cam), pi / 2)

def _test_roll3b:
    cam = land_camera_identity()
    cam.z_is_up = True
    land_camera_change_freely(&cam, 0, pi, 0)
    _test2("roll3 B", cam, land_camera_get_roll(&cam), -pi)

def _test_yaw1:
    # we pitch up up pi / 2 first to look straight
    cam = land_camera_identity()
    land_camera_change_freely(&cam, -pi / 2, 0, 0)
    _test(cam, land_camera_get_yaw(&cam), pi)

def _test_yaw2:
    for int i in range(8):
        float exp = 2 * pi * i / 8 - pi
        if exp < -pi: exp += 2 * pi
        cam = land_camera_identity()
        land_camera_change_freely(&cam, -pi / 2, i * 2 * pi / 8, 0)
        _test(cam, land_camera_get_yaw(&cam), exp)

def _test_yaw2b:
    cam = land_camera_identity()
    cam.z_is_up = True
    for int i in range(8):
        char yaw[100]
        sprintf(yaw, "yaw2 B [%d]", 1 + i)
        float exp = 2 * pi * i / 8
        if exp >= pi: exp -= 2 * pi
        _test2(yaw, cam, land_camera_get_yaw(&cam), exp)
        land_camera_change_freely(&cam, 0, 0, 2 * pi / 8)
    
