#!/usr/bin/env python3
from __future__ import annotations

import contextlib

# load variables before other imports
# this prevents other imports from being loaded into the console such as
# code, readline, psutils, etc.
variables = globals().copy()
variables.update(locals())
from typing import cast, Any, TYPE_CHECKING
import subprocess
import code
import rlcompleter
import readline
from os import getenv

try:
    from ooo_dev_cli_hlp.cli.interactive_hlp import interactive_hlp
except ImportError:
    interactive_hlp = None

try:
    from ooodev.loader import Lo
except ImportError:
    print("ooodev is not installed. Please install it with 'poetry add --group=dev ooodev'")
    if TYPE_CHECKING:
        # satisfy type checkers
        Lo = cast(Any, None)
    SystemExit(1)

from ooodev.conn.connectors import ConnectSocket
from ooodev.utils.inst.lo.options import Options


def check_if_process_running(process_name: str) -> bool:
    """
    Check if there is any running process that contains the given name process_name.
    """
    result = False
    with contextlib.suppress(Exception):
        cmd = f"ps -ef | grep '{process_name}' | grep -v grep | awk '{{print $2}}'"
        ps_command = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        pid_str = ps_command.stdout.read()  # type: ignore
        ret_code = ps_command.wait()
        assert ret_code == 0, "ps command returned %d" % ret_code
        with contextlib.suppress(Exception):
            result = int(pid_str) > 0
    return result


lo_port = int(getenv("LO_CONN_PORT", 2002))

if check_if_process_running("soffice.bin"):
    _ = Lo.load_office(
        connector=ConnectSocket(
            host="localhost", port=lo_port, start_office=False, options=Options(verbose=True, dynamic=True)
        )
    )
else:
    _ = Lo.load_office(
        connector=ConnectSocket(
            host="localhost",
            port=lo_port,
            start_office=True,
            invisible=False,
            headless=False,
            options=Options(verbose=True, dynamic=True),
        )
    )
variables["XSCRIPTCONTEXT"] = Lo.XSCRIPTCONTEXT  # type: ignore
if interactive_hlp is not None:
    variables["odh"] = interactive_hlp

# https://stackoverflow.com/questions/50917938/enabling-console-features-with-code-interact
readline.set_completer(rlcompleter.Completer(variables).complete)
readline.parse_and_bind("tab: complete")


shell = code.InteractiveConsole(variables)
banner = """Entering LibreOffice Python Console.

XSCRIPTCONTEXT is available as XSCRIPTCONTEXT.

To leave the console, press Ctrl+Z or type exit().

Tab Completion is available for objects.
For example: XSCRIPTCONTEXT. + TAB TAB will show all available methods.

Try: X + TAB
"""
if interactive_hlp is not None:
    banner += """
OooDev CLI Help is available as odh() function.
Example: odh("-s Write.append")
run odh('-h') for more options.
"""
shell.interact(banner=banner)
