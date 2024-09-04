"""Converts Matplotlib objects to other formats such exporting to SVG, PNG, etc."""

from __future__ import annotations
from pathlib import Path
import uno
from ooodev.loader import Lo

from ooodev.utils.gen_util import Util as GenUtil
from matplotlib import pyplot as plt


def fig_to_svg() -> Path:
    """Converts a Matplotlib figure to SVG format and returns the file path.

    The file is a temporary file of LibreOffice.

    Returns:
        Path: The path to the SVG file.
    """
    # https://stackoverflow.com/questions/24525111/how-can-i-get-the-output-of-a-matplotlib-plot-as-an-svg
    s = "img_" + GenUtil.generate_random_hex_string(12) + ".svg"
    tmp_file = Lo.tmp_dir / s
    fig = plt.show()
    fig.savefig(str(tmp_file), format="svg")
    return tmp_file
