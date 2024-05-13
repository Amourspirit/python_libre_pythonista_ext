from __future__ import annotations
from dataclasses import dataclass


@dataclass
class BuildArgs:
    clean: bool = True
    """Whether to clean the build folder before building."""
    oxt_src: str = "oxt"
    """The oxt source folder."""
    process_tokens: bool = True
    """Whether to process tokens in the oxt source files."""
    process_py_packages: bool = True
    """Whether to copy python packages into pythonpath folder."""
    make_dist: bool = True
    """Whether to make the dist zip(oxt) file in the dist folder."""
    pre_install_pure_packages: bool = True
    """Whether to pre-install pure packages."""
