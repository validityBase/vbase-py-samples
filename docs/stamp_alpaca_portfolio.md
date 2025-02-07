<!-- omit in toc -->

# Stamp Alpaca Portfolio

This sample illustrates how to retrieve, save, and stamp an Alpaca portfolio.

The sample can be run from the command line interactively or as a script if your environment is set appropriately.

You can find the implementation in [`stamp_alpaca_portfolio.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/stamp_alpaca_portfolio.py).

- [1. Prerequisites](#prereq)
- [2. (Optional) Sign Up for an Alpaca Account](#signup)
- [3. (Optional) Enable Paper Trading](#paper-trading)
- [4. Obtain Your API Keys](#obtain-keys)
- [5. Switch to the Sample Directory](#switch-directory)
- [6. Install the Alpaca Python Package](#install-alpaca)
- [7. Set Environment Variables](#set-env)
- [8. Run the Sample](#run-sample)

## 1. Prerequisites<a href="#prereq" id="#prereq"></a>

1. **Alpaca Account**: You must have an Alpaca account (live or paper trading).
2. **Python**: Ensure Python is installed on your Windows machine.
3. **vBase**: Follow the [vBase Windows Guide](windows_guide.md) to set up Windows environment to run vBase samples.
4. **Alpaca Python SDK**: Alpaca provides a Python SDK to simplify accessing their API.
   To install the SDK, open your terminal or command prompt and install the SDK:
   ```bash
   pip install alpaca-trade-api
   ```

## 2. (Optional) Sign Up for an Alpaca Account<a href="#signup" id="#signup"></a>

1. **Go to Alpaca Website**:
   - Visit [Alpaca Markets](https://alpaca.markets/) and click on **Sign Up**.
2. **Create Your Account**:
   - Fill in the required personal information (name, email, password) and click **Create Account**.
3. **Verify Your Email**:
   - After signing up, you will receive a verification email from Alpaca. Click on the link to verify your email address.
4. **Complete Account Information**:
   - Once you’ve verified your email, Alpaca will ask for additional information to complete your account setup. This is standard for brokerage accounts.
   - You may need to set up multi-factor authentication (MFA) with an Authenticator app or SMS.
   - You may need to provide your address, phone number, and identity verification information.

## 3. (Optional) Enable Paper Trading<a href="#paper-trading" id="#paper-trading"></a>

1. **Go to the Paper Trading Section**:
   - Once your account is set up and verified, log in to your Alpaca account dashboard.
   - In the **dashboard**, locate and click on the **Paper Trading** section. Paper trading allows you to simulate trading with fake money without risking real funds.
2. **Enable Paper Trading**:
   - Toggle the **Enable Paper Trading** option if it’s not enabled by default.
   - You will receive a starting balance in your paper trading account.

## 4. Obtain Your API Keys<a href="#obtain-keys" id="#obtain-keys"></a>

- In the dashboard, go to **Your Account** > **API Keys**.
- Generate API keys for **paper trading**. These include:
  - **API Key ID**: Used to identify your account.
  - **API Secret Key**: Used to authenticate your requests.
- Store your **API Key ID** and **API Secret Key** securely. You’ll use these in your environment variables that Python scripts will use to access your Alpaca account.

## 5. Switch to the Sample Directory<a href="#switch-directory" id="#switch-directory"></a>

Open Command Prompt (or PowerShell) and navigate to your project folder:

```bash
cd C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples
```

## 6. Install the Alpaca Python Package<a href="#install-alpaca" id="#install-alpaca"></a>

Install the `alpaca_trade_api` Python package:

```bash
pip install alpaca_trade_api
```

## 7. Set Environment Variables<a href="#set-env" id="#set-env"></a>

Set the following environment variables for your IB and vBase configuration.    - Alpaca Configuration:
- `ALPACA_API_KEY` - The Alpaca API Key.
- `ALPACA_API_SECRET` - The Alpaca API Secret.
- `ALPACA_API_BASE_URL` - Base URL for the Alpaca API:
- https://paper-api.alpaca.markets for paper trading.
- https://api.alpaca.markets for live trading.

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

You can define these variables in the `.env` file in your `C:\Users\%USERNAME%\Projects\validityBase\vbase-py-samples` folder. Your .env file should look as follows:

```python
# Alpaca Config
ALPACA_API_KEY="ALPACA_API_KEY"
ALPACA_API_SECRET="ALPACA_API_SECRET"
ALPACA_API_BASE_URL="https://paper-api.alpaca.markets"

# AWS Config
AWS_ACCESS_KEY_ID="AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY="AWS_SECRET_ACCESS_KEY"
AWS_S3_BUCKET_NAME="test-bucket"
AWS_S3_FOLDER_NAME="portfolio_history/alpaca_portfolio_stamping"

# vBase Config
VBASE_FORWARDER_URL="https://dev.api.vbase.com/forwarder/"
VBASE_API_KEY="VBASE_API_KEY"
VBASE_COMMITMENT_SERVICE_PRIVATE_KEY="VBASE_COMMITMENT_SERVICE_PRIVATE_KEY"

# User Dataset Config
VBASE_DATASET_NAME="alpaca_portfolio_stamping_test"
```

## 8. Run the Sample<a href="#run-sample" id="#run-sample"></a>

Run the sample from the command line:

```bash
python samples\stamp_alpaca_portfolio.py
```

or walk through the sample in an interactive window.
