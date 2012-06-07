import imp, os
file, pathname, description = imp.find_module("land_ctypes")

class SharedLibraryLoader:
    def __init__(self):
        self.dll = None

shader_library_loader = SharedLibraryLoader()

def load_function(x, ret, params):
    if x in ["land_memory_add", "land_memory_remove"]:
        return lambda *args: None

    if x.endswith("memlog"):
        return lambda *args: None
    
    if not shader_library_loader.dll:
        path = os.path.join(os.path.dirname(pathname), "libland-debug.so")
        shader_library_loader.dll = CDLL(path, RTLD_GLOBAL)
    try:
        f =  shader_library_loader.dll[x]
        f.restype = ret
        f.argtypes = params
        return f
    except AttributeError:
        print("No such function " + x)
        pass

    return lambda *args: None

if file:
    exec(file.read())
    file.close()

def land_use_main(user_main):
    def python_callback():
        user_main()
        return 0
    cb = CFUNCTYPE(None)(python_callback)
    land_without_main(cb)
