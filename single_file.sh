#!/bin/bash
set -e
scramble -j src/*.py src/*/*.py -o land_tmp.py
cat > tmp.py <<HERE
out = open("land.py", "w")
for row in open("land_tmp.py"):
    if "src/yaml/external.py" in row: continue
    out.write(row)
HERE
python3 tmp.py
rm land_tmp.py
scramble -i land.py -c land.c -h land.h -N
