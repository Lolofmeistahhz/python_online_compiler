import sys
def restricted_open(filename: str, mode: str = "w", **kw):
    raise PermissionError("Cannot interact with files")

open = restricted_open
C7SNKxm9knQd3r9xyC8qDNTm65wAY8fNhDzF = __import__
def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    if globals["__name__"] != "__main__" or name in ['random', 'math', 'datetime', 'sqllite', 'tkinter']:
        return C7SNKxm9knQd3r9xyC8qDNTm65wAY8fNhDzF(name, globals, locals, fromlist, level)
    else:
        raise ImportError("Importing this module is not allowed")

sys.modules["builtins"].__import__ = restricted_import
_mn = locals
_dt = globals
def restricted_locals():
    lc = _mn()
    # lc.pop('C7SNKxm9knQd3r9xyC8qDNTm65wAY8fNhDzF')
    return lc
def restricted_globals():
    data = _dt()
    data = dict(data)
    data.pop('C7SNKxm9knQd3r9xyC8qDNTm65wAY8fNhDzF')
    print(data)
    return data

locals = restricted_locals
globals = {}
t = 6
print(t)