# Windows vBase Setup Guide

Use these steps to run the vBase samples from PowerShell on Windows 10 or 11.

## 1. Install Python and Git

Install [Python for Windows](https://www.python.org/downloads/windows/) and select **Add Python to PATH** in the installer. The core samples support Python 3.8 or newer; the optional Alpaca sample requires Python 3.10 or newer.

Install [Git for Windows](https://git-scm.com/download/win) when you want to clone the repository. Git is not required when you use the ZIP download option below.

Open PowerShell and confirm the tools are available:

```powershell
python --version
git --version
```

## 2. Get the samples

### Option 1: Clone with Git

Create only the parent directory, then clone the repository into it:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\Projects\validityBase"
Set-Location "$env:USERPROFILE\Projects\validityBase"
git clone https://github.com/validityBase/vbase-py-samples.git
Set-Location vbase-py-samples
```

### Option 2: Download a ZIP

Open the [vbase-py-samples repository](https://github.com/validityBase/vbase-py-samples), select **Code**, then **Download ZIP**. Extract it under a directory such as `%USERPROFILE%\Projects\validityBase`, rename the extracted folder to `vbase-py-samples`, and open PowerShell in that folder.

## 3. Create the environment

From the repository root, create and activate a virtual environment, then install the samples:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-win.txt
```

If PowerShell prevents the activation script from running, see Microsoft's [execution policy documentation](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies). In Command Prompt, activate the same environment with `venv\Scripts\activate.bat`.

## 4. Configure vBase

Copy the safe environment template:

```powershell
Copy-Item .env.example .env
```

Open `.env`, set `VBASE_API_KEY` to the key from [vBase Account Settings](https://app.vbase.com/profile/#account_settings), and save the file. Never commit `.env`.

## 5. Run a sample

```powershell
python samples\create_set.py
python samples\add_string_dataset_record.py
```

See the [Quickstart](quickstart.md) for Amazon S3 and verifier configuration.
