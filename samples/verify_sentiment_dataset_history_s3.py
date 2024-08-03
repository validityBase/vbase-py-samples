# # Sentiment Dataset Verification Demo

"""This sample verifies a tamper-proof dataset history.
"""


# ## Imports

import pprint
import random
import sys
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from vbase import (
    VBaseClient,
    VBaseDataset,
)
from aws_utils import (
    create_s3_client_from_env,
    init_vbase_dataset_from_s3_objects,
)


# ## Configuration

# The dataset owner address.
DATASET_OWNER = "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C"

# The dataset name.
DATASET_NAME = "sentiment_dataset_20240620103503"

# Additional configuration.
BUCKET_NAME = "vbase-test"
FOLDER_NAME = "samples/sentiment_dataset_history/"
DATASET_FOLDER_NAME = FOLDER_NAME + DATASET_NAME


# ## Setup

# Load the information necessary to call vBase APIs.
assert load_dotenv(verbose=True, override=True)

# Connect to AWS.
boto_client = create_s3_client_from_env()

# Connect to vBase.
vbc = VBaseClient.create_instance_from_env()

# Initialize the dataset object.
ds = VBaseDataset(
    vbc,
    init_dict={
        "name": DATASET_NAME,
        "owner": DATASET_OWNER,
        "record_type_name": "VBaseJsonObject",
        "records": [],
    },
)

# Additional Setup.
if "ipykernel" not in sys.modules and "IPython" in sys.modules:
    # Configure plot backend if running in interactive mode.
    # The following line creates overactive warning.
    # We want the import within the clause.
    # pylint: disable=ungrouped-imports
    import matplotlib

    # Set plot backend to WebAgg.
    # This backend provides interactive web charts.
    matplotlib.use("WebAgg")


# ## Validate the Dataset History

# Load the dataset records.
ds = init_vbase_dataset_from_s3_objects(
    ds, boto_client, BUCKET_NAME, DATASET_FOLDER_NAME
)

# Restore timestamps using the blockchain stamps.
assert ds.try_restore_timestamps_from_index()

# Verify the records.
assert ds.verify_commitments()

# Build and display the verified records.
l_receipts = ds.get_commitment_receipts()
html = "<table>"
html += "<tr><th>num</th><th>record</th><th>record_hash</th><th>tx</th></tr>"
# Populate the table with data.
for i, record in enumerate(ds.records):
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


# ## Display Analytics

# Convert dataset data to a Pandas DataFrame.
df_dataset = ds.get_pd_data_frame()
print("Dataset DataFrame:\n", df_dataset)

# Convert data to a signal.
df_signal = (df_dataset - 50) / 50
print("Signal DataFrame:\n", df_signal)

# Plot validated signal return.
random.seed(1)
df_asset_returns = pd.DataFrame(
    (np.random.random(size=df_signal.shape) * 2 - 1) / 20,
    index=df_signal.index,
    columns=df_signal.columns,
)
df_signal_returns = (df_signal.shift(1) * df_asset_returns).sum(axis=1)
print("\nReturns DataFrame:\n", df_signal_returns)
(1 + df_signal_returns).cumprod().fillna(1).plot()
plt.show()


# ## Summary

"""Process
* We used only a link to the dataset history, name and owner.
* We validated data integrity and timestamps using public blockchain records.
* We converted the historical data to a Pandas DataFrame for easy analysis.
"""

"""Key Implications
* The track record and all analytics can be independently calculated and verified forever.
* Data can be validated with a single line.
* vBase integrates smoothly with existing data science libraries and workflows.
"""
