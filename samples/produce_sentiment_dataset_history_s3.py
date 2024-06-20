# # Sentiment Dataset Stamper Demo

"""This sample creates a tamper-proof dataset history.
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

# The producer's sovereign cryptographic identity.
PK = "0xabfc6c981e4e9f1f26175bc40aef73248d467617309c5e04e83da34171999076"

# The dataset name.
DATASET_NAME = "sentiment_dataset_" + datetime.now().strftime("%Y%m%d%H%M%S")

# Additional configuration.
BUCKET_NAME = "vbase-test"
N_TIME_PERIODS = 10
FOLDER_NAME = "sentiment_dataset/"
DATASET_FOLDER_NAME = FOLDER_NAME + DATASET_NAME
ADDRESS = "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C"


# ## Setup

# Load the information necessary to call vBase APIs.
load_dotenv(verbose=True, override=True)
forwarder_url = os.environ.get("VBASE_FORWARDER_URL")
api_key = os.environ.get("VBASE_API_KEY")

# Connect to AWS.
boto_client = create_s3_client_from_env()

# Connect to vBase.
vbc = VBaseClient(
    ForwarderCommitmentService(
        forwarder_url,
        api_key,
        PK,
    )
)


# ## Create and Stamp Records

# Create the vBase dataset object.
ds = VBaseDataset(vbc, DATASET_NAME, VBaseJsonObject)
print(f"Created dataset: {pprint.pformat(ds.to_dict())}")

# Create sample records.
random.seed(1234)
for i_record in range(N_TIME_PERIODS):
    # Create a random record in [0, 100].
    record = json.dumps(
        {
            "AAPL": round(random.random() * 100),
            "MSFT": round(random.random() * 100),
            "TSLA": round(random.random() * 100),
        }
    )
    print(f"Record: {pprint.pformat(record)}")

    # Add the record to the vBase dataset object.
    receipt = ds.add_record(record)
    print(f"Stamp receipt: {pprint.pformat(receipt)}")

    # Save the record.
    write_s3_object(
        boto_client,
        BUCKET_NAME,
        DATASET_FOLDER_NAME,
        f"record_{i_record}.json",
        record,
    )

# Display the shareable dataset history URL.
print(
    "Data saved to: "
    "http://vbase-test.s3-website-us-east-1.amazonaws.com/?prefix="
    f"{DATASET_FOLDER_NAME}"
)
print(f"Dataset info: name = {ds.name}, owner = {ds.owner}")

# ## Summary

"""Process
* We used only a private key and dataset records as inputs.
* We created a tamper-proof history of dataset records.
* Data was not shared with vBase or any other third party.
"""

"""Key Implications
* We can produce an easily verifiable dataset record.
* We can selectively share the dataset history.
* The record and all analytics can be independently calculated and verified forever.
"""
