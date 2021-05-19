import global land.land
import test_util

def _test(LandCamera cam, double result, expected):
    double epsilon = 0.000001
    double differ = fabs(result - expected)
    if differ > epsilon:
        print("expected %f but got %f", expected, result)
        print("p: % .3f % .3f % .3f", cam.p.x, cam.p.y, cam.p.z)
        print("x: % .3f % .3f % .3f", cam.x.x, cam.x.y, cam.x.z)
        print("y: % .3f % .3f % .3f", cam.y.x, cam.y.y, cam.y.z)
        print("z: % .3f % .3f % .3f", cam.z.x, cam.z.y, cam.z.z)
        test_failed()

LandCamera cam

def test_camera:
    test(pitch1)
    test(pitch2)
    test(pitch3)
    test(pitch4)
    test(roll1)
    test(roll2)
    test(roll3)
    test(roll4)
    test(yaw1)
    test(yaw2)

def _test_pitch1:
    cam = land_camera_identity()
    _test(cam, land_camera_get_pitch(&cam), 0)

def _test_pitch2:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    _test(cam, land_camera_get_pitch(&cam), pi / 2)

def _test_pitch3:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    land_camera_change_freely(&cam, pi, 0, 0)
    _test(cam, land_camera_get_pitch(&cam), -pi / 2)

def _test_pitch4:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, pi * 3 / 4, 0, 0)
    _test(cam, land_camera_get_pitch(&cam), pi * 3 / 4)

def _test_roll1:
    cam = land_camera_identity()
    _test(cam, land_camera_get_roll(&cam), 0)

def _test_roll2:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, 0, pi / 2, 0)
    _test(cam, land_camera_get_roll(&cam), pi / 2)

def _test_roll3:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, 0, pi / 2, 0)
    land_camera_change_freely(&cam, 0, pi, 0)
    _test(cam, land_camera_get_roll(&cam), -pi / 2)

def _test_roll4:
    cam = land_camera_identity()
    land_camera_change_freely(&cam, 0, pi / 2, 0)
    land_camera_change_freely(&cam, 0, pi, 0)
    land_camera_change_freely(&cam, 0, -pi / 4, 0)
    _test(cam, land_camera_get_roll(&cam), -pi * 3 / 4)

def _test_yaw1:
    cam = land_camera_identity()
    _test(cam, land_camera_get_yaw(&cam), 0)

def _test_yaw2:
    for int i in range(8):
        float exp = 2 * pi * i / 8 - pi
        if exp < -pi: exp += 2 * pi
        cam = land_camera_identity()
        land_camera_change_freely(&cam, -pi / 2, i * 2 * pi / 8, 0)
        _test(cam, land_camera_get_yaw(&cam), exp)
