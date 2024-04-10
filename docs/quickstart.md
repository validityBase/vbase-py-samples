# vBase Python Samples Quickstart

The following steps guide you through this process of setting up vBase Python SDK in your local environment:

> **Note for Windows users:**
    If you're on Windows, the following instructions will work on the Windows Subsystem for Linux (WSL). WSL provides a Linux environment on your Windows OS. Please follow the following guide to set up your WSL environment for vBase: [https://docs.vbase.com/getting-started/windows-subsystem-for-linux-wsl-guide](https://docs.vbase.com/getting-started/windows-subsystem-for-linux-wsl-guide)

1. **Get a vBase API key:**
    Please [contact vBase](https://www.vbase.com/contact/) and request an API key if you wish to have the simplest experience. The API key is needed to access the forwarder API service, which simplifies commitment and validation operations but is not required for interacting with vBase.

1. **Create the vBase directory:**
    Create the directory where you want to clone vBase repositories and switch to this directory by running:
    ```bash
    mkdir ~/validityBase && cd ~/validityBase
    ```

1. **Install the vBase Python SDK:**
    Install the `vbase` python package that provides the vBase Python SDK from GitHub:
    ```bash
    pip install git+https://github.com/validityBase/vbase-py.git
    ```

2. **Install the vBase Python SDK Samples:**
    Clone the `vbase-py-samples` GitHub repository:
    ```bash
    pip install git+https://github.com/validityBase/vbase-py-samples.git
    ```

3. **Set up your environment:**

   1. **Option 1: Copy your existing environment:**
        If you have previously configured vBase access, for instance when using the `vbase-py-tools` package, you can re-use those settings by copying `.env` file to the `vbase-py-samples` folder:
        ```bash
        cp ~/validityBase/vbase-py-tools/.env ~/validityBase/vbase-py-samples
        ```

   2. **Option 2: Create a new environment:**
        If this is your first time working with vBase, you should configure new settings.

        Please install the `vbase-py-tools` package and follow the setup instructions using the `config_env` script provided in that package as instructed at the following link: [https://docs.vbase.com/python-sdk/package-vbase-py-tools/setup](https://docs.vbase.com/python-sdk/package-vbase-py-tools/setup)

4. **Verify your environment:**
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
    You can keep these values in `.env` file in the working directory of your Python code or add them to your command environment.

5. **You are all set!**
    You can make and verify commitments. Please review the samples and their documentation for additional info.
