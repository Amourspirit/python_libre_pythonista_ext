#!/bin/sh
# GitHub Copilot: The given code is a shell script that uses the `timeout` command to run the `soffice`
# command with a time limit. The `timeout` command is set to wait no more than 25 seconds for the `soffice`
# command to complete. If the `soffice` command does not complete within 25 seconds, it will be terminated.
#The `--kill-after` option is set to 40 seconds, which means that if the `soffice` command does not
# terminate after receiving a signal to terminate, it will be killed after an additional 40 seconds.

# This script in intended to be used after operation that require a start for LibreOffice such as installing
# extensions that need a restart.

timeout --kill-after=40 25s soffice --headless &
