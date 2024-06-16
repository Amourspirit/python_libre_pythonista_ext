def test_py(*args):
    """
    Allows to launch Apso from user interface (menu item, toolbar...).
    """
    ctx = XSCRIPTCONTEXT.getComponentContext()
    # ctx.ServiceManager.createInstance("apso.python.script.organizer.impl")
    print("test_py")


g_exportedScripts = (test_py,)
