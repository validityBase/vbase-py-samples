# # produce_portfolio_history_s3

"""This sample creates a strategy comprising
a history of JSON portfolio records stored in an S3 bucket.
"""


# ## Imports

from datetime import datetime
import json
import os
import pprint
import random
from dotenv import load_dotenv

from vbase import (
    VBaseClient,
    ForwarderCommitmentService,
    VBaseDataset,
    VBaseJsonObject,
)

from aws_utils import (
    create_s3_client_from_env,
    write_s3_object,
)


# ## Configuration

# The number of target allocations, or portfolios, in the portfolio history.
N_TRADES = 10

# Use hardcoded test account for the example.
PK = "0xabfc6c981e4e9f1f26175bc40aef73248d467617309c5e04e83da34171999076"
ADDRESS = "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C"

# S3 bucket for the test data.
BUCKET_NAME = "vbase-test"

# Name of the source S3 folder for the dataset records.
FOLDER_NAME = "add_trades/"

# Define the strategy name.
STRATEGY_NAME = "strategy" + datetime.now().strftime("%Y%m%d%H%M%S")
STRATEGY_FOLDER_NAME = FOLDER_NAME + STRATEGY_NAME


# ## Setup

# Load the information necessary to call vBase APIs.
load_dotenv(verbose=True, override=True)
forwarder_url = os.environ.get("VBASE_FORWARDER_URL")
api_key = os.environ.get("VBASE_API_KEY")

# Create an AWS client using environment variables.
boto_client = create_s3_client_from_env()

# Connect to vBase.
vbc = VBaseClient(
    ForwarderCommitmentService(
        forwarder_url,
        api_key,
        PK,
    )
)


# ## Create the Strategy Dataset

# Create the vBase dataset object for the strategy.
ds_strategy = VBaseDataset(vbc, STRATEGY_NAME, VBaseJsonObject)
print(f"Created dataset: {pprint.pformat(ds_strategy.to_dict())}")


# ## Create and Stamp Portfolios

# Create a set of pseudorandom portfolios using a reproducible seed.
random.seed(1234)
for i_trade in range(N_TRADES):
    # Create a random portfolio in [-1, 1].
    port = json.dumps(
        {
            "symbol": "ETHUSD",
            "size": round(random.random() * 2 - 1, 2),
        }
    )
    print(f"Added portfolio: {pprint.pformat(port)}")
    # Add portfolio to the vBase dataset object.
    receipt = ds_strategy.add_record(port)
    print(f"Stamp receipt: {pprint.pformat(receipt)}")
    # Save the portfolio.
    write_s3_object(
        boto_client, BUCKET_NAME, STRATEGY_FOLDER_NAME, f"trade_{i_trade}.json", port
    )


# ## Display the S3 URL

print(
    "Data saved to: "
    "http://vbase-test.s3-website-us-east-1.amazonaws.com/?prefix="
    f"{STRATEGY_FOLDER_NAME}"
)

print(f"Strategy info: name = {ds_strategy.name}, owner = {ds_strategy.owner}")
