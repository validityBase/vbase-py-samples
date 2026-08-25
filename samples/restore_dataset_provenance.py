# %% [markdown]
# # Restore Dataset Provenance after an S3 Copy
#
# Recover trusted record timestamps after S3 copy metadata has changed.
# %%

from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd

from aws_utils import (
    copy_s3_prefix,
    create_s3_client_from_env,
    list_s3_objects,
    print_s3_objects,
    read_s3_object,
    write_s3_object,
)
from utils import (
    create_vbase_client_from_env,
    get_cid_for_bytes,
    get_env_var_or_fail,
    wait_for_stamps,
)

N_RECORDS = 5
S3_PREFIX = "vbase-samples/provenance-restoration"
RUN_ID = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"
COLLECTION_NAME = f"Python Provenance Restoration {RUN_ID}"
COLLECTION_DESCRIPTION = "Records used to demonstrate provenance after an S3 copy."


# %% [markdown]
# ## Create, copy, and verify the records
# %%
s3_client = create_s3_client_from_env()
bucket_name = get_env_var_or_fail("AWS_S3_BUCKET")

with create_vbase_client_from_env() as client:
    collection = client.create_collection(
        name=COLLECTION_NAME,
        description=COLLECTION_DESCRIPTION,
    )
    owner_address = client.get_current_user().last_address
    if not owner_address:
        raise RuntimeError("The current vBase account does not have an owner address.")

    source_prefix = f"{S3_PREFIX}/{collection.cid}/source"
    copy_prefix = f"{S3_PREFIX}/{collection.cid}/copy"
    source_cids = []

    for value in range(1, N_RECORDS + 1):
        record_bytes = str(value).encode("utf-8")
        object_cid = get_cid_for_bytes(record_bytes)
        write_s3_object(
            s3_client,
            bucket_name,
            source_prefix,
            f"record_{value:02d}.txt",
            record_bytes,
        )
        stamp = client.create_stamp(
            data_cid=object_cid,
            collection_cid=collection.cid,
            store_stamped_file=False,
            idempotent=True,
            idempotency_window=0,
        )
        if stamp.commitment_receipt.object_cid.lower() != object_cid.lower():
            raise RuntimeError("vBase returned a different CID than the stamped bytes.")
        source_cids.append(object_cid)

    source_receipts = wait_for_stamps(
        client,
        source_cids,
        collection.cid,
        user_address=owner_address,
    )
    print("Source objects:")
    print_s3_objects(s3_client, bucket_name, source_prefix)

    copied_keys = copy_s3_prefix(
        s3_client,
        bucket_name,
        source_prefix,
        bucket_name,
        copy_prefix,
    )
    if len(copied_keys) != N_RECORDS:
        raise RuntimeError(
            f"Expected {N_RECORDS} copied records, found {len(copied_keys)}."
        )

    print("Copied objects with new S3 metadata:")
    print_s3_objects(s3_client, bucket_name, copy_prefix)

    copied_objects = list_s3_objects(s3_client, bucket_name, copy_prefix)
    copied_records = []
    for item in copied_objects:
        record_bytes = read_s3_object(s3_client, bucket_name, item["Key"])
        copied_records.append(
            {
                "object_key": item["Key"],
                "storage_timestamp": item["LastModified"],
                "object_cid": get_cid_for_bytes(record_bytes),
                "value": int(record_bytes.decode("utf-8")),
            }
        )

    copied_cids = [record["object_cid"] for record in copied_records]
    if len({cid.lower() for cid in copied_cids}) != len(copied_cids):
        raise RuntimeError("The copied history contains duplicate record CIDs.")
    if {cid.lower() for cid in copied_cids} != {cid.lower() for cid in source_cids}:
        raise RuntimeError(
            "The copied record bytes differ from the stamped source records."
        )

    restored_receipts = wait_for_stamps(
        client,
        copied_cids,
        collection.cid,
        user_address=owner_address,
    )
    provenance_frame = pd.DataFrame(
        [
            {
                **record,
                "stamp_timestamp": restored_receipts[
                    record["object_cid"].lower()
                ].timestamp,
            }
            for record in copied_records
        ]
    ).sort_values("stamp_timestamp")

    if set(restored_receipts) != set(source_receipts):
        raise RuntimeError("The restored receipts do not match the source receipts.")

    print(provenance_frame)
    print(f"Collection CID: {collection.cid}")
    print(f"Owner address: {owner_address}")
    print("The copied records were verified and their stamp timestamps restored.")
