# vi: syntax=python
import glob, os

# We put all generated files into this directory, but scons can't create it itself
try: os.mkdir("scons")
except OSError: pass

# Cross compile using mingw
crosscompile = ARGUMENTS.get("crosscompile", "")

debug = ARGUMENTS.get("debug", "")
profile = ARGUMENTS.get("profile", "")
optimization = ARGUMENTS.get("optimization", "")

static = ARGUMENTS.get("static", "")

pyfiles = glob.glob("src/*.py")
pyfiles += glob.glob("src/*/*.py")

# Environment to generate includes.
includeenv = Environment()
includeenv.SConsignFile("scons/signatures")
includeenv.BuildDir("include/land", "src", duplicate = False)
# This means, if the same .c or .h is created, then it should be treated as
# unmodified (does this really work?)
includeenv.TargetSignatures("content")

includeenv.BuildDir("c", "src", duplicate = False)
includeenv.BuildDir("docstrings", "src", duplicate = False)

if includeenv["PLATFORM"] == "win32":
    pyfiles = [x.replace("\\", "/") for x in pyfiles]

for py in pyfiles:
    h = "include/land/" + py[4:-3] + ".h"
    c = "c/" + py[4:-3] + ".c"
    doc = "docstrings/" + py[4:-3] + ".txt"
    name = py[4:-3]
    includeenv.Command([c, h, doc], py, "scramble.py -i %s -c %s -h %s -d %s -n %s -p _LAND_HEADER" % (py, c, h, doc, name))

includeenv.Command("include/land.h", [],
    "echo '#include \"land/land.h\"' > include/land.h")

# Main environment.
env = Environment()
env.TargetSignatures("content")

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
env.Append(CCFLAGS = "--std=gnu99")

if debug:
    if optimization != "0":
        env.Append(CCFLAGS = "-O2")
    env.Append(CCFLAGS = "-g -DLAND_MEMLOG")
    BUILDDIR = "scons/build/%s/debug" % (env["PLATFORM"])
    LIBNAME = "lib/%s/landd" % (env["PLATFORM"])
    env.ParseConfig("allegro-config --cflags debug")
elif profile:
    env.Append(CCFLAGS = "-g -pg -fprofile-arcs")
    env.Append(LINKFLAGS = "-pg")
    BUILDDIR = "scons/build/%s/profile" % (env["PLATFORM"])
    LIBNAME = "lib/%s/landp" % (env["PLATFORM"])
    env.ParseConfig("allegro-config --cflags profile")
else:
    if optimization != "0":
        env.Append(CCFLAGS = "-O3")
    BUILDDIR = "scons/build/%s/release" % (env["PLATFORM"])
    LIBNAME = "lib/%s/land" % (env["PLATFORM"])
    env.ParseConfig("allegro-config --cflags release")

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
    env.Append(CCFLAGS = ["-DWINDOWS"])

    env.Append(CPPPATH = ["dependencies/mingw-include"])
    env.Append(LIBPATH = ["dependencies/mingw-lib"])
    env.Append(LIBS = ["aldmb", "dumb", "fudgefont", "ldpng",
        "jpgal", "alleg_s", "freetype"])

    if debug or profile: env.Append(LIBS = ["agld_s"])
    else: env.Append(LIBS = ["agl_s"])

    env.Append(LIBS = ["opengl32", "glu32", "png", "z"])

    env.Append(LIBS = ["kernel32", "user32", "gdi32", "comdlg32",
        "ole32", "dinput", "ddraw", "dxguid", "winmm",
        "dsound", "ws2_32"])

    duplicate = True
else:
    duplicate = False

env.BuildDir(BUILDDIR , "c", duplicate = duplicate)

sources = [BUILDDIR + "/" + x[4:-3] + ".c" for x in pyfiles]

sharedlib = env.SharedLibrary(SHAREDLIBNAME, sources)
if static:
    staticlib = env.StaticLibrary(STATICLIBNAME, sources)

basenames = [x[4:-3] for x in pyfiles]

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

env.Alias('install', ["include", LIBDIR, INSTALL_HEADERS])

if static:
    env.Default(["include", staticlib])
    env.Install(LIBDIR, [staticlib])
else:
    env.Default(["include", sharedlib])
    env.Install(LIBDIR, [sharedlib])
