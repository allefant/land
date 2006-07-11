# vi: syntax=python
import glob, os

# We put all generated files into this directory, but scons can't create it itself
try: os.mkdir("scons")
except OSError: pass

# Cross compile using mingw
crosscompile = ARGUMENTS.get("crosscompile", "")

debug = ARGUMENTS.get("debug", "")
profile = ARGUMENTS.get("profile", "")

sfiles = glob.glob("src/*.c")
sfiles += glob.glob("src/*/*.c")

# Environment to generate headers.
headerenv = Environment(ENV = os.environ)
headerenv.SConsignFile("scons/signatures")
headerenv.BuildDir("inc", "src", duplicate = False)

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
        "inc/" + c[4:-2] + ".inc",
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

# Environment to generate includes.
includeenv = Environment()
includeenv.SConsignFile("scons/signatures")
includeenv.BuildDir("include/land", "src", duplicate = False)
protoenv.TargetSignatures("content")

def make_include(env, target, source):
    h = file(source[0].path).readlines()
    pro = file(source[1].path).readlines()
    inc = file(target[0].path, "w").writelines(h[:-4] + pro + ["\n"] + h[-1:])

for c in sfiles:
    pro = "pro/" + c[4:-2] + ".pro"
    h = "inc/" + c[4:-2] + ".inc"
    inc = "include/land/" + c[4:-2] + ".h"
    p = includeenv.Command(
        inc,
        [h, pro],
        make_include)

includeenv.Command("include/land.h", [],
    "echo '#include \"land/land.h\"' > include/land.h")

# Main environment.
env = Environment()

if crosscompile:
    env["PLATFORM"] = "win32"

# We use C99, so MSVC probably won't do in any case.
if env["PLATFORM"] == "win32":
    Tool("mingw")(env)

print "platform", env["PLATFORM"]
print crosscompile and "cross" or "native", \
    debug and "debug" or profile and "profile" or "release", "build"

env.SConsignFile("scons/signatures")

env.Append(CCFLAGS = "-W -Wall")
env.Append(CCFLAGS = "-Wmissing-prototypes -Wstrict-prototypes")
env.Append(CCFLAGS = "-Wshadow")
env.Append(CCFLAGS = "-Wpointer-arith -Wcast-align")
env.Append(CCFLAGS = "-Wwrite-strings -Wsign-compare")
env.Append(CCFLAGS = "-Wmissing-noreturn -Wredundant-decls")
env.Append(CCFLAGS = "-Wpacked")
env.Append(CCFLAGS = "-Wdisabled-optimization")
#env.Append(CCFLAGS = "-Wunreachable-code")
env.Append(CCFLAGS = "-Wmissing-declarations")
env.Append(CCFLAGS = "-Wno-unused-parameter")

if debug:
    env.Append(CCFLAGS = "-O2 -g -DLAND_MEMLOG")
    BUILDDIR = "scons/build/%s/debug" % (env["PLATFORM"])
    LIBNAME = "lib/%s/landd" % (env["PLATFORM"])
elif profile:
    env.Append(CCFLAGS = "-g -pg -fprofile-arcs")
    env.Append(LINKFLAGS = "-pg")
    BUILDDIR = "scons/build/%s/profile" % (env["PLATFORM"])
    LIBNAME = "lib/%s/landp" % (env["PLATFORM"])
else:
    env.Append(CCFLAGS = "-O3")
    BUILDDIR = "scons/build/%s/release" % (env["PLATFORM"])
    LIBNAME = "lib/%s/land" % (env["PLATFORM"])

SHAREDLIBNAME = LIBNAME
STATICLIBNAME = LIBNAME + "_s"

env.Append(CPPPATH = ["include/land"])

if crosscompile:
    env["CC"] = "i586-mingw32msvc-gcc"
    env["LINK"] = "i586-mingw32msvc-gcc"
    env["AR"] = "i586-mingw32msvc-ar"
    env["RANLIB"] = "i586-mingw32msvc-ranlib"
    env['SHLIBSUFFIX'] = ".dll"
    env['SHLIBPREFIX'] = ""

if env["PLATFORM"] == "win32":
    env.Append(CCFLAGS = ["-DALLEGRO_STATICLINK"])

    env.Append(CPPPATH = ["dependencies/mingw-include"])
    env.Append(LIBPATH = ["dependencies/mingw-lib"])
    env.Append(LIBS = ["aldmb", "dumb", "fudgefont", "ldpng",
        "jpgal", "alleg_s", "freetype"])

    if debug or profile: env.Append(LIBS = ["agld_s"])
    else: env.Append(LIBS = ["agl_s"])

    env.Append(LIBS = ["opengl32", "glu32", "png", "z"])

    env.Append(LIBS = ["kernel32", "user32", "gdi32", "comdlg32",
        "ole32", "dinput", "ddraw", "dxguid", "winmm",
        "dsound"])

env.BuildDir(BUILDDIR, "src", duplicate = False)

sharedlib = env.SharedLibrary(SHAREDLIBNAME,
    [BUILDDIR + "/" + x[4:] for x in sfiles])

staticlib = env.StaticLibrary(STATICLIBNAME,
    [BUILDDIR + "/" + x[4:] for x in sfiles])

basenames = [x[4:-2] for x in sfiles]

LIBDIR = '/usr/local/lib'
INCDIR = '/usr/local/include'

# Install locations for headers and prototypes.
INCDIRS = []
INCDICT = {}
for f in basenames:
    dir = INCDIR + "/land/" + os.path.dirname(f)
    if not dir in INCDIRS:
        INCDIRS.append(dir)
        INCDICT[dir] = []
    INCDICT[dir].append("include/land/" + f + ".h")

INSTALL_HEADERS = []
for incdir in INCDIRS:
    env.Install(incdir, INCDICT[incdir])
    INSTALL_HEADERS.append(incdir)
INSTALL_HEADERS.append(env.Install(INCDIR, ["include/land.h"]))

env.Install(LIBDIR, [sharedlib, staticlib])

env.Alias('install', ["inc", "pro", "include", LIBDIR, INSTALL_HEADERS])

env.Default(["inc", "pro", "include", sharedlib, staticlib])
