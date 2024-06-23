# # Track Record Verification Demo

"""This sample verifies a tamper-proof portfolio track record.
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

# The strategy owner address.
STRATEGY_OWNER = "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C"

# The strategy name.
STRATEGY_NAME = "strategy20240618145216"

# Additional configuration.
BUCKET_NAME = "vbase-test"
FOLDER_NAME = "samples/portfolio_history/"
STRATEGY_FOLDER_NAME = FOLDER_NAME + STRATEGY_NAME


# ## Setup

# Load the information necessary to call vBase APIs.
assert load_dotenv(verbose=True, override=True)

# Connect to AWS.
boto_client = create_s3_client_from_env()

# Connect to vBase.
vbc = VBaseClient.create_instance_from_env()

# Initialize the strategy dataset object.
ds_strategy = VBaseDataset(
    vbc,
    init_dict={
        "name": STRATEGY_NAME,
        "owner": STRATEGY_OWNER,
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


# ## Validate the Portfolio History

# Load the portfolio records.
ds_strategy = init_vbase_dataset_from_s3_objects(
    ds_strategy, boto_client, BUCKET_NAME, STRATEGY_FOLDER_NAME
)

# Restore timestamps using the blockchain stamps.
assert ds_strategy.try_restore_timestamps_from_index()

# Verify the portfolio records.
assert ds_strategy.verify_commitments()

# Build and display the verified portfolio records.
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


# ## Display Portfolio Analytics

# Convert strategy data to a Pandas DataFrame.
df_strategy = ds_strategy.get_pd_data_frame()
print("Strategy DataFrame:\n", df_strategy)

# Plot validated strategy return.
random.seed(1)
df_asset_returns = pd.DataFrame(
    (np.random.random(size=df_strategy.shape) * 2 - 1) / 20,
    index=df_strategy.index,
    columns=df_strategy.columns,
)
df_strategy_returns = (df_strategy.shift(1) * df_asset_returns).sum(axis=1)
print("\nReturns DataFrame:\n", df_strategy_returns)
(1 + df_strategy_returns).cumprod().fillna(1).plot()
plt.show()


# ## Summary

"""Process
* We used only a link to the portfolio history, strategy name and owner.
* We validated data integrity and timestamps using public blockchain records.
* We converted the historical data to a Pandas DataFrame for easy analysis.
"""

"""Key Implications
* The track record and all analytics can be independently calculated and verified forever.
* Data can be validated with a single line.
* vBase integrates smoothly with existing data science libraries and workflows.
"""
