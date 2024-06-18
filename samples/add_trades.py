# # add_trades

"""This sample creates a strategy comprising JSON trade records
and verifies the strategy.
"""

from datetime import datetime
import json
import pprint
import time

from vbase import (
    VBaseClient,
    VBaseDataset,
    VBaseJsonObject,
)


# ## Configuration

# Name for the strategy to create.
# Use a test dataset name that is unique and will not collide with other tests.
STRATEGY_NAME = "strategy_" + datetime.now().strftime("%Y%m%d%H%M%S")


# ## Setup

# Initialize vBase using environment variables.
vbc = VBaseClient.create_instance_from_env()

# Create the vBase dataset object.
ds = VBaseDataset(vbc, STRATEGY_NAME, VBaseJsonObject)
print(f"Created dataset: {STRATEGY_NAME}")


# ## Post Trades

trades = []
receipts = []
start_time = time.time()
for i in range(10):
    trade = json.dumps(
        {
            "tade_id": i,
            "symbol": "ETHUSD",
            "size": 1 if i % 2 == 0 else -1,
        }
    )
    trades.append(trade)
    receipt = ds.add_record(trade)
    print(f"Posted trade: {pprint.pformat(receipt)}")
    receipts.append(receipt)
elapsed_time = time.time() - start_time
print(f"Posting trades took {elapsed_time} seconds.")
print(f"TPS: {10 / elapsed_time}")


# ## Validate Trades

# Find the commitment receipts for the strategy.
# Note that this operation queries the blockchain for
# commitment transaction and timestamps, and verifies data integrity
# without relying on the user's cooperation.
# First, we will create a copy dataset to be validated by the consumer.
ds_dict = ds.to_dict()
ds_dict = {k: ds_dict[k] for k in ["name", "owner", "record_type_name", "records"]}
print(
    f"Initialize validation strategy dataset using the following data:\n{pprint.pformat(ds_dict)}"
)

ds_copy = VBaseDataset(vbc, init_dict=ds_dict)
print(f"Copy dataset before timestamp validation:\n{pprint.pformat(ds_copy.to_dict())}")

# Get commitment receipts for the dataset's records.
commitment_receipts = ds_copy.get_commitment_receipts()
print(f"Commitment receipts: {pprint.pformat(commitment_receipts)}")

# Display the validated dataset.
ds_copy.try_restore_timestamps_from_index()
print(f"Copy dataset after timestamp validation:\n{pprint.pformat(ds_copy.to_dict())}")

# Display the validated dataset as DataFrame suitable for portfolio analysis.
df = ds_copy.get_pd_data_frame()
print(f"Strategy DataFrame:\n{pprint.pformat(df)}")

# Plot the cumulative strategy return
# using a fictional return series.
df["wt"] = df["size"].cumsum()
returns = [0.01, -0.02, 0.03, -0.01, 0.02, -0.03, 0.015, -0.01, 0.025, -0.02]
(1 + df["wt"] * returns).cumprod().plot()
