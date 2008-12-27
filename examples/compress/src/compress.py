import global land/land
int def main():
    land_init()

    printf("Buffer 1\n")
    char const *str = "Land All New Design"
    printf("Contents: «%s»\n", str)
    LandBuffer *b = land_buffer_new()
    land_buffer_cat(b, str)
    printf("Uncompressed length: %d\n", b->n)
    land_buffer_compress(b)
    printf("Compressed length: %d (%.1f%%)\n", b->n,
        100.0 * b->n / strlen(str))
    printf("length (4 bytes): 0x%08x\n", *((uint32_t *)(b->buffer)))
    printf("compression method (1 byte): %d\n", b->buffer[4] & 15)
    printf("compression info: %d\n", (b->buffer[4] >> 4) & 15)
    printf("check (1 byte): %d [%d]\n", b->buffer[5] & 31,
        (unsigned char)b->buffer[4] * 256 + (unsigned char)b->buffer[5] )
    printf("dictionary: %s\n", b->buffer[5] & 32 ? "yes" : "no")
    printf("compression level: %d\n", (b->buffer[5] >> 6) & 3)
    int start = 6
    if b->buffer[5] & 32:
        start += 4
        printf("dictionary identifier (4 bytes): %08x", *((uint32_t *)(b->buffer + 6)))
    printf("Checksum (4 bytes): %08x\n", *((uint32_t *)(b->buffer + b->n - 4)))
    printf("Bitstream (%d bytes):", b->n - 4 - start)
    for int i = start; i < b->n - 4; i++:
        printf(" %02x", (unsigned char)b->buffer[i])
    printf("\n")
    land_buffer_decompress(b)
    printf("Uncompressed length: %d\n", b->n)
    char *de = land_buffer_finish(b)
    printf("Uncompressed: «%s»\n", de)
    land_free(de)

    printf("\nBuffer 2\n")
    LandBuffer *orig = land_buffer_read_from_file("src/compress.py")
    b = land_buffer_read_from_file("src/compress.py")
    printf("Uncompressed length: %d\n", b->n)
    land_buffer_compress(b)
    printf("Compressed length: %d (%.1f%%)\n", b->n, 100.0 * b->n / orig->n)
    land_buffer_decompress(b)
    printf("Uncompressed length: %d\n", b->n)
    printf("Difference: %d\n", land_buffer_compare(orig, b))

    return 0
