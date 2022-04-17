import global land.land
import test_util

def test_random:
    test(shuffle)

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
            test_failed()
            break
        #    if a[j] == 0: printf("%s", land_color_bash("red"))
        #    if a[j] == 12: printf("%s", land_color_bash("green"))
        #    if a[j] == 24: printf("%s", land_color_bash("blue"))
        #    printf("%2d ", a[j])
        #    printf("%s", land_color_bash("end"))
        #printf("\n")
