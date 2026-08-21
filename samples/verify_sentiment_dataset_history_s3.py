# %% [markdown]
# # Verify a Sentiment Dataset History from S3
#
# Verify exact sentiment bytes against one vBase collection and owner.
# %%

import json
import os

import numpy as np
import pandas as pd

from aws_utils import (
    create_s3_client_from_env,
    read_s3_objects,
    validate_s3_object_keys,
)
from utils import (
    create_vbase_client_from_env,
    get_cid_for_bytes,
    get_collection_by_cid,
    get_env_var_or_fail,
    wait_for_stamps,
)

EXPECTED_RECORD_COUNT = 10
S3_PREFIX = "vbase-samples/sentiment-history"


# %% [markdown]
# ## Load exact bytes and verify every expected record
# %%
s3_client = create_s3_client_from_env()
bucket_name = get_env_var_or_fail("AWS_S3_BUCKET")
collection_cid = get_env_var_or_fail("VBASE_COLLECTION_CID")

with create_vbase_client_from_env() as client:
    owner_address = (
        os.getenv("VBASE_OWNER_ADDRESS") or client.get_current_user().last_address
    )
    if not owner_address:
        raise RuntimeError("Set VBASE_OWNER_ADDRESS or configure an account address.")

    collection = get_collection_by_cid(client, collection_cid, owner_address)
    collection_prefix = f"{S3_PREFIX}/{collection.cid}"
    s3_objects = read_s3_objects(s3_client, bucket_name, collection_prefix)
    expected_keys = [
        f"{collection_prefix}/record_{period:02d}.json"
        for period in range(EXPECTED_RECORD_COUNT)
    ]
    validate_s3_object_keys(s3_objects, expected_keys, "sentiment history")

    records = []
    for object_key, record_bytes in s3_objects:
        sentiment = json.loads(record_bytes.decode("utf-8"))
        if not isinstance(sentiment, dict):
            raise ValueError(f"Expected a JSON object in {object_key}.")
        records.append(
            {
                "object_key": object_key,
                "data": sentiment,
                "object_cid": get_cid_for_bytes(record_bytes),
            }
        )

    object_cids = [record["object_cid"] for record in records]
    if len({cid.lower() for cid in object_cids}) != len(object_cids):
        raise RuntimeError("The sentiment history contains duplicate record CIDs.")

    receipts_by_cid = wait_for_stamps(
        client,
        object_cids,
        collection.cid,
        user_address=owner_address,
    )
    verification_frame = pd.DataFrame(
        [
            {
                "object_key": record["object_key"],
                "object_cid": record["object_cid"],
                "timestamp": receipts_by_cid[record["object_cid"].lower()].timestamp,
                "transaction_hash": receipts_by_cid[
                    record["object_cid"].lower()
                ].transaction_hash,
            }
            for record in records
        ]
    )
    print(verification_frame)

    dataset_frame = pd.DataFrame(
        [record["data"] for record in records],
        index=pd.to_datetime(
            [
                receipts_by_cid[record["object_cid"].lower()].timestamp
                for record in records
            ],
            utc=True,
        ),
    ).sort_index()
    dataset_frame.index.name = "timestamp"
    signal_frame = (dataset_frame - 50) / 50
    print(signal_frame)

    random_generator = np.random.default_rng(1)
    asset_returns = pd.DataFrame(
        (random_generator.random(size=signal_frame.shape) * 2 - 1) / 20,
        index=signal_frame.index,
        columns=signal_frame.columns,
    )
    signal_returns = (signal_frame.shift(1) * asset_returns).sum(axis=1)
    (1 + signal_returns).cumprod().fillna(1).plot()

    print("Every expected sentiment record has a matching vBase stamp.")
