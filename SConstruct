# vi: syntax=python
import glob, os

# We put all generated files into this directory, but scons can't create it itself
try: os.mkdir("scons")
except OSError: pass

# Cross compile using mingw
crosscompile = ARGUMENTS.get("crosscompile", "")

debug = ARGUMENTS.get("debug", "")

sfiles = glob.glob("src/*.c")
sfiles += glob.glob("src/*/*.c")

# Environment to generate headers.
headerenv = Environment(ENV = os.environ)
headerenv.SConsignFile("scons/signatures")
headerenv.BuildDir("h", "src", duplicate = False)

# This means, if the same h is created, it is recognized as unmodified
headerenv.TargetSignatures("content")

for c in sfiles:
    dir = os.path.split(c)[0]
    dir = dir[4:]
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
        "cproto.py $SOURCE > $TARGET")

# Main environment.
env = Environment()

if crosscompile:
    env["PLATFORM"] = "mingw"

# We use C99, so MSVC probably won't do in any case.
if env["PLATFORM"] == "win32":
    Tool("mingw")(env)

print "platform", env["PLATFORM"]
print crosscompile and "cross" or "native", debug and "debug" or "release", "build"

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

if debug:
    env.Append(CCFLAGS = "-g")
    BUILDDIR = "scons/build/%s/debug" % (env["PLATFORM"])
    LIBNAME = "landd"
else:
    env.Append(CCFLAGS = "-O3")
    BUILDDIR = "scons/build/%s/release" % (env["PLATFORM"])
    LIBNAME = "land"

env.Append(CPPPATH = ["pro", "h"])

if crosscompile:
    env["CC"] = "i586-mingw32msvc-gcc"
    env["AR"] = "i586-mingw32msvc-ar"

if env["PLATFORM"] == "mingw":
    env.Append(CCFLAGS = ["-DALLEGRO_STATICLINK"])

    env.Append(CPPPATH = ["dependencies/include"])
    env.Append(LIBPATH = ["dependencies/lib"])
    env.Append(LIBS = ["aldmb", "dumb", "fudgefont", "glyphkeeper-alleggl", "agl_s", "ldpng", "alleg_s", "freetype"])

    env.Append(LIBS = ["opengl32", "glu32", "png", "z"])

    env.Append(LIBS = ["kernel32", "user32", "gdi32", "comdlg32", "ole32", "dinput", "ddraw", "dxguid", "winmm",
        "dsound"])

env.BuildDir(BUILDDIR, "src", duplicate = False)

sharedlib = env.SharedLibrary(LIBNAME,
    [BUILDDIR + "/" + x[4:] for x in sfiles])

staticlib = env.StaticLibrary(LIBNAME,
    [BUILDDIR + "/" + x[4:] for x in sfiles])

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

env.Install(LIBDIR, [sharedlib, staticlib])

env.Alias('install', ["h", "pro", LIBDIR, INSTALL_HEADERS])
env.Default(["h", "pro", sharedlib, staticlib])
