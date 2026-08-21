# vBase Python Samples Quickstart

This guide configures the recommended `vbase-api` Python client and runs the first samples.

## 1. Get a vBase API key <a href="#get-a-vbase-api-key" id="get-a-vbase-api-key"></a>

Sign in to the [vBase app](https://app.vbase.com/) and copy your API key from [Account Settings](https://app.vbase.com/profile/#account_settings). The key belongs to your vBase account. Do not create it in GitHub and do not commit it to this repository.

## 2. Install the samples <a href="#install-the-samples" id="install-the-samples"></a>

```bash
git clone https://github.com/validityBase/vbase-py-samples.git
cd vbase-py-samples
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements-win.txt
```

## 3. Configure the environment <a href="#configure-the-environment" id="configure-the-environment"></a>

Copy the safe template and add your API key:

```bash
cp .env.example .env
```

```ini
VBASE_API_KEY="YOUR_VBASE_API_KEY"
```

The samples load `.env` without replacing values already present in the process environment.

## 4. Verify the setup <a href="#verify-the-setup" id="verify-the-setup"></a>

Create or retrieve the sample collection, then stamp and verify a text record:

```bash
python samples/create_set.py
python samples/add_string_dataset_record.py
```

A successful run prints the collection CID, object CID, owner address, stamp timestamp, and transaction hash.

## 5. Configure Amazon S3 <a href="#configure-amazon-s3" id="configure-amazon-s3"></a>

Only the storage-backed samples need AWS configuration. Set the bucket name in `.env`:

```ini
AWS_S3_BUCKET="YOUR_BUCKET_NAME"
```

The samples use boto3's standard credential and region resolution. A shared profile, AWS IAM Identity Center (SSO), or an IAM role needs no static access keys in `.env`. When using environment credentials, add:

```ini
AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
AWS_DEFAULT_REGION="us-east-1"
# AWS_SESSION_TOKEN="YOUR_TEMPORARY_SESSION_TOKEN"
```

Use `AWS_SESSION_TOKEN` only with temporary AWS credentials. The bucket name must not include `s3://`.

Run a producer first. It prints values for the matching verifier:

```bash
python samples/produce_portfolio_history_json_s3.py
```

Add the printed collection information to `.env`, then run the verifier:

```ini
VBASE_COLLECTION_CID="0x..."
VBASE_OWNER_ADDRESS="0x..."
```

```bash
python samples/verify_portfolio_history_json_s3.py
```

The verifier requires exactly the expected sample files and matches every file CID to the configured collection and owner. For canonical complete-archive verification, use [vBase Verify](https://app.vbase.com/verify/?method=collection).
