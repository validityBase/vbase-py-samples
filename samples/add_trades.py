# # add_trades_parallel

"""This sample creates a strategy comprising JSON trade records
stored in an S3 bucket.
"""


# ## Imports

from datetime import datetime
import json
import os
import pprint
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import matplotlib.pyplot as plt

from vbase import (
    VBaseClient,
    ForwarderCommitmentService,
    VBaseDataset,
    VBaseJsonObject,
)

from samples.aws_utils import (
    create_s3_client_from_env,
    write_s3_object,
)


# ## Configuration

# Post 10 sample trades.
N_TRADES = 10

# Use hardcoded test account for the example.
pk = "0xabfc6c981e4e9f1f26175bc40aef73248d467617309c5e04e83da34171999076"
address = "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C"

# S3 bucket for the test data.
BUCKET_NAME = "vbase-test"

# Name of the source S3 folder for the dataset records.
FOLDER_NAME = f"add_trades/"

# Define the strategy name.
STRATEGY_NAME = f"strategy" + datetime.now().strftime("%Y%m%d%H%M%S")
STRATEGY_FOLDER_NAME = f"{FOLDER_NAME}{STRATEGY_NAME}/"

# Check if the script is running in an interactive mode or a Jupyter notebook.
if "ipykernel" not in sys.modules and "IPython" in sys.modules:
    # The following line creates overactive warning.
    # We want the import within the clause.
    # pylint: disable=ungrouped-imports
    import matplotlib

    # Set plot backend to WebAgg.
    # This backend provides interactive web charts.
    matplotlib.use("WebAgg")


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
        pk,
    )
)


# ## Create the Strategy Dataset

# Create the vBase dataset object for the strategy.
# TODO: Uncomment
# ds_strategy = VBaseDataset(vbc, STRATEGY_NAME, VBaseJsonObject)
# print(f"Created dataset: {pprint.pformat(ds_strategy.to_dict())}")


# ## Create and Stamp Trades

# Create a set of pseudorandom trades using a reproducible seed.
random.seed(1234)
for i_trade in range(N_TRADES):
    # Create a random trade in [-1, 1].
    trade = json.dumps(
        {
            "trade_id": i_trade,
            "symbol": "ETHUSD",
            "size": round(random.random() * 2 - 1, 2),
        }
    )
    print(f"Created trade: {pprint.pformat(trade)}")
    # Save the trade.
    write_s3_object(
        boto_client, BUCKET_NAME, STRATEGY_FOLDER_NAME, f"trade_{i_trade}.json", trade
    )
    # Add trade to the vBase dataset object.
    # TODO: Uncomment
    # receipt = ds_strategy.add_record(trade)
    # print(f"Stamp receipt: {pprint.pformat(receipt)}")


# ## Display the Trade URL

print(
    "Data saved to: "
    "http://vbase-test.s3-website-us-east-1.amazonaws.com/?prefix="
    f"{STRATEGY_FOLDER_NAME}"
)
