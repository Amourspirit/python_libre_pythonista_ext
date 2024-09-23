<p align="center"><img src="https://github.com/user-attachments/assets/4535b1a5-7a18-4a76-b4ba-61f688455bc0" alt="logo"></p>

# LibrePythonista

[![License](https://img.shields.io/badge/License-Apache2-blue.svg)](https://opensource.org/license/apache-2-0)


LibrePythonista is an extension for LibreOffice Calc. The extension allows Interactive Python code to be run directly in a spreadsheet.

LibrePythonista is currently in beta and is subject to change based on feedback. 

LibrePythonista is free and open source software so there are no fees to start using it.

LibrePythonista bring the power of [Pandas](https://pandas.pydata.org/pandas-docs/stable/index.html), [Matplotlib](https://matplotlib.org/stable/) and much more to LibreOffice Calc.

All  python code is executes on your local computer. This can alleviate many concerns around data privacy as your data

Using LibrePythonista is it possible to create Data frame's, Series, custom Graphs an much more directly in a spreadsheet.

LibrePythonista is built using [OOO Development Tools](https://python-ooo-dev-tools.readthedocs.io/en/latest/index.html) which removes many barriers when working with the LibreOffice API.

## What is LibrePythonista?

LibrePythonista brings the power of Python analytics into LibreOffice Calc. Use it to process data in Calc with Python code. You type Python directly into a cell via the code edit window, the Python calculations runs locally, and your results are displayed in the sheet.

![500](https://github.com/user-attachments/assets/0493c94f-4cbf-4262-bc2f-f28ed4082906)

LibrePythonista comes with a core set of Python libraries. Use Python libraries to simplify your data analysis, find patterns and hidden insights, and visualize your data with plots.

## Watch the Introduction Video

<a href="https://youtu.be/AQLuSNHhUY4?si=VMTHh-0UNGFCLnQd" target="_blank">
 <img src="https://i.ytimg.com/vi/AQLuSNHhUY4/hq720.jpg" alt="Watch the Introduction Video" width="600" />
</a>

## Start using Python

To begin using LibrePythonista, select a cell and on the **LibrePy** menu, **Insert Python**. This tells Calc that you want to write a Python formula in the selected cell.

![menu_001](https://github.com/user-attachments/assets/4b55f17d-daf1-4cf0-a9a7-ecae8bcfd0ef)


Alternatively insert using shortcut `Shift+Ctl+Alt+L` or by clicking on the toolbar button.

![toolbar_py_c](https://github.com/user-attachments/assets/7db6b9e1-617a-4ed7-9f42-af32d3c4f115)


LibrePythonista uses the custom Python function `lp()` to interface between Calc and Python. The `lp()` function accepts Calc objects like ranges, named ranges, and data ranges.
You can also directly type references into a Python cell with the `lp()` function. For example, to reference cell **A1** use `lp("A1")` and for the range **B1:C5** use `lp("B1:C5")`. For a named range with headers named **MyRange**, use `lp("MyRange", headers=True)`.

If the range or named range has empty rows at the end of the range then `collapse=True` can be used. The `collapse` parameter instructs the Data frame to exclude empty rows at the end of the named range. This way when new data is added to the end of the range the Data frame will automatically recalculate to include the new rows.

Example named
`df = lp("A2:D81", headers=True, collapse=True)`


The following image shows a Python in Calc calculation adding the values of cell **A1** and **B1**, with the Python result returned in cell **C1**.

![image](https://github.com/user-attachments/assets/2bd490e0-6f4b-4205-a71d-9d644212695b)

## Code Editing

When a cell contains Python code It can be edit by clicking the control and choosing Edit Code.

![image](https://github.com/user-attachments/assets/f9d50085-d496-4f62-852f-cf98d514b5e8)

Or Python cells and charts can right click and choose `Pythonista --> Edit Code`
![image](https://github.com/user-attachments/assets/1b129b80-1558-42fe-b937-e4810f5be513)

Image for the code editor for the example above.
![tri_code](https://github.com/user-attachments/assets/a52c20f9-6536-437a-8ebd-8f997921b83f)


## Other Resources

- [LibrePythonista Channel](https://www.youtube.com/@LibrePythonista)