# # verify_portfolio_history_s3

"""This sample verifies a strategy comprising
a history of JSON portfolio records stored in an S3 bucket.
"""


# ## Imports

import os
import pprint
import random
import sys
from dotenv import load_dotenv
import matplotlib.pyplot as plt

from vbase import (
    VBaseClient,
    VBaseDataset,
)

from aws_utils import (
    create_s3_client_from_env,
    init_vbase_dataset_from_s3_objects,
)


# ## Configuration

# Note that the data to verify is defined solely by the dataset name
# and the owner address.

# Define the strategy name.
STRATEGY_NAME = "strategy20240617231129"

# Define the strategy owner address.
STRATEGY_OWNER = "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C"

# S3 bucket for the test data.
BUCKET_NAME = "vbase-test"

# Name of the source S3 folder for the dataset records.
FOLDER_NAME = "add_trades/"

STRATEGY_FOLDER_NAME = FOLDER_NAME + STRATEGY_NAME


# ## Setup

# Load the information necessary to call vBase APIs.
load_dotenv(verbose=True, override=True)

# Create an AWS client using environment variables.
boto_client = create_s3_client_from_env()

# Connect to vBase.
vbc = VBaseClient.create_instance_from_env()


# ## Plot Setup

# Check if the script is running in an interactive mode or a Jupyter notebook.
if "ipykernel" not in sys.modules and "IPython" in sys.modules:
    # The following line creates overactive warning.
    # We want the import within the clause.
    # pylint: disable=ungrouped-imports
    import matplotlib

    # Set plot backend to WebAgg.
    # This backend provides interactive web charts.
    matplotlib.use("WebAgg")


# ## Validate Load the Portfolio Dataset

# Create a strategy dataset to validate.
# This is done on the consumer/validator machine
# using data specified by the producer/prover.
ds_strategy = VBaseDataset(
    vbc,
    init_dict={
        "name": STRATEGY_NAME,
        "owner": STRATEGY_OWNER,
        "record_type_name": "VBaseJsonObject",
        "records": [],
    },
)

# Load dataset records from the bucket.
init_vbase_dataset_from_s3_objects(
    ds_strategy, boto_client, BUCKET_NAME, STRATEGY_FOLDER_NAME
)
print(f"Dataset before timestamp validation:\n{pprint.pformat(ds_strategy.to_dict())}")


# ## Validate the Portfolio Dataset

# Restore timestamps using commitments and display the validated dataset.
ds_strategy.try_restore_timestamps_from_index()
print(f"Dataset after timestamp validation:\n{pprint.pformat(ds_strategy.to_dict())}")

# Start building the HTML table.
l_receipts = ds_strategy.get_commitment_receipts()
html = "<table>"
html += "<tr><th>num</th><th>portfolio</th><th>portfolio_hash</th><th>tx</th></tr>"
# Populate the table with data.
for i, record in enumerate(ds_strategy.records):
    html += (
        f"<tr><td>{i}</td><td>{record.data}</td><td>{record.cid}</td>"
        f"<td>{l_receipts[i]['transactionHash']}</td></tr>"
    )
html += "</table>"

# Check if the script is running in an interactive mode or a Jupyter notebook.
if "ipykernel" not in sys.modules and "IPython" in sys.modules:
    pprint.pprint(html)
else:
    # Load support for HTML display, if necessary.
    from IPython.display import display, HTML

    # Display the HTML table in the Jupyter notebook.
    display(HTML(html))


# ## Print Portfolio Analytics

# Plot the cumulative strategy return
# using a fictional return series.
df = ds_strategy.get_pd_data_frame()
print("Strategy DataFrame:\n", df)
random.seed(1)
asset_returns = [(random.random() * 2 - 1) / 100 for i in range(df.shape[0])]
df["returns"] = df["size"] * asset_returns
print("\nReturns DataFrame:\n", df["returns"])
(1 + df["returns"]).cumprod().shift(1).fillna(1).plot()
plt.show()
