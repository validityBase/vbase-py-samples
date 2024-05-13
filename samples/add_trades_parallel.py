# # add_trades

"""This sample creates a strategy comprising JSON trade records
and verifies the strategy.
"""

from datetime import datetime
from dotenv import load_dotenv
import json
import os
import pprint
import random
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from vbase import (
    VBaseClient,
    ForwarderCommitmentService,
    VBaseDataset,
    VBaseJsonObject,
)

from samples.aws_utils import (
    create_s3_client_from_env,
    create_s3_objects_from_dataset,
    init_vbase_dataset_from_s3_objects,
)


# ## Configuration

# The sample uses 5 users, 2 strategies per user,
# and 10 trades per strategy.
N_USERS = 5
N_TRADES = 10

# Use hardcoded test accounts for the example.
# Each account is a PK, address tuple.
l_accounts = [
    {
        "pk": "0xabfc6c981e4e9f1f26175bc40aef73248d467617309c5e04e83da34171999076",
        "address": "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C",
    },
    {
        "pk": "0x422043f88fbd2f605f0237512e090032ad90c0a5583df4a189f446ab7abf779a",
        "address": "0xEe8633d1fC69d045442Da84f08DF49C48826b163",
    },
    {
        "pk": "0x321c704b7edbeec46a1200f6862548604ba255e2c1f7dd08e9c1d18fcfc0cfb9",
        "address": "0x7e3CB5Bc50E1864b3Dc863299b4A4269D12928f1",
    },
    {
        "pk": "0x7d0776af9f1eac044e9d390a84a9a3608350ebce036bc0215e6b19c77d51f700",
        "address": "0xcd9b43102E26d3191a7a76eA98dF858daa1e34Ae",
    },
    {
        "pk": "0x63716eb43c9a84224715bcf5dd901e9dd3100791526dc65993898c0a676ffa68",
        "address": "0xd991dc481319fb3C93fe01d124a4ae0b197FcB8B",
    },
]

# S3 bucket for the test data.
BUCKET_NAME = "vbase-test"

# Name of the source S3 folder for the dataset records.
FOLDER_NAME = "add_trades_parallel/"


# ## Setup

# Create a VBaseClient object for each strategy.
load_dotenv(verbose=True, override=True)
forwarder_url = os.environ.get("VBASE_FORWARDER_URL")
api_key = os.environ.get("VBASE_API_KEY")

# Create an AWS client using environment variables.
boto_client = create_s3_client_from_env()

# Create strategy data.
# This is the data users will be using to post trades.
# We will simulate multiple users and strategies using multiple threads,
# with each thread using a given strategy dataset.
l_starts = []
for i_user in range(N_USERS):
    vbc = VBaseClient(
        ForwarderCommitmentService(
            forwarder_url,
            api_key,
            l_accounts[i_user]["pk"],
        )
    )
    strategy_data = {
        "name": (f"user{i_user}_strategy" + datetime.now().strftime("%Y%m%d%H%M%S")),
        "address": l_accounts[i_user]["address"],
        "vbc": vbc,
    }
    l_starts.append(strategy_data)

print(f"Created users and strategies:\n{pprint.pformat(l_starts)}")


# ## Create Strategy Datasets


def create_strategy_dataset(i_strat):
    """
    Create the strategy dataset

    :param i_strat: Strategy index
    """
    # Create the vBase dataset object.
    ds = VBaseDataset(
        l_starts[i_strat]["vbc"], l_starts[i_strat]["name"], VBaseJsonObject
    )
    print(f"Created dataset: {ds}")
    return ds


with ThreadPoolExecutor(max_workers=len(l_starts)) as executor:
    results = executor.map(create_strategy_dataset, range(len(l_starts)))
l_datasets = [ds for ds in results]


# ## Post Trades


def post_strategy_trades(i_strat):
    """
    Post trades for a strategy

    :param i_strat: Strategy index
    """
    trades = []
    receipts = []
    # Create a set of pseudorandom trades with a reproducible seed.
    random.seed(i_strat)
    for i_trade in range(N_TRADES):
        trade = json.dumps(
            {
                "tade_id": i_trade,
                "symbol": "ETHUSD",
                # Create a random trade in [-1, 1].
                "size": random.random() * 2 - 1,
            }
        )
        trades.append(trade)
        receipt = l_datasets[i_strat].add_record(trade)
        print(f"Posted trade: {pprint.pformat(receipt)}")
        receipts.append(receipt)
    return trades, receipts


start_time = time.time()
with ThreadPoolExecutor(max_workers=len(l_starts)) as executor:
    results = executor.map(post_strategy_trades, range(len(l_starts)))
elapsed_time = time.time() - start_time
l_trades, l_receipts = zip(*results)
print(f"Posting trades took {elapsed_time} seconds.")
print(f"TPS: {N_USERS * N_TRADES / elapsed_time}")

# Save all the posted trades.
for ds in l_datasets:
    print(f"Saving dataset: {ds.name}")
    create_s3_objects_from_dataset(
        ds, boto_client, BUCKET_NAME, FOLDER_NAME
    )

# Display saved data using the shell.
for ds in l_datasets:
    print(f"Displaying S3 objects for dataset: {ds.name}")
    for i in range(len(ds.records)):
        command = f"curl https://vbase-test.s3.amazonaws.com/add_trades_parallel/{ds.name}/obj_{i}.json"
        print(command)
        process = subprocess.run(command, shell=True, text=True, capture_output=True)
        print(process.stdout)


# ## Validate Trades

# Create a strategy dataset to validate.
# This is done on the consumer/validator machine
# using data specified by the producer/prover.
ds_consumer = VBaseDataset(
    vbc=VBaseClient(
        ForwarderCommitmentService(
            forwarder_url,
            api_key
        )
    ),
    init_dict={
        "name": "user0_strategy20240512224826",
        "owner": "0xA401F59d7190E4448Eb60691E3bc78f1Ef03e88C",
        "record_type_name": "VBaseJsonObject",
        "records": [],
    }
)

# Load dataset records from the bucket.
init_vbase_dataset_from_s3_objects(
    ds_consumer,
    boto_client,
    BUCKET_NAME,
    FOLDER_NAME + ds_consumer.name
)
print(f"Consumer dataset before timestamp validation:\n{pprint.pformat(ds_consumer.to_dict())}")

# Restore timestamps using commitments and display the validated dataset.
ds_consumer.try_restore_timestamps_from_index()
print(f"Copy dataset after timestamp validation:\n{pprint.pformat(ds_consumer.to_dict())}")

# Plot the cumulative strategy return
# using a fictional return series.
df = ds_consumer.get_pd_data_frame()
print("Strategy DataFrame:\n", df)
df["wt"] = df["size"].cumsum()
random.seed(1)
returns = [(random.random() * 2 - 0.9) / 100 for i in range(df.shape[0])]
(1 + df["wt"] * returns).cumprod().plot()
