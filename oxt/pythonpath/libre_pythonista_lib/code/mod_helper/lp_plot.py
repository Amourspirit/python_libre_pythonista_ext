from typing import Any, TYPE_CHECKING
import re
from pathlib import Path
import functools
from matplotlib import pyplot as plt

from ooodev.utils.helper.dot_dict import DotDict
from ooodev.utils.gen_util import Util as OooDevGenUtil
from ooodev.loader import Lo

LAST_LP_RESULT = DotDict(data=None)

if TYPE_CHECKING:
    from ...log.log_inst import LogInst
else:
    from libre_pythonista_lib.log.log_inst import LogInst


def _lp_plt_show_prefix_function(function: Any, pre_function: Any):
    @functools.wraps(function)
    def run(*args, **kwargs):
        pre_function(*args, **kwargs)
        # in theory the real plot.show() can be called here.
        # However, this would run the real plot.show() which may popup an window and
        # event crash LibreOffice. So, we just return None here.
        # I LibreOffice Flatpak, this seem to make no difference.
        # Because the image is saved to a file, it can be loaded in LibreOffice.
        #
        # return function(*args, **kwargs)
        return None

    return run


def _custom_plt_show(*args, **kwargs):
    # Your own code here that will be run before
    global LAST_LP_RESULT
    # log = LogInst()
    # log.debug("Custom Plot Method")
    s = "plt_" + OooDevGenUtil.generate_random_hex_string(12) + ".svg"
    pth = Lo.tmp_dir / s
    plt.savefig(str(pth), format="svg")
    dd = DotDict(data=str(pth), data_type="file", file_kind="image", file_ext="svg", details="figure")
    LAST_LP_RESULT = dd


plt.show = _lp_plt_show_prefix_function(plt.show, _custom_plt_show)
