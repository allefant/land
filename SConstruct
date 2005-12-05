# vi: syntax=python
import glob, os

sfiles = glob.glob("src/*.c")
sfiles += glob.glob("src/allegro/*.c")
sfiles += glob.glob("src/allegrogl/*.c")
sfiles += glob.glob("src/image/*.c")
sfiles += glob.glob("src/widget/*.c")

env = Environment()

env.SConsignFile("scons/signatures")

# First, update headers and prototypes.
if GetOption("clean"):
    env.Execute(Action("scons -c -Qf scons/headers.scons"))
    env.Execute(Action("scons -c -Qf scons/prototypes.scons"))
else:
    env.Execute(Action("scons -Qf scons/headers.scons"))
    env.Execute(Action("scons -Qf scons/prototypes.scons"))


env.BuildDir("build", "src", duplicate = False)
land = env.SharedLibrary("land",
    ["build/" + x[4:] for x in sfiles],
    CPPPATH = "pro")

basenames = [x[4:-2] for x in sfiles]
hfiles = [x + ".h" for x in basenames]
profiles = [x + ".pro" for x in basenames]
headers = hfiles + profiles

LIBDIR = '/usr/local/lib'
INCDIR = '/usr/local/include'

INCDIRS = []
INCDICT = {}
for f in headers:
    dir = os.path.dirname(f)
    if not dir in INCDIRS:
        INCDIRS.append(dir)
        INCDICT[dir] = []
    INCDICT[dir].append("pro/" + f)

INSTALL_HEADERS = []
for incdir in INCDIRS:
    instdir = INCDIR + "/land/" + incdir
    env.Install(instdir, INCDICT[incdir])
    INSTALL_HEADERS.append(instdir)

env.Install(LIBDIR, land)

env.Alias('install', [LIBDIR, INSTALL_HEADERS])

