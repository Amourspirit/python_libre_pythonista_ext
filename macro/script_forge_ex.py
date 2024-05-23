# coding: utf-8
import scriptforge as SF
import time

# other Links
# https://wiki.documentfoundation.org/Macros/Python_Design_Guide#Output_to_Consoles


def console(*args) -> None:
    serv = SF.CreateScriptService("ScriptForge.Exception")
    serv.PythonShell({**globals(), **locals()})
    time.sleep(1)
    print("Hello World!")


def show_hello_sf(*args) -> None:
    bas = SF.CreateScriptService("Basic")
    bas.MsgBox(prompt="Hello World!", title="HI")


g_exportedScripts = (console, show_hello_sf)
