# Python LibreOffice Pip Extension Template

## Introduction

This project is intended to be a template for developers of LibreOffice Extensions.

Need to create a quick cross platform extension that installs python packages requirements? If so you found the correct template.

If you only need to create an extension that installs one or more Python Packages into LibreOffice the no code experience is needed. Simply make a repo from the current template, change configuration, build and your done. A new LibreOffice extension has been generated that will install your python packages when it is installed into LibreOffice. See the [Quick Start](https://github.com/Amourspirit/python-libreoffice-pip/wiki/Quick-Start) in the Wiki.

This project is also well suited for developers who want to create a LibreOffice Extension using Python and need to Pip install one or more requirements.

All the tools needed to develop, debug, and test are included in this template.
A developer can use this template to create a LibreOffice Extension that uses Python and Pip install.

The extensions created with this template can be installed cross platform.

Tested on the following:

- Windows
- Windows LibreOffice Portable
- Mac
- Linux sudo installed LibreOffice
- Linux Snap installed LibreOffice
- Linux Flatpak installed LibreOffice
- Linux AppImage LibreOffice

For more information see the [Wiki](https://github.com/Amourspirit/python-libreoffice-pip/wiki)

For a working example see the following extensions:

- [OOO Development Tools Extension](https://github.com/Amourspirit/libreoffice_ooodev_ext#readme)
- [OooDev GUI Automation for Windows](https://github.com/Amourspirit/ooodev-gui-win-ext#readme)

<details>
<summary>Original Template Readme</summary>

# Live LibreOffice Python

Live LibreOffice Python is a complete development environment for creating, debugging and testing python scripts. It leverages the power of [VS Code] and has [LibreOffice] baked in that can be access via the internal web browser or via your local web browser which allows for a much more pleasant and consistent debugging experience.

With the power of [GitHub Codespaces](https://docs.github.com/en/codespaces/overview) it is possible to have [VS Code] and [LibreOffice] running together. One big benefit is a isolated and [VS Code]/[LibreOffice] environment.

Locally a project based upon this template can also be run in a [Development Container](https://code.visualstudio.com/remote/advancedcontainers/overview).

It is also possible to use [GitHub CLI/CD] to create a workflow that test your project with the presents of LibreOffice. This template has a working example of testing using [GitHub CLI/CD].

There are Built in [Tools](https://github.com/Amourspirit/live-libreoffice-python/wiki/Tools) such as [gitget](https://github.com/Amourspirit/live-libreoffice-python/wiki/Tools#gitget) that allow you to quickly add examples to your project from sources such as [LibreOffice Python UNO Examples]. Also there is a built in [console](https://github.com/Amourspirit/live-libreoffice-python/wiki/Console) to help debug the [API](https://api.libreoffice.org/).

This templated can also be leveraged to demonstrate working examples of code.

[![image](https://github.com/Amourspirit/live-libreoffice-python/assets/4193389/35758c26-63b7-48f9-99c0-84dd19b26a8f)](https://github.com/Amourspirit/live-libreoffice-python/assets/4193389/35758c26-63b7-48f9-99c0-84dd19b26a8f)

## Getting Started

See the [Getting Started](https://github.com/Amourspirit/live-libreoffice-python/wiki/Getting-Started) in the [Wiki](https://github.com/Amourspirit/live-libreoffice-python/wiki).

[VS Code]:https://code.visualstudio.com/

[LibreOffice]:https://www.libreoffice.org/
[GitHub CLI/CD]:https://resources.github.com/ci-cd/
[LibreOffice Python UNO Examples]:https://github.com/Amourspirit/python-ooouno-ex

</details>
