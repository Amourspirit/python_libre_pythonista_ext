from typing import Any, TYPE_CHECKING
import re
import functools
from matplotlib import pyplot as plt

from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.gen_util import Util as OooDevGenUtil
from ooodev.loader import Lo

LAST_LP_RESULT = DotDict(data=None)

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.log.log_inst import LogInst
else:
    from libre_pythonista_lib.log.log_inst import LogInst

# _ORIG_PLT_SHOW = plt.show


def _lp_plt_show_prefix_function(function: Any, pre_function: Any):
    @functools.wraps(function)
    def run(*args, **kwargs):
        pre_function(*args, **kwargs)
        # in theory the real plot.show() can be called here.
        # However, this would run the real plot.show() which may popup an window and
        # event crash LibreOffice. So, we just return None here.
        # In LibreOffice Flatpak, this seem to make no difference.
        # Because the image is saved to a file, it can be loaded in LibreOffice.
        #
        # return function(*args, **kwargs)
        return None

    return run


def _custom_plt_show(*args, **kwargs):
    # Your own code here that will be run before
    global LAST_LP_RESULT
    log = LogInst()
    log.debug("Custom Plot Method")
    s = "plt_" + OooDevGenUtil.generate_random_hex_string(12) + ".svg"
    pth = Lo.tmp_dir / s
    if log.is_debug:
        log.debug("Saving Plot to %s", pth)

    plt.savefig(str(pth), format="svg")
    try:
        # https://stackoverflow.com/questions/9622163/save-plot-to-image-file-instead-of-displaying-it
        # Is is important to call plt.close() to clear the plot after saving it.
        # This fixes the issue of the plot going for area to line still being outputted as area.
        plt.close()
        log.debug("Closed plot")
    except Exception as e:
        log.exception("Error in _custom_plt_show with plt.close: %s", e, exc_info=True)
    if log.is_debug:
        log.debug("Plot saved to %s", pth)
    dd = DotDict(data=str(pth), data_type="file", file_kind="image", file_ext="svg", details="figure")
    LAST_LP_RESULT = dd

    log.debug("_custom_plt_show Done")


plt.show = _lp_plt_show_prefix_function(plt.show, _custom_plt_show)
