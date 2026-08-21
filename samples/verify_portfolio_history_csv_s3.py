# %% [markdown]
# # Verify a CSV Portfolio History from S3
#
# Verify exact CSV portfolio bytes and derive history from stamp timestamps.
# %%

from io import BytesIO
import os

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

EXPECTED_RECORD_COUNT = 5
S3_PREFIX = "vbase-samples/portfolio-history-csv"


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
        f"{collection_prefix}/portfolio_{period:02d}.csv"
        for period in range(EXPECTED_RECORD_COUNT)
    ]
    validate_s3_object_keys(s3_objects, expected_keys, "CSV portfolio history")

    records = []
    for object_key, record_bytes in s3_objects:
        portfolio_frame = pd.read_csv(BytesIO(record_bytes))
        if list(portfolio_frame.columns) != ["sym", "wt"]:
            raise ValueError(f"Expected sym,wt columns in {object_key}.")
        if portfolio_frame["sym"].duplicated().any():
            raise ValueError(f"Expected unique symbols in {object_key}.")
        records.append(
            {
                "object_key": object_key,
                "data": portfolio_frame,
                "object_cid": get_cid_for_bytes(record_bytes),
            }
        )

    object_cids = [record["object_cid"] for record in records]
    if len({cid.lower() for cid in object_cids}) != len(object_cids):
        raise RuntimeError("The CSV portfolio history contains duplicate record CIDs.")

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

    portfolio_history_frame = pd.concat(
        [
            record["data"].assign(
                timestamp=pd.Timestamp(
                    receipts_by_cid[record["object_cid"].lower()].timestamp
                )
            )[["timestamp", "sym", "wt"]]
            for record in records
        ],
        ignore_index=True,
    )
    print(portfolio_history_frame)

    strategy_frame = portfolio_history_frame.pivot(
        index="timestamp",
        columns="sym",
        values="wt",
    ).sort_index()
    strategy_frame.columns.name = None
    strategy_frame.index.name = "timestamp"
    print(strategy_frame)

    print("Every expected CSV portfolio record has a matching vBase stamp.")
