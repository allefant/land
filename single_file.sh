#!/bin/bash
scramble -j src/*.py src/*/*.py -o land.py
scramble -i land.py -c land.c -h land.h -N
