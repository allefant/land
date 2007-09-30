import global allegro
import global land
import global jpeglib, jerror

static class my_src_mgr:
    struct jpeg_source_mgr pub
    JOCTET eoi_buffer[2]

static def init_source(j_decompress_ptr cinfo):
    pass

static int def fill_input_buffer(j_decompress_ptr cinfo):
    return 1

static def skip_input_data(j_decompress_ptr cinfo, long num_bytes):
    my_src_mgr *src = (void *)cinfo->src

    if num_bytes > 0:
        while num_bytes > (long)src->pub.bytes_in_buffer:
            num_bytes -= (long)src->pub.bytes_in_buffer
            fill_input_buffer(cinfo)

    src->pub.next_input_byte += num_bytes
    src->pub.bytes_in_buffer -= num_bytes

static def term_source(j_decompress_ptr cinfo):
    pass

def jpeg_memory_src(j_decompress_ptr cinfo, unsigned char const *buffer,
    size_t bufsize):
    my_src_mgr *src

    if not cinfo->src:
        cinfo->src = (*cinfo->mem->alloc_small)((void *)cinfo, JPOOL_PERMANENT,
            sizeof(my_src_mgr));

    src = (void *)cinfo->src
    src->pub.init_source = init_source
    src->pub.fill_input_buffer = fill_input_buffer
    src->pub.skip_input_data = skip_input_data
    src->pub.resync_to_restart = jpeg_resync_to_restart
    src->pub.term_source = term_source

    src->pub.next_input_byte = buffer
    src->pub.bytes_in_buffer = bufsize

static BITMAP *def load_jpg_helper(FILE *f, unsigned char *memory, int size):
    struct jpeg_decompress_struct cinfo
    struct jpeg_error_mgr jerr

    cinfo.err = jpeg_std_error(&jerr)

    jpeg_create_decompress(&cinfo)
    if f: jpeg_stdio_src(&cinfo, f)
    else: jpeg_memory_src(&cinfo, memory, size)
    jpeg_read_header(&cinfo, TRUE)
    jpeg_start_decompress(&cinfo)

    int w = cinfo.output_width
    int h = cinfo.output_height
    int s = cinfo.output_components

    BITMAP *bmp = create_bitmap_ex(24, w, h)

    unsigned char *buffer[1]
    unsigned char temp[w * s]
    buffer[0] = temp

    unsigned char *p = bmp->dat

    while (int)cinfo.output_scanline < h:
        int j = cinfo.output_scanline
        jpeg_read_scanlines(&cinfo, (void *)buffer, 1)
        if s == 1:
            for int i = 0; i < w; i++:
                unsigned char c = buffer[0][i]
                p[j * w * 3 + i * 3 + 0] = c
                p[j * w * 3 + i * 3 + 1] = c
                p[j * w * 3 + i * 3 + 2] = c
        elif s == 3:
            for int i = 0; i < w; i++:
                unsigned char r = buffer[0][i * s + 0]
                unsigned char g = buffer[0][i * s + 1]
                unsigned char b = buffer[0][i * s + 2]
                p[j * w * 3 + i * 3 + 0] = r
                p[j * w * 3 + i * 3 + 1] = g
                p[j * w * 3 + i * 3 + 2] = b
        else:
            fprintf(stderr, "Error! Cannot read JPEG data.\n")
            return None

    jpeg_finish_decompress(&cinfo)
    jpeg_destroy_decompress(&cinfo)

    return bmp

BITMAP *def load_jpg(char const *filename, PALETTE pal):
    FILE *f = fopen(filename, "rb")
    if not f: return NULL
    BITMAP *bmp = load_jpg_helper(f, None, 0)
    fclose(f)
    return bmp

BITMAP *def load_memory_jpg(char *memory, int size):
    return load_jpg_helper(None, (void *)memory, size)
   