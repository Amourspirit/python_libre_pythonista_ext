# ------------------------------------------------------------------------------
# LibreOffice Extensions - bundle install (for all users) just by unzipping!!!
# https://wiki.documentfoundation.org/Documentation/HowTo/install_extension
# ------------------------------------------------------------------------------
MY_EXTENSIONS_TO_INSTALL_DIR="$CONFIG_DIR/.tmp/res/ext"
LO_EXTENSION_DIR=/usr/lib/libreoffice/share/extensions
if [ -x "${LO_EXTENSION_DIR}/" ]; then
    for EXT_FILE in "${MY_EXTENSIONS_TO_INSTALL_DIR}/"*.oxt ; do
    if [ -f "${EXT_FILE}" ]; then
        LO_EXTENSION=$(basename --suffix=.oxt ${EXT_FILE})
        if [ -e "${LO_EXTENSION_DIR}/${LO_EXTENSION}" ]; then
        echo "  Replacing ${LO_EXTENSION} extension"
        rm -rf "${LO_EXTENSION_DIR}/${LO_EXTENSION}"
        else
        echo "  Adding ${LO_EXTENSION} extension"
        fi
        unzip -q -d "${LO_EXTENSION_DIR}/${LO_EXTENSION}" \
                    "${MY_EXTENSIONS_TO_INSTALL_DIR}/${LO_EXTENSION}.oxt"
    else
        [ "$DEBUG" ] && echo "DEBUG: no .oxt files to install"
    fi
    done
else
    echo "WARNING: could not find LibreOffice install..."
fi