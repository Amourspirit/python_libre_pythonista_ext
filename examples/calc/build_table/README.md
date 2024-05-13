# Build Table

<p align="center">
<img src="https://github.com/Amourspirit/live-libreoffice-python/assets/4193389/8f3afaf8-4ecc-4dfe-a790-8ce7a8705ab5" width="485" height="273">
</p>

Example of building different kinds of Spreadsheet Tables.

Also demonstrates create a chart.

This demo uses This demo uses [OOO Development Tools] (OooDev).

## Build

Build will compile the python scripts for this example into a single python script.

The `make` command must be run from this current folder.

### Compile into Document


The following command will compile script as `builder.py` and embed it into `builder.ods`
The output is written into `build/build_table/` folder in the projects root.

```sh
make build
```

### Compile as Macro

The following command will compile script into `builder.py` and place it in the `macro` folder. After script is compiled it is available as LibreOffice Macros.

```sh
make macro
```

## Run Directly

To start LibreOffice and build table run the following command from this folder.

```sh
make tbl
```

or

```sh
make tbl-style
```

or

```sh
make tbl-chart
```

## Related

- [OOO Development Tools - Chapter 20. Spreadsheet Displaying and Creation](https://python-ooo-dev-tools.readthedocs.io/en/latest/odev/part4/chapter20.html)
- [OOO Development Tools - Chapter 22. Styles](https://python-ooo-dev-tools.readthedocs.io/en/latest/odev/part4/chapter22.html)
- [LibreOffice Python UNO Examples - Build Table](https://github.com/Amourspirit/python-ooouno-ex/tree/main/ex/auto/calc/odev_build_table)



[OOO Development Tools]: https://python-ooo-dev-tools.readthedocs.io/en/latest/