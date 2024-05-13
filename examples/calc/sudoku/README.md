# LibreOffice Calc Sudoku

This is an example of Sudoku in **Calc** using [ScriptForge].

This example uses [types-scriptforge](https://pypi.org/project/types-scriptforge/) and [types-unopy](https://pypi.org/project/types-unopy/) give advantages of typing support and Intellisense (autocomplete) support inside development environment.


## Build

Build will compile the python scripts for this example into a single python script.

The `make` command must be run from this current folder.

### Compile into Document


The following command will compile script as `builder.py` and embed it into `builder.ods`
The output is written into `build/build_table/` folder in the projects root.

```sh
make build
```

## Sample Document

See sample LibreOffice Calc document, [calc-sudoku.ods](calc-sudoku.ods)

[![calc_sudoku](https://user-images.githubusercontent.com/4193389/165391098-883a7647-5fc8-47de-b028-4c2c98337abe.png)](https://user-images.githubusercontent.com/4193389/165391098-883a7647-5fc8-47de-b028-4c2c98337abe.png)

[ScriptForge]: https://gitlab.com/LibreOfficiant/scriptforge
