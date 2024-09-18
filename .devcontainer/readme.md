# Development Container

There are two configuration files in the .devcontainer folder. The `lo_only/.devcontainer.json` file is the main configuration file for the development container.

## lo_only

The `lo_only` does not include the SDK for LibreOffice. This allows the extension to be installed and run without issues.

When building the extension, use `python -m make build -i` to build the extension. This will build the extension without the SDK.

## lo_sdk

The `lo_sdk` also installs the SDK for LibreOffice. This is necessary to build the `oxt/sources` `idl` files.

When building the extension with the SDK, use `python -m make build`. This will build the extension with the SDK.

## Why two configurations?

The SDK for LibreOffice must be a exact match to the Installed LibreOffice version in the container.
This is not guaranteed to be the case for all containers. Therefore, the `lo_only` configuration is the default configuration and does not include the SDK.

This way when the `*.idl` file are neede to be build into `*.rdb` file the `lo_sdk` configuration can be used.
To install and run the extension the `lo_only` configuration can be used.