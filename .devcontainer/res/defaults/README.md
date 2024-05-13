# LibreOffice Defaults

The `registrymodifications.xcu` file in this folder will be copied to the container during the build process.
The file contains defaults such as setting the macro security level to low.
The low security macro setting is only effects LibreOffice when it is run in the container.
It does not effect the host system or any documents or macros created using this container.