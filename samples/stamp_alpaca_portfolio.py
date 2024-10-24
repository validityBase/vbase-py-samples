"""
Alpaca Portfolio Stamping Sample

The sample can be run from the command line interactively or as a script
if your environment is set appropriately.
"""

# ## Imports

from io import StringIO
from datetime import datetime
import os
import pprint
import json
import dotenv
import pandas as pd
import requests
from vbase import (
    VBaseClient,
    VBaseDataset,
    VBaseStringObject,
)

import alpaca_trade_api as tradeapi

from aws_utils import (
    create_s3_client_from_env,
    write_s3_object,
)
from utils import get_env_var_or_fail


# ## Configuration

# Load dotenv configuration if available, else, use environment variables.
dotenv.load_dotenv(".env", verbose=True, override=True)

# Load Alpaca configuration from environment variables.
ALPACA_API_KEY = get_env_var_or_fail("ALPACA_API_KEY")
ALPACA_API_SECRET = get_env_var_or_fail("ALPACA_API_SECRET")
ALPACA_API_BASE_URL = get_env_var_or_fail("ALPACA_API_BASE_URL")


# ## Get Portfolio from Alpaca

# Initialize the Alpaca API
api = tradeapi.REST(
    ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_API_BASE_URL, api_version="v2"
)

# Fetch your portfolio positions.
resp = api.list_positions()
if len(resp) == 0:
    raise Exception("No equity positions found.")

# Extract the symbol and market value from the positions.
positions = [
    {"sym": p.symbol, "value": p.market_value}
    for p in resp
]

# Normalize weights as % of the total value.
total_value = sum([p["value"] for p in positions])
for p in positions:
    p["wt"] = p["value"] / total_value

# Drop the value field.
for p in positions:
    p.pop("value")

# Create a pd.DataFrame from the positions.
df_port = pd.DataFrame(positions)
print("The following portfolio will be stamped:")
pprint.pprint(df_port)
# Prompt user to confirm with a "yes"/"no" or "y"/"n".
# with the default option set to "yes" or "y".
if input("Stamp this portfolio? (yes/no) [y]: ").lower() not in ["yes", "y", ""]:
    print("Exiting.")
    exit(0)


# ## Save the Portfolio CSV

# First, save to a buffer we will write to S3.
csv_buffer = StringIO()
df_port.to_csv(csv_buffer, index=False)
str_csv = csv_buffer.getvalue()
print("The following portfolio will be saved:")
print(str_csv)

# Save portfolio CSV to an S3 bucket.
# This sample uses an S3 bucket to store and share the portfolio CSV.
# You can use any other storage service or method.

"""
The following environment variables should be set to use S3:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_S3_BUCKET_NAME
AWS_S3_FOLDER_NAME
"""

# The following function uses AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# environment variables to create an S3 client.
s3_client = create_s3_client_from_env()
if s3_client is None:
    raise Exception(
        "Failed to connect to S3. "
        "Make sure valid AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are set."
    )

# Load the S3 environment variables specifying the bucket and folder.
bucket_name = get_env_var_or_fail("AWS_S3_BUCKET_NAME")
folder_name = get_env_var_or_fail("AWS_S3_FOLDER_NAME")

# Get current timestamp as a string.
str_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# We will save the portfolio CSV to a file with the timestamp suffix.
file_name = f"port_{str_timestamp}.csv"

# Save the portfolio CSV to the S3 bucket.
boto3_receipt = write_s3_object(s3_client, bucket_name, folder_name, file_name, str_csv)
if boto3_receipt is None or boto3_receipt["ResponseMetadata"]["HTTPStatusCode"] != 200:
    raise Exception(f"Failed to save portfolio CSV to S3: {boto3_receipt}")
print(f"Saved CSV: {file_name}")


# ## Commit the Portfolio CSV to vBase

# Connect to vBase.
# The following function uses
# VBASE_FORWARDER_URL, VBASE_API_KEY, and VBASE_COMMITMENT_SERVICE_PRIVATE_KEY
# environment variables to create a vBase client.
vbc = VBaseClient.create_instance_from_env()
if vbc.commitment_service is None:
    raise Exception(
        "Failed to connect to vBase. "
        "Make sure valid VBASE_FORWARDER_URL, VBASE_API_KEY, "
        "and VBASE_COMMITMENT_SERVICE_PRIVATE_KEY environment variables are set."
    )

# Load the dataset (strategy) name from the environment variables.
vbase_dataset_name = get_env_var_or_fail("VBASE_DATASET_NAME")

# Create the vBase dataset object for the strategy.
# This operation is idempotent.
# If the dataset already exists, no additional commitments will be made.
ds_strategy = VBaseDataset(vbc, vbase_dataset_name, VBaseStringObject)
print(f"Created dataset: {pprint.pformat(ds_strategy.to_dict())}")

receipt = ds_strategy.add_record(str_csv)
print(f"Stamp receipt: {pprint.pformat(receipt)}")

print("Done.")
