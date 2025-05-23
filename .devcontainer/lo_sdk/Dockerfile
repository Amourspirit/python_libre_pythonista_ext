ARG LO_VERSION
ARG UV_VERSION=0.5.5
ARG UVSRC=ghcr.io/astral-sh/uv:$UV_VERSION

# Lifehack
# see https://stackoverflow.com/questions/43473236/docker-build-arg-and-copy
FROM $UVSRC AS uv_full_src

FROM linuxserver/libreoffice:${LO_VERSION}

ARG CODE_PORT=2002
ARG CONFIG_DIR=/config

# Had Error: Compilation error in psutil/_psutil_linux
# See Github: https://github.com/giampaolo/psutil//issues/664
RUN apk update \
    && apk add --no-cache --update htop \
    linux-headers \
    libc-dev \
    rsync \
    g++ \
    gcc \
    python3-dev \
    git \
    py-pip \
    github-cli \
    subversion \
    make \
    openssh-client-default \
    openssh \
    zip \
    libreoffice-sdk
# https://pkgs.alpinelinux.org/package/edge/main/x86/subversion
# subversion can be used to download github repos sub folders. Great for downloading just a single folder from a repo.
# Can be run as examples.
# https://stackoverflow.com/questions/7106012/download-a-single-folder-or-directory-from-a-github-repo

# install rust
# This is baffling but for a few hours of trying to building this image I could not get poetry to install without rust.
# This was the case for both local and codespaces.
# This was on July 6th 2023.  I had to install rust to get poetry to install.
# Uncomment to install rust. Add PATH="$CONFIG_DIR/.cargo/bin:$PATH" to environment.
# RUN echo "Installing Rust into $CONFIG_DIR/.cargo/env" \
#     && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
#     && source "$CONFIG_DIR/.cargo/env" \
#     && rustup install stable \
#     && rustup default stable \
#     && rustup update \
#     && rustup component add rls rust-analysis rust-src


# RUN chsh -s /bin/bash root
# root:x:0:0:root:/root:/bin/ash

RUN sed -i "s/\/bin\/ash/\/bin\/bash/g" /etc/passwd \
    && sed -i "s/libreoffice/soffice --accept=\"socket,host=localhost,port=${CODE_PORT},tcpNoDelay=1;urp;StarOffice.ServiceManager\"/g" /defaults/autostart \
    && sed -i "s/--base/--base --accept=\"socket,host=localhost,port=${CODE_PORT},tcpNoDelay=1;urp;StarOffice.ServiceManager\"/g" /usr/lib/libreoffice/share/xdg/base.desktop \
    && sed -i "s/--calc/--calc --accept=\"socket,host=localhost,port=${CODE_PORT},tcpNoDelay=1;urp;StarOffice.ServiceManager\"/g" /usr/lib/libreoffice/share/xdg/calc.desktop \
    && sed -i "s/--draw/--draw --accept=\"socket,host=localhost,port=${CODE_PORT},tcpNoDelay=1;urp;StarOffice.ServiceManager\"/g" /usr/lib/libreoffice/share/xdg/draw.desktop \
    && sed -i "s/--impress/--impress --accept=\"socket,host=localhost,port=${CODE_PORT},tcpNoDelay=1;urp;StarOffice.ServiceManager\"/g" /usr/lib/libreoffice/share/xdg/impress.desktop \
    && sed -i "s/--math/--math --accept=\"socket,host=localhost,port=${CODE_PORT},tcpNoDelay=1;urp;StarOffice.ServiceManager\"/g" /usr/lib/libreoffice/share/xdg/math.desktop \
    && sed -i "s/--writer/--writer --accept=\"socket,host=localhost,port=${CODE_PORT},tcpNoDelay=1;urp;StarOffice.ServiceManager\"/g" /usr/lib/libreoffice/share/xdg/writer.desktop

# Codespaces mounts its own /tmp directory, so we need to create a new one
COPY ../.devcontainer/res $CONFIG_DIR/.tmp/res
COPY ../.devcontainer/root/rc.sh /etc/profile.d/10bashrc.sh
COPY ../.devcontainer/root/bashrc.sh $CONFIG_DIR/.bashrc
COPY ./.devcontainer/root/bash_custom.sh $CONFIG_DIR/.bashrc_custom


# ENV HOME=$CONFIG_DIR \
ENV RUN_ENV=${RUN_ENV} \
    LANG=C.UTF-8 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    LO_CONN_PORT=${CODE_PORT} \
    UV_LINK_MODE=copy


RUN if [ x"$LOCAL_GIT_AUTHOR_NAME" != "x" ]; then git config --global user.name "$LOCAL_GIT_AUTHOR_NAME" || true; fi \
    && if [ x"$LOCAL_GIT_AUTHOR_EMAIL" != "x" ]; then git config --global user.email $LOCAL_GIT_AUTHOR_EMAIL || true; fi

# remove /usr/lib/python3.11 EXTERNALLY-MANAGED file to allow pip to work
# https://www.makeuseof.com/fix-pip-error-externally-managed-environment-linux/
RUN MY_PY_VER=$(python -c "import sys; major, minor = sys.version_info[:2]; print(f'{major}.{minor}');" ) \
    && if [ -f "/usr/lib/python$MY_PY_VER/EXTERNALLY-MANAGED" ]; then \
    rm "/usr/lib/python$MY_PY_VER/EXTERNALLY-MANAGED"; fi

WORKDIR /workspace/libreoffice_pip_ext
COPY ../*.toml ../*.lock ../*.md ./

COPY --from=uv_full_src /uv /uvx /bin/
ENV VIRTUAL_ENV=/workspace/libreoffice_pip_ext/.venv

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project \
    && sed -i "s/include-system-site-packages = false/include-system-site-packages = true/g" /workspace/libreoffice_pip_ext/.venv/pyvenv.cfg \
    && if [ -f "$CONFIG_DIR/.tmp/res/req/requirements.txt" ]; then \
    uv pip install --requirement "$CONFIG_DIR/.tmp/res/req/requirements.txt"; fi

# Many of these environment variable are required for python and LibreOffice imports to work correctly.
# For instance without proper environment vars: from com.sun.star.frame import XComponentLoader # results in error
# many of these values can be gotten by opening APSO console in running instance of LinuxServer LibreOffice and
# import os
# os.environ
# See Also: https://uucode.com/blog/2013/01/09/solved-createinstancewithcontext-binary-urp-bridge-disposed-during-call/
# Note: not all os's need extra LibreOffice Environment Vars, I did not have to do this for Ubuntu
# Note: Path includes virtual environment path to allow for the virtual environment python to be used.
#   This is by design so that LibreOfffice will use the virtual environment python by default.
#   This is done by adding the virtual environment path to the beginning of the PATH environment variable.
#   When Poetry installs the virtual environment it will be modified to include the system site packages.
ENV PATH="/workspace/libreoffice_pip_ext/.venv/bin:/usr/lib/libreoffice/program:/usr/lib/libreoffice/sdk/bin:$PATH" \
    URE_BOOTSTRAP="file:///usr/lib/libreoffice/program/fundamentalrc" \
    # PYTHONPATH="/usr/lib/libreoffice/program/../program:$PYTHONPATH" \
    PYTHONPATH="/usr/lib/libreoffice/program:$PYTHONPATH" \
    UNO_PATH="/usr/lib/libreoffice/program" \
    LD_LIBRARY_PATH="/usr/lib/libreoffice/sdk/lib:/usr/lib/libreoffice/program:/usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/client:/usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/server:/usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64/native_threads:/usr/lib/jvm/java-1.8-openjdk/jre/lib/amd64" \
    OFFICE_HOME="/usr/lib/libreoffice" \
    OFFICE_PROGRAM_PATH="/usr/lib/libreoffice/program" \
    UNO_PATH="/usr/lib/libreoffice/program" \
    OO_SDK_NAME="libreoffice_sdk" \
    OO_SDK_HOME="/usr/lib/libreoffice/sdk" \
    OO_SDK_MAKE_HOME="/usr/bin" \
    OO_SDK_CAT_HOME="/bin" \
    OO_SDK_SED_HOME="/bin" \
    OO_SDK_ZIP_HOME="usr/bin" \
    OO_SDK_URE_BIN_DIR="/usr/lib/libreoffice/program" \
    OO_SDK_URE_LIB_DIR="/usr/lib/libreoffice/program" \
    OO_SDK_URE_JAVA_DIR="/usr/lib/libreoffice/program/classes" \
    OO_SDK_JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk" \
    OO_SDK_OUTPUT_DIR="/config" \
    OO_SDK_OUT="/config/libreoffice_sdk" \
    OO_TYPES_UNO="/usr/lib/libreoffice/program/types.rdb" \
    OO_TYPES_OFFICE="/usr/lib/libreoffice/program/types/offapi.rdb"

# Cannot persist python version into build here so, get the python version and run all the commands the use it.
RUN MY_PY_VER=$(python -c "import sys; major, minor = sys.version_info[:2]; print(f'{major}.{minor}');" ) \
    && echo "Python version: $MY_PY_VER" \
    && echo "/workspace/libreoffice_pip_ext" >> "/workspace/libreoffice_pip_ext/.venv/lib/python$MY_PY_VER/site-packages/ooo_dev_tools.pth" \
    && echo "/usr/lib/libreoffice/program" >> "/workspace/libreoffice_pip_ext/.venv/lib/python$MY_PY_VER/site-packages/libreoffice_program.pth"

WORKDIR /workspace/libreoffice_pip_ext

# EXPOSE $CODE_PORT
COPY ../.devcontainer/root/defaults /defaults
COPY ../.devcontainer/startup.sh /usr/local/bin/startup.sh

# Moved extension install to to here 
RUN chmod -R +x "$CONFIG_DIR/.tmp/res/scripts" \
    && mv "$CONFIG_DIR/.tmp/res/scripts/unlock.sh" "/usr/local/bin/unlock" \
    && chmod +x "/usr/local/bin/unlock" \
    && mv "$CONFIG_DIR/.tmp/res/scripts/lo_console.py" "/usr/local/bin/console" \
    && chmod +x "/usr/local/bin/console" \
    && chmod +x "/defaults/autostart" \
    && mkdir -p "$CONFIG_DIR/.config/libreoffice/4/user/" \
    && mv "$CONFIG_DIR/.tmp/res/defaults/registrymodifications.xcu" "$CONFIG_DIR/.config/libreoffice/4/user/registrymodifications.xcu" \
    && mkdir -p "/usr/lib/libreoffice/share/extensions" \
    && chmod +x "/usr/local/bin/startup.sh" \
    && mv "$CONFIG_DIR/.tmp/res/scripts/reload.sh" "/usr/local/bin/reload" \
    && chmod +x "/usr/local/bin/reload" \
    && mv "$CONFIG_DIR/.tmp/res/scripts/gitget.sh" "/usr/local/bin/gitget" \
    && chmod +x "/usr/local/bin/gitget"

# ENTRYPOINT ["/usr/local/bin/startup.sh"]
