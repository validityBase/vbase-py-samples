# Stamp Interactive Brokers Portfolio

<!-- omit in toc -->

This sample illustrates how to retrieve, save, and stamp an Interactive Brokers (IB) portfolio.

The sample can be run from the command line interactively or as a script if your environment is set appropriately.

The sample will run the **Interactive Brokers (IB) Client Portal Gateway** on your Windows computer and make a request to it using the Web API from Python.

You can find the implementation in [`stamp_interactive_brokers_portfolio.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/stamp_interactive_brokers_portfolio.py).

- [1. Prerequisites](stamp_interactive_brokers_portfolio.md#prerequisites)
- [2. Download and Install Client Portal Gateway](stamp_interactive_brokers_portfolio.md#download-and-install-client-portal-gateway)
- [3. Set Environment Variables](stamp_interactive_brokers_portfolio.md#set-environment-variables)
- [4. Run the Sample](stamp_interactive_brokers_portfolio.md#run-the-sample)

## 1. Prerequisites <a href="#prerequisites" id="prerequisites"></a>

1. **Interactive Brokers Account**: You must have an IB account (live or paper trading).
2. **Python**: Ensure Python is installed on your Windows machine.
3. **vBase**: Follow the [vBase Windows Guide](windows_guide.md) to set up Windows environment to run vBase samples.

## 2. Download and Install Client Portal Gateway <a href="#download-and-install-client-portal-gateway" id="download-and-install-client-portal-gateway"></a>

Interactive Brokers provides the **Client Portal Gateway** as a lightweight API gateway for accessing account data via a Web API. Follow these steps to download and run the gateway:

1. **Download the Client Portal Gateway**:
   - Visit the official [Client Portal Gateway page](https://www.interactivebrokers.com/en/index.php?f=50462) and download the latest **Client Portal Gateway** for Windows.
   - Alternatively, you can access the latest **Client Portal Gateway** directly from the [IBKR GitHub Repository](https://github.com/InteractiveBrokers/clientportal.gw).
2. **Extract the ZIP File**:
   - After downloading the Client Portal Gateway ZIP file, extract it to a folder on your machine (e.g., `C:\IBClientPortalGateway`).
3. **Run the Gateway**:
   - At the Command Line, run:

   ```default
   cd \\path\\to\\clientportal\\clientportal.gw
   bin\\run.bat root\\conf.yaml
   ```

4. **Authenticate to the Gateway**:
   - Open the client portal in a browser:

   ```default
   https://localhost:5000/
   ```

   You may need to ignore security warnings and accept the self-signed certificate in your browser.
   - Login to the client portal with your IB credentials.
   - You should see the “Client login succeeds” message.
   - Once the gateway is running, it provides a Web API that requires authentication via the session token returned during the login process. The gateway will keep running in the background.

## 3. Set Environment Variables<a href="#set-environment-variables" id="set-environment-variables"></a>

Set the following environment variables for your IB and vBase configuration:

- IB Configuration:
  - `IB_ACCOUNT_ID` - The IB account id.
- AWS S3 Configuration (Optional if you save the portfolio data elsewhere):
  - `AWS_ACCESS_KEY_ID` - The Access Key used to connect to the S3 service.
  - `AWS_SECRET_ACCESS_KEY` - The Secret Key used to connect to the S3 service.
  - `AWS_S3_BUCKET_NAME` - The AWS S3 bucket name used to store the portfolio data.
- vBase Configuration:
  - `VBASE_FORWARDER_URL` - vBase Forwarder Service URL:
    - https://dev.api.vbase.com/forwarder/ for development/testnet.
    - https://api.vbase.com/forwarder/ for production.
  - `VBASE_API_KEY` - The vBase API Key used to access the Forwarder service.
  - `VBASE_COMMITMENT_SERVICE_PRIVATE_KEY` - The private key used to sign portfolio stamps.
  - `VBASE_DATASET_NAME` - The name of the vBase dataset that will hold the portfolio history.

## 4. Run the Sample<a href="#run-the-sample" id="run-the-sample"></a>

Run the sample from the command line:

```bash
python3 stamp_interactive_brokers_portfolio.py
```

or walk through the sample in an interactive window.
