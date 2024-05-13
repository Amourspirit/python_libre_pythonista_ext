# Calc Add Range of Data Example

This example demonstrates how to add a range of data to a spreadsheet using a macro and [OOO Development Tools].

There is also an automation command line version of this example.
See [Add Range Automation](https://github.com/Amourspirit/python-ooouno-ex/tree/main/ex/auto/calc/odev_add_range_data)

## Sample Document

See [odev_add_range.ods](odev_add_range.ods).


## Build

Build will compile the python scripts for this example into a single python script.

The `make` command must be run from this current folder.

### Compile into Document


The following command will compile script as `odev_add_range.py` and embed it into `odev_add_range.ods`
The output is written into `build/add_range_data/` folder in the projects root.

```sh
make build
```

### Compile as Macro

The following command will compile script into `odev_add_range.py` and place it in the `macro` folder. After script is compiled it is available as LibreOffice Macros.

```sh
make macro
```

## Run Directly

To start LibreOffice and display a message box run the following command from this folder.

```sh
make run
```

## Related

See: [How can I compile my project if I have multiple python files?](https://github.com/Amourspirit/live-libreoffice-python/wiki/FAQ#how-can-i-compile-my-project-if-i-have-multiple-python-files)

![calc_range_macro](https://user-images.githubusercontent.com/4193389/173204999-924f12f6-59df-4bfe-8c2c-bee4cc5b9d6b.gif)

[OOO Development Tools]: https://python-ooo-dev-tools.readthedocs.io/en/latest/
