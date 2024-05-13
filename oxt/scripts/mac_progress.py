#!/usr/bin/env python
# This script works with oxt/___lo_pip___/install/progress_window/mac_terminal.py to display a progress indicator in the terminal.
# When mac_terminal calls start this script is called.
# When mac_terminal calls stop it is done using SIGINT. This script catches the SIGINT and then exits.
# It seems it is not possible to kill the terminal window from this script.

from __future__ import annotations
import signal
import time
import sys
import os
import subprocess

LOOP_ME = True


def signal_handler(sig, frame):
    # https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
    global LOOP_ME
    LOOP_ME = False
    # print("")
    # print("You pressed Ctrl+C!")


signal.signal(signal.SIGINT, signal_handler)

os.system("cls" if os.name == "nt" else "clear")

if len(sys.argv) > 1:
    print(sys.argv[1], flush=True, end="")


while LOOP_ME:
    print(".", flush=True, end="")
    time.sleep(1)

print("")
if len(sys.argv) > 2:
    print(sys.argv[2])
else:
    print("Done")


def _kill_parent():
    try:
        pid = os.getppid()
        # os.kill(pid, signal.SIGHUP)
        subprocess.Popen(f"kill {pid}", shell=True)
    except Exception:
        return


# _kill_parent()

sys.exit(0)
