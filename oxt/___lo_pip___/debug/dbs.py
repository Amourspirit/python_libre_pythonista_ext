import importlib
import debugpy

debugpy.listen(8550)
debugpy.wait_for_client()  # blocks execution until client is attached
print("Debug Proceeding ...")

from macro import ooodev_ex as my_macro


def mod():
    return my_macro


def rl():
    importlib.reload(my_macro)


# make sure this is not run as macro in LibreOffice
g_exportedScripts = ()
