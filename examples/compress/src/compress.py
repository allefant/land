import global land/land

def _com:
    land_find_data_prefix("data/")

    print("Buffer 1")
    char const *str = "Land All New Design"
    print("Contents: «%s»", str)
    LandBuffer *b = land_buffer_new()
    land_buffer_cat(b, str)
    print("Uncompressed length: %d", b->n)
    land_buffer_compress(b)
    print("Compressed length: %d (%.1f%%)", b->n,
        100.0 * b->n / strlen(str))
    print("length (4 bytes): 0x%08x", *((uint32_t *)(b->buffer)))
    print("compression method (1 byte): %d", b->buffer[4] & 15)
    print("compression info: %d", (b->buffer[4] >> 4) & 15)
    print("check (1 byte): %d [%d]", b->buffer[5] & 31,
        (unsigned char)b->buffer[4] * 256 + (unsigned char)b->buffer[5] )
    print("dictionary: %s", b->buffer[5] & 32 ? "yes" : "no")
    print("compression level: %d", (b->buffer[5] >> 6) & 3)
    uint64_t start = 6
    if b->buffer[5] & 32:
        start += 4
        printf("dictionary identifier (4 bytes): %08x", *((uint32_t *)(b->buffer + 6)))
    print("Checksum (4 bytes): %08x", *((uint32_t *)(b->buffer + b->n - 4)))
    print("Bitstream (%d bytes):", b->n - 4 - start)
    for uint64_t i = start while i < b->n - 4 with i++:
        printf(" %02x", (unsigned char)b->buffer[i])
    land_buffer_decompress(b)
    print("Uncompressed length: %d", b->n)
    char *de = land_buffer_finish(b)
    print("Uncompressed: «%s»", de)
    land_free(de)

    print("")
    print("Buffer 2")
    LandBuffer *orig = land_buffer_read_from_file("GPL-2")
    b = land_buffer_read_from_file("GPL-2")
    print("Uncompressed length: %d", b->n)
    land_buffer_compress(b)
    print("Compressed length: %d (%.1f%%)", b->n, 100.0 * b->n / orig->n)
    land_buffer_decompress(b)
    print("Uncompressed length: %d", b->n)
    print("Difference: %d", land_buffer_compare(orig, b))

    print("")
    print("Buffer 3")
    b = land_buffer_read_from_file("GPL-2.gz")
    land_buffer_decompress(b)
    print("Difference: %d", land_buffer_compare(orig, b))

    print("")
    print("Buffer 4")
    land_buffer_clear(orig)
    char word[1000]
    for int i in range(1000):
        word[i] = land_rand(0, 255)
    for int i in range(10000):
        land_buffer_add(orig, word, 1000)
        land_buffer_add_char(orig, i)
    b = land_buffer_copy(orig)
    land_buffer_compress(b)
    print("Original: %d", orig.n)
    print("Compressed: %d", b.n)
    land_buffer_decompress(b)
    print("Decompressoed: %d", b.n)
    print("Difference: %d", land_buffer_compare(orig, b))

land_commandline_example()
