from __future__ import annotations
from typing import Any, Dict, Optional
import os
import subprocess
import sys
from pathlib import Path
import shutil
import stat
import tempfile
import logging
import pytest


from ooodev.utils import paths as mPaths
from ooodev.loader import Lo
from ooodev.conn import connectors
from ooodev.conn import cache as mCache
from ooodev.loader.inst import Options as LoOptions


def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


@pytest.fixture(scope="session")
def tmp_path_session():
    result = Path(tempfile.mkdtemp())  # type: ignore
    yield result
    if os.path.exists(result):
        shutil.rmtree(result, onerror=remove_readonly)


@pytest.fixture(scope="session")
def root_dir():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def build_code(root_dir):
    # run make.py in a subprocess
    make_py = root_dir / "make.py"
    assert make_py.exists()
    _ = subprocess.run(f"python make.py build --no-dist", shell=True, check=True, cwd=str(root_dir))
    return True


@pytest.fixture(scope="session")
def build_setup(root_dir, build_code):
    build_path = str(root_dir / "build")
    if build_path not in sys.path:
        sys.path.append(build_path)
    pythonpath = str(root_dir / "build" / "pythonpath")
    if pythonpath not in sys.path:
        sys.path.append(pythonpath)
    return True


# region Soffice


@pytest.fixture(scope="session")
def soffice_path():
    return mPaths.get_soffice_path()


def _get_loader_pipe_default(
    headless: bool, soffice: str, working_dir: Any, env_vars: Optional[Dict[str, str]] = None
) -> Any:
    dynamic = False
    verbose = False
    visible = False
    return Lo.load_office(
        connector=connectors.ConnectPipe(headless=headless, soffice=soffice, env_vars=env_vars, invisible=not visible),
        cache_obj=mCache.Cache(working_dir=working_dir),
        opt=LoOptions(verbose=verbose, dynamic=dynamic, log_level=logging.DEBUG),
    )


@pytest.fixture(scope="session")
def soffice_env():
    # for snap testing the PYTHONPATH must be set to the virtual environment
    return {}


@pytest.fixture(scope="session")
def run_headless():
    # windows/powershell
    #   $env:NO_HEADLESS='1'; pytest; Remove-Item Env:\NO_HEADLESS
    # linux
    #  NO_HEADLESS="1" pytest
    return os.environ.get("ODEV_TEST_HEADLESS", "1") == "1"


@pytest.fixture(scope="session")
def loader(build_setup, tmp_path_session, run_headless, soffice_path, soffice_env):
    # for testing with a snap the cache_obj must be omitted.
    # This because the snap is not allowed to write to the real tmp directory.
    connect_kind = os.environ.get("ODEV_TEST_CONN_SOCKET_KIND", "default")
    loader = _get_loader_pipe_default(
        headless=run_headless, soffice=soffice_path, working_dir=tmp_path_session, env_vars=soffice_env
    )
    yield loader
    if connect_kind == "no_start":
        # only close office if it was started by the test
        return
    Lo.close_office()


# endregion soffice
