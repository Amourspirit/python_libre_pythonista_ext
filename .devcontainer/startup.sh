#/bin/sh

# This file is run when the container is started.
# If you need custom initialization, add them here.

# install extensions that reside in the .devcontainer/res/ext folder
source "$CONFIG_DIR/.tmp/res/scripts/ext.sh"

# run soffice after ext are installed.
# Some extensions such as the MRI extnesion seem to need an initial run to configure and work properly.
# This call runs office in the background and then kills it after specified time.
source "$CONFIG_DIR/.tmp/res/scripts/lo_init.sh"

# remove the lock file if it exists.
# This is needed because sometimes libreoffice does not close properly and the lock file is not removed.
# Also running unlock on the command line can bu used to remove the lock file and close any hanging libreoffice processes.
FILE_LOCK=$CONFIG_DIR/.config/libreoffice/4/.lock
if [ -f "$FILE_LOCK" ]; then
    rm "$FILE_LOCK"
fi

# this next command does not work properly for some reason so it is added to devcontainer.json
# nohup bash /defaults/autostart > /var/log/autostart.log 2>&1 &

# if using github codespace then add some aliases
if [ "$CODESPACES" == "true" ]; then
    git config --local alias.co "checkout"
    git config --local alias.br "branch"
    git config --local alias.ci "commit"
    git config --local alias.s "status -s"
    git config --local alias.type "cat-file -t"
    git config --local alias.dump "cat-file -p"
fi

mkdir -p "$CONFIG_DIR/.config/gtk-3.0"
echo "file:///workspace/libreoffice_pip_ext" > "$CONFIG_DIR/.config/gtk-3.0/bookmarks"

echo "Startup Success!!!"
