#!/usr/bin/env python
import os, sys
from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

platform = "linux"
if "mingw" in sys.argv: platform = "mingw"

libraries = ["landd", "ldpng", "png", "jpgal", "fudgefont", "agl",
    "freetype", "m"]

library_dirs = [".."]
extra_link_args = []
extra_compile_args = []

if platform == "linux":
    libraries.extend(["GL", "GLU"])
    args = os.popen("allegro-config --shared debug").read()
    for arg in args.split():
        if arg[:2] == '-L': library_dirs.append(arg[2:])
        elif arg[:2] == '-l': libraries.append(arg[2:])
        else: extra_link_args.append(arg)
    extra_compile_args.append("-I/usr/local/include/land")
else:
    libraries.extend(["opengl32", "glu32"])
    extra_compile_args.extend(["-I../pro", "-I../h", "-DALLEGRO_STATICLINK"])

modules = ["land", "main", "runner", "display", "keyboard", "mouse", "image",
    "text"]
ext_modules = []

for module in modules:
    ext_modules.append(Extension(
        "land." + module, ["pyrex/" + module + ".pyx"],
        library_dirs = library_dirs,
        libraries = libraries,
        extra_link_args = extra_link_args,
        extra_compile_args = extra_compile_args))

setup(
  name = "land",
  packages = ["land"],
  package_dir = {'land': 'pyrex'},
  ext_modules = ext_modules,
  cmdclass = {'build_ext': build_ext}
)

