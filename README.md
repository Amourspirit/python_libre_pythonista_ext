<p align="center"><img src="https://github.com/user-attachments/assets/4535b1a5-7a18-4a76-b4ba-61f688455bc0" alt="logo"></p>

# LibrePythonista

[![License](https://img.shields.io/badge/License-Apache2-blue.svg)](https://opensource.org/license/apache-2-0)


LibrePythonista is an extension for LibreOffice Calc. The extension allows Interactive Python code to be run directly in a spreadsheet. LibrePythonista has its own PIP package manager to install additional Python packages.

LibrePythonista is currently in beta and is subject to change based on feedback. 

LibrePythonista is free and open source software so there are no fees to start using it.

LibrePythonista bring the power of [Pandas](https://pandas.pydata.org/pandas-docs/stable/index.html), [Matplotlib](https://matplotlib.org/stable/) and much more to LibreOffice Calc.

All  python code is executes on your local computer. This can alleviate many concerns around data privacy as your data

Using LibrePythonista is it possible to create Data frame's, Series, custom Graphs an much more directly in a spreadsheet.

LibrePythonista is built using [OOO Development Tools](https://python-ooo-dev-tools.readthedocs.io/en/latest/index.html) which removes many barriers when working with the LibreOffice API.

## What is LibrePythonista?

### Intro

LibrePythonista brings the power of Python analytics into LibreOffice Calc. Use it to process data in Calc with Python code. You type Python directly into a cell via the code edit window, the Python calculations runs locally, and your results are displayed in the sheet.

![500](https://github.com/user-attachments/assets/0493c94f-4cbf-4262-bc2f-f28ed4082906)

LibrePythonista comes with a core set of Python libraries. Use Python libraries to simplify your data analysis, find patterns and hidden insights, and visualize your data with plots.

### Features

LibrePythonista is a powerful tool for data analysis and visualization in LibreOffice Calc. It allows you to:

- Run Python code directly in a Calc cell
- Use Python libraries like Pandas, Matplotlib, and NumPy
- Install other python packages using a built-in package manager
- Create Data frames and Series
- Create custom graphs and charts
- Use Python to process data in Calc
- Use Python to automate tasks in Calc
- Use Python to create custom functions in Calc
- And much more

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

### Experimental Code Editor

As of version `0.6.0`, the code editor has been updated to include syntax highlighting and code completion. Currently the code editor is experimental.

To activated the experimental code editor, open the LibreOffice Extension Manager and click on the LibrePythonista extension. Then click on the Options button. Navigate to `LibrePythonista -> Options`  check the box for `Use Experimental Python Cell Editor` and click OK. Now restart LibreOffice to activate the new code editor.

![image](https://github.com/user-attachments/assets/745af61c-4c44-4f1c-be82-87cce9a603c6)

### Default Code Editor

![image](https://github.com/user-attachments/assets/f9d50085-d496-4f62-852f-cf98d514b5e8)

Or Python cells and charts can right click and choose `Pythonista --> Edit Code`
![image](https://github.com/user-attachments/assets/1b129b80-1558-42fe-b937-e4810f5be513)

Image for the code editor for the example above.
![tri_code](https://github.com/user-attachments/assets/a52c20f9-6536-437a-8ebd-8f997921b83f)


## Security

LibrePythonista is designed to run Python code locally on your computer. This means that your data never leaves your computer. LibrePythonista does not send your data to any external servers. LibrePythonista is open source software and the code is available on GitHub.

### Running Sheet Level Python

LibrePythonista allows Python code to be run at the sheet level. This means that Python code can be run in any cell in the sheet. This can be a security risk if the sheet is from a untrusted source. To mitigate this risk, LibrePythonista will not run Python code unless macros have been enabled for the sheet. This means that the user must enable macros for the sheet before Python code can be run.

Usually, when a sheet is opened, LibreOffice will ask the user if they want to enable macros. If the user does not enable macros, then Python code will not run. If the user enables macros, then Python code will run.

The recommended security setting for LibrePythonista is `Medium`. This setting will allow Python code to run when macros are enabled. To set the security level, go to `Tools -> Options -> LibreOffice -> Security -> Macro Security` and set the security level to `Medium`.

## Installation Troubleshoot

If you find an installation issue, please refer here: (For Linux - tested on linux mint 22)

- If you get following error message in dialog box when installing the extension:

  "Failed to register package <some_package>"

  Try to install _libreoffice-script-provider-python_ package from package manager.

- If you have a fresh copy of linux or _python3-pip_ package is not install or simply "pip3" command is not working on terminal. Please install _python3-pip_ otherwise extension will not start.

## Uninstall

As of version `0.7.0` LibrePythonista can also uninstall the Python Packages that were installed as part of the extension.

There are two ways to uninstall the extension python packages.

### With LibreOffice Running

The first way is via the extension options from the LibreOffice Extension Manager.

**Note:** LibreOffice must be a fresh start for this method to work. If you are not sure then restart LibreOffice and then try again.

Open the LibreOffice Extension Manager and click on the LibrePythonista extension. Then click on the Options button. Navigate to `LibrePythonista -> Uninstall`. Select the packages to uninstall and click on the `Uninstall` button. This will remove the selected Python packages.

If you want to uninstall the extension then select all the packages and click on the `Uninstall` button. This will remove all the Python packages that were installed as part of the extension.
Next, Click `OK` to go back to the Extension Manager and then click `Remove` to remove the extension.

**Note:** If the extension is not removed then any python package that was removed will be reinstalled when LibreOffice is restarted.


### With LibreOffice Closed

The second way, and the recommended way.
When LibrePythonista is installed it also writes a script file that can be used to uninstall the extension Python packages. The script location is different depending on the operating system and installation type, such as FlatPak and Snap.

To get the command to uninstall the extension Python packages, open the LibreOffice Extension Manager and click on the LibrePythonista extension. Then click on the Options button. Navigate to `LibrePythonista -> Uninstall`. Select the packages to uninstall and click on the `Copy command` button. This will copy the command to the clipboard.

Next you can uninstall the extension from LibreOffice and then close LibreOffice. Open a terminal (PowerShell on Windows) and paste the command that was copied to the clipboard and press enter. This will remove all the Python packages that were installed as part of the extension.

**Important:** It is important that LibreOffice not be running when this command is run. If LibreOffice is running then the command may not work correctly.

The output will be something like this:

```bash
bash "/home/username/.config/libreoffice/4/user/cleanup_LibrePythonista.sh"
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_typing-extensions.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_seaborn.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_matplotlib.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_verr.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_pandas.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_ooo-dev-tools.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_librepythonista-python-editor.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_odfpy.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_debugpy.json
Deleted file: /home/username/.local/lib/python3.12/site-packages/LibrePythonista_sortedcontainers.json
Deleted folder: /home/username/.local/lib/python3.12/site-packages/typing_extensions-4.12.2.dist-info
...
```

![image](https://github.com/user-attachments/assets/8e83f863-8b1c-4093-b69b-2a69eb78d377)

## Other Resources

- [LibrePythonista Channel](https://www.youtube.com/@LibrePythonista)
