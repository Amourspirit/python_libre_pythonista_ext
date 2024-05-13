#!/bin/sh

# This script is can be run on the command line by calling reload in the contanier.
# This script reloads the menu of the container.
echo "Reloading..."
if pgrep tint2 > /dev/null; then
    pkill -SIGKILL tint2
fi
nohup bash /defaults/autostart >> /var/log/autostart.log 2>&1
echo "Reloaded!"