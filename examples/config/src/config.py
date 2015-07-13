import global land.land

def main() -> int:
    land_init()

    LandProtobuf *p = land_protobuf_load("../../data/config.protobuf")

    int id
    uint64_t size
    while True:
        id = land_protobuf_next(p, &size)
        if not id:
            break
        if id == 1:
            printf("Object found (size %lu)\n", size)
            land_protobuf_sub_start(p, &size)
            uint64_t end1 = size
            while True:
                id = land_protobuf_next(p, &size)
                if not id:
                    break
                if id == 1:
                    char *s = land_protobuf_string(p, size)
                    printf("    Name found: %.*s\n", (int)size, s)
                elif id == 2:
                    printf("    Frames found (size %lu)\n", size)
                    land_protobuf_sub_start(p, &size)
                    uint64_t end12 = size
                    while True:
                        id = land_protobuf_next(p, &size)
                        if id == 0:
                            break
                        if id == 1:
                            char *s = land_protobuf_string(p, size)
                            printf("        Name found: %.*s\n", (int)size, s)
                        elif id == 2:
                            printf("        RotationQuaternion found (size %lu)\n", size)
                            land_protobuf_string(p, size)
                        elif id == 3:
                            printf("        Location found (size %lu)\n", size)
                            land_protobuf_string(p, size)
                        else:
                            land_protobuf_string(p, size)
                            printf("    (skipped %d/%lu)\n", id, size)

                    land_protobuf_sub_end(p, end12)
                elif id == 3:
                    printf("    ArmaturePart found (size %lu)\n", size)
                    land_protobuf_sub_start(p, &size)
                    uint64_t end12 = size
                    while True:
                        id = land_protobuf_next(p, &size)
                        if id == 0:
                            break
                        if id == 1:
                            char *s = land_protobuf_string(p, size)
                            printf("        Name found: %.*s\n", (int)size, s)
                        elif id == 2:
                            char *s = land_protobuf_string(p, size)
                            printf("        Parent found: %.*s\n", (int)size, s)
                        elif id == 3:
                            printf("        px = %f\n", land_protobuf_double(p))
                        elif id == 4:
                            printf("        py = %f\n", land_protobuf_double(p))
                        elif id == 5:
                            printf("        pz = %f\n", land_protobuf_double(p))
                        elif id == 6:
                            printf("        qw = %f\n", land_protobuf_double(p))
                        elif id == 7:
                            printf("        qx = %f\n", land_protobuf_double(p))
                        elif id == 8:
                            printf("        qy = %f\n", land_protobuf_double(p))
                        elif id == 9:
                            printf("        qz = %f\n", land_protobuf_double(p))
                        
                        else:
                            land_protobuf_string(p, size)
                            printf("    (skipped %d/%lu)\n", id, size)
                            
                    land_protobuf_sub_end(p, end12)
                elif id == 4:
                    printf("    Mesh found (size %lu)\n", size)
                    land_protobuf_sub_start(p, &size)
                    uint64_t end12 = size
                    while True:
                        id = land_protobuf_next(p, &size)
                        if id == 0:
                            break
                        if id == 1:
                            char *s = land_protobuf_string(p, size)
                            printf("        Name found: %.*s\n", (int)size, s)
                        elif id == 2:
                            printf("        Triangle found (size %lu)\n", size)
                            land_protobuf_string(p, size)
                        else:
                            land_protobuf_string(p, size)
                            printf("    (skipped %d/%lu)\n", id, size)
                            
                    land_protobuf_sub_end(p, end12)
                else:
                    land_protobuf_string(p, size)
                    printf("    (skipped %d/%lu)\n", id, size)

            land_protobuf_sub_end(p, end1)

    land_protobuf_destroy(p)

    return 0
