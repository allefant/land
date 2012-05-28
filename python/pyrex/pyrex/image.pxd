cdef extern from "land.h":
    cdef struct LandImage:
        pass

cdef class Image:
    cdef LandImage *wrapped
