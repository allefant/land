#!/bin/bash
scramble -j src/*.py src/widget/*.py -o land_api.py
scramble -i land_api.py -t python/ctypes/land_ctypes.py
