<!-- omit in toc -->

# vBase Python Samples Quickstart

The following steps guide you through this process of setting up vBase Python SDK in your local environment:

<!-- omit in toc -->
> **Note for Windows users:**
> If you’re on Windows, the following instructions will work on the Windows Subsystem for Linux (WSL). WSL provides a Linux environment on your Windows OS. Please follow [this guide to set up your WSL environment for vBase.](windows_subsystem_for_linux_guide.md)
- [1. Get a vBase API Key](#get-a-vbase-api-key)
- [2. Create the vBase Directory](#create-the-vbase-directory)
- [3. Install the vBase Python SDK](#install-the-vbase-python-sdk)
- [4. Clone the vBase Python SDK Samples](#clone-the-vbase-python-sdk-samples)
- [5. Set up Your Environment](#set-up-your-environment)
- [6. Verify Your Environment](#verify-your-environment)
- [7. You Are All Set!](#you-are-all-set)


## 1. Get your vBase API Key <a href="#get-a-vbase-api-key" id="get-a-vbase-api-key"></a>


Please [access the vBase App](https://app.vbase.com), sign-up, and retrieve the API Key from your user profile if you wish to have the simplest experience. The API key is needed to access the forwarder API service. This service simplifies commitment and validation operations but is not required for interacting with vBase.


## 2. Create the vBase Directory <a href="#create-the-vbase-directory" id="create-the-vbase-directory"></a>


Create the directory where you want to clone vBase repositories and switch to this directory by running:
```bash
mkdir ~/validityBase && cd ~/validityBase
```


## 3. Install the vBase Python SDK <a href="#install-the-vbase-python-sdk" id="install-the-vbase-python-sdk"></a>


Install the `vbase` python package that provides the vBase Python SDK from GitHub:
```bash
pip install git+https://github.com/validityBase/vbase-py.git
```


## 4. Clone the vBase Python SDK Samples <a href="#clone-the-vbase-python-sdk-samples" id="clone-the-vbase-python-sdk-samples"></a>


Clone the `vbase-py-samples` GitHub repository:
```bash
git clone https://github.com/validityBase/vbase-py-samples.git
```


## 5. Set up Your Environment <a href="#set-up-your-environment" id="set-up-your-environment"></a>

   **Option 1: Copy your existing environment:** If you have previously configured vBase access, for instance, when using the `vbase-py-tools` package, you can re-use those settings by copying `.env` file to the `vbase-py-samples` folder:
   ```bash
   cp ~/validityBase/vbase-py-tools/.env ~/validityBase/vbase-py-samples
   ```
   
**Option 2: Create a new environment:**
   If this is your first time working with vBase, you should configure new settings.
Please install the `vbase-py-tools` package and follow the setup instructions using the `config_env` script provided in that package as instructed at the following link: [vBase Py Tools Setup Instructions](https://github.com/validityBase/vbase-py-tools/blob/main/docs/setup.md).


## 6. Verify Your Environment <a href="#verify-your-environment" id="verify-your-environment"></a>


Below is a summary of the configuration settings from the resulting `.env` file:

```bash
# This is the vBase Forwarder URL.
# The following is the production vBase Forwarder service URL.
# Users should not change this value:
VBASE_FORWARDER_URL="https://api.vbase.com/forwarder/"
# This is the API key for accessing the vBase Forwarder service.
# Users should set this value to the API key they received from vBase.
VBASE_API_KEY="USER_VBASE_API_KEY"

# This is the private key for making stamps/commitments.
# This key signs and controls all operations for the user
# -- it must be kept secret.
# vBase will never request this value.
VBASE_COMMITMENT_SERVICE_PRIVATE_KEY="USER_VBASE_COMMITMENT_SERVICE_PRIVATE_KEY"
```
You can keep these values in the `.env` file in the working directory of your Python code or add them to your command environment.


## 7. You Are All Set! <a href="#you-are-all-set" id="you-are-all-set"></a>


You can make and verify commitments. Please review the samples and their documentation for additional info.
