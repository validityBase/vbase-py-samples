# # Strategy Stamper Demo

"""This sample creates a tamper-proof portfolio track record.
"""


# ## Imports

from datetime import datetime
import os
import pandas as pd
import pprint
import random
from dotenv import load_dotenv

from vbase import (
    VBaseClient,
    ForwarderCommitmentService,
    VBaseDataset,
    VBaseStringObject,
)

from aws_utils import (
    create_s3_client_from_env,
    write_s3_object,
)


# ## Configuration

# The trader's sovereign cryptographic identity.
PRIVATE_KEY = "0xabfc6c981e4e9f1f26175bc40aef73248d467617309c5e04e83da34171999076"

# The strategy name.
STRATEGY_NAME = "strategy" + datetime.now().strftime("%Y%m%d%H%M%S")

# Additional configuration.
BUCKET_NAME = "vbase-test"
N_TIME_PERIODS = 10
FOLDER_NAME = "samples/portfolio_history/"
STRATEGY_FOLDER_NAME = FOLDER_NAME + STRATEGY_NAME
ADDRESS = "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C"


# ## Setup

# Load the information necessary to call vBase APIs.
load_dotenv(verbose=True, override=True)
forwarder_url = os.environ.get("VBASE_FORWARDER_URL")
api_key = os.environ.get("VBASE_API_KEY")

# Connect to vBase.
vbc = VBaseClient(
    ForwarderCommitmentService(
        forwarder_url,
        api_key,
        PRIVATE_KEY,
    )
)

# Connect to AWS.
boto_client = create_s3_client_from_env()


# ## Create and Stamp Portfolios

# Create the vBase dataset object for the strategy.
ds_strategy = VBaseDataset(vbc, STRATEGY_NAME, VBaseStringObject)
print(f"Created dataset: {pprint.pformat(ds_strategy.to_dict())}")

# Create sample portfolios.
random.seed(1234)
for i_trade in range(N_TIME_PERIODS):
    # Create a random portfolio in [-1, 1].
    # We can use any identifier for which returns can be verified.
    port_csv = pd.DataFrame({
        "sym": ["SPY", "TSLA", "BTCUSD", "JPM:CDS:5"],
        "wt": [round(random.random() * 2 - 1, 2) for _ in range(4)]
    }).to_csv(index=False)
    print(f"Portfolio:\n{port_csv}")

    # Add the portfolio to the vBase dataset object.
    receipt = ds_strategy.add_record(port_csv)
    print(f"Stamp receipt: {pprint.pformat(receipt)}")

    # Save the portfolio.
    write_s3_object(
        boto_client,
        BUCKET_NAME,
        STRATEGY_FOLDER_NAME,
        f"portfolio_{i_trade}.csv",
        port_csv,
    )

# Display the shareable portfolio history URL.
print(
    "Data saved to: "
    "http://vbase-test.s3-website-us-east-1.amazonaws.com/?prefix="
    f"{STRATEGY_FOLDER_NAME}"
)
print(f"Strategy info: name = {ds_strategy.name}, owner = {ds_strategy.owner}")

# ## Summary

"""Process
* We used only a private key and portfolio weights as inputs.
* We created a tamper-proof history of portfolio records.
* Portfolio data was not shared with vBase or any other third party.
"""

"""Key Implications
* We can produce an easily verifiable track record.
* We can selectively share the portfolio history.
* The track record and all analytics can be independently calculated and verified forever.
"""
