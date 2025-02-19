from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING
import os
import sys
import importlib.util
import subprocess
import sys
from pathlib import Path
import shutil
import stat
import tempfile
import logging
import pytest


from ooodev.utils import paths as mPaths  # noqa: N812
from ooodev.loader import Lo
from ooodev.conn import connectors
from ooodev.conn import cache as mCache  # noqa: N812
from ooodev.loader.inst import Options as LoOptions
import contextlib

from tests.files.calc import __test__path__ as calc_fixture_path


@pytest.fixture(scope="session")
def import_available() -> Any:  # noqa: ANN401
    def is_available(module_name: str) -> bool:
        spec = importlib.util.find_spec(module_name)
        return spec is not None

    return is_available


def remove_readonly(func, path, exc_info) -> None:  # noqa: ANN001
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


@pytest.fixture(scope="session")
def tmp_path_session():  # noqa: ANN201
    result = Path(tempfile.mkdtemp())  # type: ignore
    yield result
    if os.path.exists(result):
        if sys.version_info >= (3, 12):
            shutil.rmtree(result, onexc=remove_readonly)
        else:
            shutil.rmtree(result, onerror=remove_readonly)


@pytest.fixture(scope="session")
def root_dir():  # noqa: ANN201
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def build_code(root_dir) -> bool:  # noqa: ANN001
    # run make.py in a subprocess
    make_py = root_dir / "make.py"
    assert make_py.exists()
    _ = subprocess.run(f"uv run {make_py} build --no-dist -i", shell=True, check=True, cwd=str(root_dir))
    return True


@pytest.fixture(scope="session")
def build_setup(root_dir, build_code) -> bool:  # noqa: ANN001
    build_path = str(root_dir / "build")
    if build_path not in sys.path:
        sys.path.append(build_path)
    pythonpath = str(root_dir / "build" / "pythonpath")
    if pythonpath not in sys.path:
        sys.path.append(pythonpath)
    return True


@pytest.fixture(scope="session")
def py_src_uri(build_setup) -> Any:  # noqa: ANN401
    from ooodev.utils import gen_util

    if TYPE_CHECKING:
        from ooodev.calc import CalcCell
        from oxt.___lo_pip___.basic_config import BasicConfig
    else:
        from libre_pythonista.basic_config import BasicConfig
    cfg = BasicConfig()

    def wrapper(cell: CalcCell) -> str:
        nonlocal cfg, gen_util
        runtime_uid = cell.calc_sheet.calc_doc.runtime_uid
        code_prop_name = cfg.cell_cp_codename
        if not cell.has_custom_property(code_prop_name):
            value = gen_util.Util.generate_random_string(10)
            cell.set_custom_property(code_prop_name, value)

        code_id = cell.get_custom_property(code_prop_name)
        root_uri = f"vnd.sun.star.tdoc:/{runtime_uid}/{cfg.lp_code_dir}"
        uri = f"{root_uri}/{cell.calc_sheet.unique_id}/{code_id}.py"
        return uri

    return wrapper


# region Soffice


@pytest.fixture(scope="session")
def soffice_path():  # noqa: ANN201
    return mPaths.get_soffice_path()


def _get_loader_pipe_default(
    headless: bool,
    soffice: str,
    working_dir: Any,  # noqa: ANN401
    env_vars: Optional[Dict[str, str]] = None,  # noqa: ANN401
) -> Any:  # noqa: ANN401
    dynamic = False
    verbose = False
    visible = False
    return Lo.load_office(
        connector=connectors.ConnectPipe(headless=headless, soffice=soffice, env_vars=env_vars, invisible=not visible),
        cache_obj=mCache.Cache(working_dir=working_dir, profile_path="", no_shared_ext=True),
        opt=LoOptions(verbose=verbose, dynamic=dynamic, log_level=logging.DEBUG),
    )


@pytest.fixture(scope="session")
def soffice_env():  # noqa: ANN201
    # for snap testing the PYTHONPATH must be set to the virtual environment
    return {}


@pytest.fixture(scope="session")
def run_headless():  # noqa: ANN201
    # windows/powershell
    #   $env:NO_HEADLESS='1'; pytest; Remove-Item Env:\NO_HEADLESS
    # linux
    #  NO_HEADLESS="1" pytest
    return os.environ.get("ODEV_TEST_HEADLESS", "1") == "1"


@pytest.fixture(scope="session")
def loader(build_setup, tmp_path_session, run_headless, soffice_path, soffice_env):  # noqa: ANN001, ANN201
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
    with contextlib.suppress(Exception):
        Lo.close_office()


# endregion soffice


@pytest.fixture(scope="session")
def copy_fix_calc(tmp_path_session):  # noqa: ANN001, ANN201
    def copy_res(fnm):  # noqa: ANN202
        src = Path(calc_fixture_path, fnm)
        dst = Path(tmp_path_session, fnm)
        shutil.copy2(src=src, dst=dst)
        return dst

    return copy_res
