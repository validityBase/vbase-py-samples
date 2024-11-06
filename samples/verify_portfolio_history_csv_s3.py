# # Track Record Verification Demo

"""This sample verifies a tamper-proof portfolio track record.
"""


# ## Imports

import pprint
import sys
from dotenv import load_dotenv

from vbase import (
    VBaseClient,
    VBaseDataset,
)

from aws_utils import (
    create_s3_client_from_env,
    read_s3_object,
    init_vbase_dataset_from_long_csv,
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
        "record_type_name": "VBaseStringObject",
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

# Load the long portfolio history CSV.
csv_ports_long = read_s3_object(
    boto_client,
    BUCKET_NAME,
    STRATEGY_FOLDER_NAME,
    "portfolio_long.csv",
)
print("Strategy long CSV:\n", csv_ports_long)

# Load the portfolio records.
ds_strategy = init_vbase_dataset_from_long_csv(ds_strategy, csv_ports_long)

# Restore timestamps using the blockchain stamps.
assert ds_strategy.try_restore_timestamps_from_index()

# Verify the portfolio records.
assert ds_strategy.verify_commitments()

# Build and display the verified portfolio records.
l_receipts = ds_strategy.get_commitment_receipts()
html = (
    "<table>"
    + "<tr><th>num</th><th>portfolio</th><th>portfolio_hash</th><th>tx</th></tr>"
)
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


# ## Summary

"""Process
* We used only a link to the portfolio history, strategy name and owner.
* We validated data integrity and timestamps using public blockchain records.
* We converted the long CSV to a series of verified timestamped records.
"""

"""Key Implications
* The track record and all analytics can be independently calculated and verified forever.
* Data can be validated with a single line.
* vBase integrates smoothly with existing data science libraries and workflows.
"""
