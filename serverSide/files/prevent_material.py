def restricted_open(filename: str, mode: str = "w", **kw):
    raise PermissionError("Cannot interact with files")

open = restricted_open
C7SNKxm9knQd3r9xyC8qDNTm65wAY8fNhDzF = __import__
def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    if globals["__name__"] != "__main__" or name in granted_modules:
        return C7SNKxm9knQd3r9xyC8qDNTm65wAY8fNhDzF(name, globals, locals, fromlist, level)
    else:
        raise ImportError("Importing this module is not allowed")

sys.modules["builtins"].__import__ = restricted_import

def restricted_locals():
    return {}
def restricted_globals():
    return {}
locals = restricted_locals
globals = restricted_globals