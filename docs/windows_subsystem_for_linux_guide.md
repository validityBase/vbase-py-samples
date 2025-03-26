---
title: Windows Subsystem for Linux (WSL) vBase Setup Guide
---

<!-- omit in toc -->
# Windows Subsystem for Linux (WSL) vBase Setup Guide

This tutorial guides you through setting up Windows Subsystem for Linux (WSL)
to run vBase samples.

- [1. Install Windows Subsystem for Linux (WSL)](windows_subsystem_for_linux_guide.md#install-windows-subsystem-for-linux-wsl)
- [2. Install Jupyter Lab](windows_subsystem_for_linux_guide.md#install-jupyter-lab)
- [3. Install Git](windows_subsystem_for_linux_guide.md#install-git)
- [4. Clone the vbase-py-samples Git Repository](windows_subsystem_for_linux_guide.md#clone-the-vbase-py-samples-git-repository)
- [5. Run Jupyter Lab and Open a Notebook](windows_subsystem_for_linux_guide.md#run-jupyter-lab-and-open-a-notebook)

## 1. Install Windows Subsystem for Linux (WSL)<a href="#install-windows-subsystem-for-linux-wsl" id="install-windows-subsystem-for-linux-wsl"></a>

1. **Open PowerShell as Administrator:**
   Right-click the Start button and select “Windows PowerShell (Admin)”.

2. **Enable WSL**:
   Type the following command into PowerShell and press Enter:
    ```powershell
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    ```

3. **Enable VirtualMachinePlatform Feature:**
   Type the following command into PowerShell and press Enter:
    ```powershell
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    ```

4. **Restart your PC.**

5. **Download and Install a Linux Distribution:**
   Go to the Microsoft Store, search for the Ubuntu Linux distribution, and install it.

6. **Set WSL 2 as your default version:**
   Open PowerShell as Administrator again and run:
    ```powershell
    wsl --set-default-version 2
    ```

7. **Launch WSL:**
   After installation, launch WSL from the Start menu. The first launch will take some time due to setup. You will be prompted to create a user account and password.

## 2. Install Jupyter Lab<a href="#install-jupyter-lab" id="install-jupyter-lab"></a>

> **Note:** The following steps assume you have WSL installed and are running commands in the open WSL console window.

1. **Update and Upgrade Packages:**
   Update your Linux package list and upgrade the packages by running:
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2. **Install Python3 and pip:**
   Run the following command:
    ```bash
    sudo apt install python3 python3-pip -y
    ```

3. **Install Jupyter Lab:**
   Use pip to install Jupyter Lab:
    ```bash
    pip3 install jupyterlab
    ```

## 3. Install Git<a href="#install-git" id="install-git"></a>

1. **Install Git:**
   Run the following command to install git:
    ```bash
    sudo apt install git -y
    ```

## 4. Clone the vbase-py-samples Git Repository<a href="#clone-the-vbase-py-samples-git-repository" id="clone-the-vbase-py-samples-git-repository"></a>

1. **Create the vBase directory:**
   Create the directory where you want to clone vBase repositories and switch to this directory by  running:
    ```bash
    mkdir ~/validityBase && cd ~/validityBase
    ```

2. **Clone the Repository:**
   Once you are in the directory where you want to clone the repository, run:
    ```bash
    git clone https://github.com/validityBase/vbase-py-samples
    ```

## 5. Run Jupyter Lab and Open a Notebook<a href="#run-jupyter-lab-and-open-a-notebook" id="run-jupyter-lab-and-open-a-notebook"></a>

1. **Navigate to the Repository Directory:**
    ```bash
    cd vbase-py-samples
    ```

1. **Run Jupyter Lab:**
   Start Jupyter Lab by running:
    ```bash
    jupyter lab
    ```
    This command will start Jupyter Lab and provide you with a URL (including a security access token) to access it from your browser.

2. **Access Jupyter Lab:**
   Copy the provided URL and paste it into your browser's address bar to access Jupyter Lab.

3. **Open a Notebook:**
   In Jupyter Lab, navigate through the file explorer to find the notebook you wish to open in the `~/validityBase/vbase-py-samples/samples` folder. Click on it to open and interact with the notebook.
