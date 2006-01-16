# vi: syntax=python
import glob, os

sfiles = glob.glob("src/*.c")
sfiles += glob.glob("src/*/*.c")

# Environment to generate headers.
headerenv = Environment()
headerenv.SConsignFile("scons/signatures")
headerenv.BuildDir("h", "src", duplicate = False)

# This means, if the same h is created, it is recognized as unmodified
headerenv.TargetSignatures("content")

for c in sfiles:
    dir = c[4:c.rfind("/")]
    if dir:
        d = "-d " + dir + " "
    else:
        d = ""
    headerenv.Command(
        "h/" + c[4:-2] + ".h",
        c,
        "splitheader -i $SOURCE -o $TARGET " + d + "-p LAND_LAND_")

# Environment to generate prototypes with cproto.
protoenv = Environment()
protoenv.SConsignFile("scons/signatures")
protoenv.BuildDir("pro", "src", duplicate = False)

# This means, if the same pro is created, it is recognized as unmodified
protoenv.TargetSignatures("content")

for c in sfiles:
    pro = "pro/" + c[4:-2] + ".pro"
    p = protoenv.Command(
        pro,
        c,
        "cproto -e -v -D _CPROTO_ -Ih $SOURCE > $TARGET")

# Main environment.
env = Environment()

env.SConsignFile("scons/signatures")

env.Append(CCFLAGS = "-W -Wall")
env.Append(CCFLAGS = "-Wmissing-prototypes -Wstrict-prototypes")
env.Append(CCFLAGS = "-Wshadow")
env.Append(CCFLAGS = "-Wpointer-arith -Wcast-align")
env.Append(CCFLAGS = "-Wwrite-strings -Wsign-compare")
env.Append(CCFLAGS = "-Wmissing-noreturn -Wredundant-decls")
env.Append(CCFLAGS = "-Wpacked")
env.Append(CCFLAGS = "-Wdisabled-optimization")
env.Append(CCFLAGS = "-Wunreachable-code")
env.Append(CCFLAGS = "-Wmissing-declarations")
env.Append(CCFLAGS = "-Wno-unused-parameter")

if ARGUMENTS.get("debug", 0):
    env.Append(CCFLAGS = "-g")
    BUILDDIR = "build/debug"
    LIBNAME = "landd"
else:
    BUILDDIR = "build/release"
    LIBNAME = "land"

env.BuildDir(BUILDDIR, "src", duplicate = False)
lib = env.SharedLibrary(LIBNAME,
    [BUILDDIR + "/" + x[4:] for x in sfiles],
    CPPPATH = ["pro", "h"])

basenames = [x[4:-2] for x in sfiles]
hfiles = ["h/" + x + ".h" for x in basenames]
profiles = ["pro/" + x + ".pro" for x in basenames]
headers = hfiles + profiles

LIBDIR = '/usr/local/lib'
INCDIR = '/usr/local/include'

# Install locations for headers and prototypes.
INCDIRS = []
INCDICT = {}
for f in headers:
    dir = os.path.dirname(f)
    pos = dir.find("/")
    if pos < 0:
        dir = ""
    else:
        dir = dir[pos + 1:]
    if not dir in INCDIRS:
        INCDIRS.append(dir)
        INCDICT[dir] = []
    INCDICT[dir].append(f)

INSTALL_HEADERS = []
for incdir in INCDIRS:
    instdir = INCDIR + "/land/" + incdir
    env.Install(instdir, INCDICT[incdir])
    INSTALL_HEADERS.append(instdir)

env.Install(LIBDIR, lib)

env.Alias('install', ["h", "pro", LIBDIR, INSTALL_HEADERS])
env.Default(["h", "pro", lib])
