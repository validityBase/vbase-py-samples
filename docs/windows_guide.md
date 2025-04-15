# Windows vBase Setup Guide

<!-- omit in toc -->

This tutorial guides you through setting up Windows environment to run vBase samples.

We provide steps for setting up a Python virtual environment (venv) on a Windows 10 system and installing all the necessary build tools required for compiling and installing typical Python packages.

- [1. Install Python on Windows](windows_guide.md#install-python-on-windows)
- [2. Install Microsoft Visual C++ Build Tools](windows_guide.md#install-microsoft-visual-c-build-tools)
- [3. Create the Project Directory](windows_guide.md#create-the-project-directory)
- [4. Clone vBase Samples into the Project Directory](windows_guide.md#clone-vbase-samples-into-the-project-directory)
  - [4.1. Option 1. Clone the vbase-py-samples repository:](windows_guide.md#option-1-clone-the-vbase-py-samples-repository)
  - [4.2. Option 2. Download the vbase-py-samples repository as a ZIP file:](windows_guide.md#option-2-download-the-vbase-py-samples-repository-as-a-zip-file)
- [5. Create a Python Virtual Environment (venv)](windows_guide.md#create-a-python-virtual-environment-venv)
- [6. Install Required Build Tools for Python Packages](windows_guide.md#install-required-build-tools-for-python-packages)
- [7. Install vBase Dependencies](windows_guide.md#install-vbase-dependencies)
- [8. You Are All Set!](windows_guide.md#you-are-all-set)

## 1. Install Python on Windows<a href="#install-python-on-windows" id="install-python-on-windows"></a>

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

## 2. Install Microsoft Visual C++ Build Tools<a href="#install-microsoft-visual-c-build-tools" id="install-microsoft-visual-c-build-tools"></a>

Many Python packages require compilation using Microsoft Visual C++ Build Tools.

1. **Download Microsoft Visual C++ Build Tools**:

   - Go to the [Visual Studio Build Tools page](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and download the installer.

2. **Install the C++ Build Tools**:

   - In the installer, select the **"Desktop development with C++"** workload.
   - Ensure the following components are selected:
     - **MSVC v142 - VS 2019 C++ x64/x86 build tools**
     - **Windows 10 SDK**

3. **Finish Installation** and allow the tools to install.

## 3. Create the Project Directory<a href="#create-the-project-directory" id="create-the-project-directory"></a>

These instructions assume that the samples will be located in the `C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples` folder.

Create the project folder and switch to it:

```bash
mkdir -p  C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples
cd  C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples
```

## 4. Clone vBase Samples into the Project Directory<a href="#clone-vbase-samples-into-the-project-directory" id="clone-vbase-samples-into-the-project-directory"></a>

Samples can be cloned using `git` or downloaded and extracted as a ZIP file.

### 4.1. Option 1. Clone the vbase-py-samples repository<a href="#option-1-clone-the-vbase-py-samples-repository" id="option-1-clone-the-vbase-py-samples-repository"></a>

If you have `git` installed, clone the `vbase-py-samples` repository using the command line:

```bash
cd C:\Users\%USERNAME%\Projects\validityBase
git clone https://github.com/validityBase/vbase-py-samples.git
```

### 4.2. Option 2. Download the vbase-py-samples repository as a ZIP file<a href="#option-2-download-the-vbase-py-samples-repository-as-a-zip-file" id="option-2-download-the-vbase-py-samples-repository-as-a-zip-file"></a>

On Windows 10, the easiest way to clone a GitHub repository without installing additional software is to use **GitHub’s built-in Zip download** feature. This method allows you to download the repository as a ZIP file and extract it, effectively "cloning" the repository without requiring Git or any command-line tools.

1. **Go to the GitHub Repository**:

   - Open your web browser and navigate to the GitHub repository page: https://github.com/validityBase/vbase-py-samples

2. **Download as ZIP**:

   - On the repository’s main page, click the green **Code** button.
   - In the dropdown, select **Download ZIP**. This will download the entire repository as a ZIP file.

3. **Extract the ZIP File**:
   - Once downloaded, locate the ZIP file (usually in your **Downloads** folder).
   - Right-click on the ZIP file and select **Extract All...**.
   - Choose a destination folder, such as the samples folder `C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples`, and extract the contents.

## 5. Create a Python Virtual Environment (venv)<a href="#create-a-python-virtual-environment-venv" id="create-a-python-virtual-environment-venv"></a>

1. **Open Command Prompt** (or PowerShell) and navigate to your project folder:

   ```bash
   cd C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples
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

## 6. Install Required Build Tools for Python Packages<a href="#install-required-build-tools-for-python-packages" id="install-required-build-tools-for-python-packages"></a>

Some packages need additional Python build tools like `setuptools` and `wheel`. Install these tools globally in your virtual environment:

1. **Upgrade `pip`, `setuptools`, and `wheel`**:

   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install `build`**: The `build` package helps when building some Python projects.

   ```bash
   pip install build
   ```

## 7. Install vBase Dependencies<a href="#install-vbase-dependencies" id="install-vbase-dependencies"></a>

Now that the virtual environment and build tools are set up, you can install the vBase dependencies:

1. **Change to the project folder** using Command Prompt or PowerShell navigate to the `vbase-py-samples` project folder:

   ```bash
   cd C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples
   ```

2. **Instal dependencies**: The `vbase-py-samples` project comes with its `requirements-win.txt`. This installs the required pre-built packages available for Windows:

   ```bash
   pip install -r requirements-win.txt
   ```

## 8. You Are All Set!<a href="#you-are-all-set" id="you-are-all-set"></a>

Once the above `pip install` command succeeded, you are ready to run the samples.
