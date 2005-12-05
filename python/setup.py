#!/usr/bin/env python
import os
from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

libraries = ["land", "ldpng", "png", "glyphkeeper-agl", "agl", "GL", "GLU", "freetype"]
library_dirs = ["../"]
extra_link_args = []

args = os.popen("allegro-config --shared release").read()
for arg in args.split():
    if arg[:2] == '-L': library_dirs.append(arg[2:])
    elif arg[:2] == '-l': libraries.append(arg[2:])
    else: extra_link_args.append(arg)

modules = ["land", "main", "runner", "display", "keyboard", "mouse"]
ext_modules = []

for module in modules:
    ext_modules.append(Extension(
        "land." + module, ["pyrex/" + module + ".pyx"],
        library_dirs = library_dirs,
        libraries = libraries,
        extra_link_args = extra_link_args,
        extra_compile_args = ["-I/usr/local/include/land"]))

setup(
  name = "land",
  packages = ["land"],
  package_dir = {'land': 'pyrex'},
  ext_modules = ext_modules,
  cmdclass = {'build_ext': build_ext}
)

