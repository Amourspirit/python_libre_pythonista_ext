#!/bin/sh
# this script is call by running unlock on the command line in the contanier.
# This script will kill any running instances of Libreoffice and remove the lock file.

# kill soffice if it's running
pkill -SIGKILL soffice 2>/dev/null || true

# remove the lock file if it exists.
FILE_LOCK=$CONFIG_DIR/.config/libreoffice/4/.lock
if [ -f "$FILE_LOCK" ]; then
    rm "$FILE_LOCK"
fi
