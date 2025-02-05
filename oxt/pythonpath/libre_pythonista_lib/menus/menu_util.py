from __future__ import annotations
from typing import Dict, TYPE_CHECKING
import threading
from urllib.parse import parse_qs, urlparse

from com.sun.star.frame import XDispatch
from com.sun.star.util import URL

from ooodev.loader import Lo


if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


def get_url_from_command(cmd: str) -> URL:
    if cmd.startswith(".uno:"):
        cmd = cmd.replace(".uno:", "", 1)
    url = URL()
    url.Complete = cmd
    url.Main = cmd.split("?")[0]
    if "#" in cmd:
        url.Mark = cmd.split("#")[1]

    if "?" in cmd:
        if url.Mark:
            url.Arguments = cmd.split("?")[1].split("#")[0]
        else:
            url.Arguments = cmd.split("?")[1]
    if ":" in cmd:
        name = cmd.split(":")[1].split("?")[0]
        url.Protocol = name
        if "/" in name:
            url.Name = name.split("/")[-1]
        else:
            url.Name = name
    else:
        url.Name = cmd.split("?")[0]
        url.Protocol = url.Name

    return url


def dispatch_cs_cmd(cmd: str, in_thread: bool, url: URL, log: OxtLogger) -> None:
    try:
        service_name = "___lo_identifier___.ProtocolHandler.CalcSheetDispatch"
        helper = Lo.create_instance_mcf(XDispatch, service_name, args=(Lo.desktop.get_active_frame(),), raise_err=True)

        # url = get_url_from_command(cmd)
        if log.is_debug:
            log.debug("URL: %s", str(url))
        if in_thread:

            def worker(callback, helper: XDispatch, url: URL, cmd: str, props: tuple) -> None:  # noqa: ANN001
                helper.dispatch(url, props)
                callback(cmd)

            def callback(cmd: str) -> None:  # noqa: ANN401
                nonlocal log
                # runs after the threaded dispatch is finished
                log.debug("Finished Dispatched in thread: %s", cmd)

            log.debug("Dispatching in thread: %s", cmd)

            t = threading.Thread(target=worker, args=(callback, helper, url, cmd, ()), daemon=True)
            t.start()
            return
        else:
            helper.dispatch(url, ())
    except Exception:
        log.exception("dispatch_cell_cmd() Error")
    finally:
        return


def convert_query_to_dict(query: str) -> Dict[str, str]:
    if not query:
        return {}
    query_dict = parse_qs(query)
    return {k: v[0] for k, v in query_dict.items()}


def get_query_params(url_str: str) -> Dict[str, str]:
    # Parse the URL and extract the query part
    query = urlparse(url_str).query
    # Parse the query string into a dictionary
    return convert_query_to_dict(query)
