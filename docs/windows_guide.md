---
title: Windows vBase Setup Guide
---

<!-- omit in toc -->
# Windows vBase Setup Guide

This tutorial guides you through setting up Windows environment
to run vBase samples.

We provide steps for setting up a Python virtual environment (venv) on a Windows 10 system and installing all the necessary build tools required for compiling and installing typical Python packages.

- [1: Install Python on Windows](#1-install-python-on-windows)
- [2: Install Microsoft Visual C++ Build Tools](#2-install-microsoft-visual-c-build-tools)
- [3: Create a Python Virtual Environment (venv)](#3-create-a-python-virtual-environment-venv)
- [4: Install Required Build Tools for Python Packages](#4-install-required-build-tools-for-python-packages)
- [5: Install Python Packages (with Dependencies)](#5-install-python-packages-with-dependencies)
- [6: Verify Installation (Optional)](#6-verify-installation-optional)

## 1: Install Python on Windows

If Python is not already installed on your system, follow these steps:

1. **Download Python**:
   - Visit the [official Python website](https://www.python.org/downloads/) and download the latest version of Python for Windows.
   
2. **Run the Installer**:
   - During installation, **check the box** that says **"Add Python to PATH"** at the bottom of the installer.
   - Select **Customize Installation**.
   - Ensure that the following options are selected:
     - `pip` (Python package manager)
     - `venv` (Virtual environment support)

3. **Finish Installation** and verify Python is installed:
   - Open **Command Prompt** and run:
     ```bash
     python --version
     ```
   - You should see the installed Python version.

## 2: Install Microsoft Visual C++ Build Tools

Many Python packages with native extensions (like `cytoolz`, `lru-dict`, etc.) require compilation using Microsoft Visual C++ Build Tools.

1. **Download Microsoft Visual C++ Build Tools**:
   - Go to the [Visual Studio Build Tools page](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and download the installer.

2. **Install the C++ Build Tools**:
   - In the installer, select the **"Desktop development with C++"** workload.
   - Ensure the following components are selected:
     - **MSVC v142 - VS 2019 C++ x64/x86 build tools**
     - **Windows 10 SDK**

3. **Finish Installation** and allow the tools to install.

## 3: Create a Python Virtual Environment (venv)

1. **Open Command Prompt** (or PowerShell) and navigate to your project folder:
   ```bash
   cd C:\path\to\your\project
   ```

2. **Create a virtual environment** using the `venv` module:
   ```bash
   python -m venv venv
   ```

   This creates a folder called `venv` in your project directory, which will contain the virtual environment.

3. **Activate the virtual environment**:
   ```bash
   .\venv\Scripts\activate
   ```

   You should now see `(venv)` at the beginning of your command line, indicating that the virtual environment is active.

## 4: Install Required Build Tools for Python Packages

Some packages need additional Python build tools like `setuptools` and `wheel`. Install these tools globally in your virtual environment:

1. **Upgrade `pip`, `setuptools`, and `wheel`**:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install `build` (optional)**:
   The `build` package helps when building Python projects that require C extensions.
   ```bash
   pip install build
   ```

## 5: Install Python Packages (with Dependencies)

Now that the virtual environment and build tools are set up, you can install any typical Python package, even if it has native dependencies that require compilation.

1. **Change to the project folder** using Command Prompt or PowerShell navigate to the `vbase-py-sample` project folder:
   ```bash
   cd C:\path\to\your\projects\vbase-py-samples
   ```

2. **Installing packages with `requirements-win.txt`**:
   The `vbase-py-samples` project comes with its `requirements-win.txt`.
   This installs the required pre-built packages available for Windows:
   ```bash
   pip install -r requirements-win.txt
   ```

## 6: Verify Installation (Optional)

If the above `pip install` command succeeded, you are ready to run the samples.

After installing your packages, you can verify the packages installed in your virtual environment by running:

```bash
pip freeze
```

This will list all installed packages along with their versions.
