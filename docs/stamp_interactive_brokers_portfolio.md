# stamp_interactive_brokers_portfolio.py

This sample illustrates how to retrieve, save, and stamp an Interactive Brokers (IB) portfolio.

The sample can be run from the command line interactively or as a script if your environment is set appropriately.

The sample will run the **Interactive Brokers (IB) Client Portal Gateway** on your Windows computer and make a request to it using the Web API from Python.

## Prerequisites
1. **Interactive Brokers Account**: You must have an IB account (live or paper trading).
2. **Python**: Ensure Python is installed on your Windows machine.
3. **vBase**: Follow the [vBase Windows Guide](windows_guide.md) to set up Windows environment to run vBase samples.
4. **Set Environment Variables**: Set the following environment variables for your IB and vBase configuration:
   - `IB_ACCOUNT_ID` - The IB account id.
   - `AWS_ACCESS_KEY_ID` - The Access Key used to connect to the S3 service.
   - `AWS_SECRET_ACCESS_KEY` - The Secret Key used to connect to the S3 service.
   - `AWS_S3_BUCKET_NAME` - The AWS S3 bucket name used to store the portfolio data.
   - `VBASE_FORWARDER_URL` - vBase Forwarder Service URL:
     - https://dev.api.vbase.com/forwarder/ for development/testnet.
     - https://api.vbase.com/forwarder/ for production.
   - `VBASE_API_KEY` - The vBase API Key used to access the Forwarder service.
   - `VBASE_COMMITMENT_SERVICE_PRIVATE_KEY` - The private key used to sign portfolio stamps.

# User Dataset Config
VBASE_DATASET_NAME="ib_portfolio_stamping"

## 1: Download and Install Client Portal Gateway
Interactive Brokers provides the **Client Portal Gateway** as a lightweight API gateway for accessing account data via a Web API. Follow these steps to download and run the gateway:

1. **Download the Client Portal Gateway**:
   - Visit the official [Client Portal Gateway page](https://www.interactivebrokers.com/en/index.php?f=50462) and download the latest **Client Portal Gateway** for Windows.
   - Alternatively, you can access the latest **Client Portal Gateway** directly from the [IBKR GitHub Repository](https://github.com/InteractiveBrokers/clientportal.gw).

2. **Extract the ZIP File**:
   - After downloading the Client Portal Gateway ZIP file, extract it to a folder on your machine (e.g., `C:\IBClientPortalGateway`).

3. **Run the Gateway**:
   - Navigate to the extracted folder and double-click the `ibgateway.bat` file.
   - This will start the gateway, and it will launch a web page where you can log in to your Interactive Brokers account using your credentials and 2FA (if required).
   - After successful login, the gateway will start and display a `Gateway session started` message, along with the Web API access URL and port number (default is `127.0.0.1:5000`).

## 2: Authenticate to the Gateway
Once the gateway is running, it provides a Web API that requires authentication via the session token returned during the login process. The gateway will keep running in the background.

## 3: Run the Sample

Run the sample from the command line:
   ```bash
   python3 stamp_interactive_brokers_portfolio.py
   ```

or walk through the sample in an interactive window.