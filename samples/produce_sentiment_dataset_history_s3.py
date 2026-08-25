# %% [markdown]
# # Produce a Sentiment Dataset History in S3
#
# Stamp exact sentiment record bytes privately and store them in Amazon S3.
# %%

from datetime import datetime, timezone
import json
import random
from uuid import uuid4

from aws_utils import create_s3_client_from_env, write_s3_object
from utils import (
    create_vbase_client_from_env,
    get_cid_for_bytes,
    get_env_var_or_fail,
    wait_for_stamps,
)

N_TIME_PERIODS = 10
S3_PREFIX = "vbase-samples/sentiment-history"
RUN_ID = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"
COLLECTION_NAME = f"Python Sentiment Sample {RUN_ID}"
COLLECTION_DESCRIPTION = "A verifiable sentiment history stored in Amazon S3."


# %% [markdown]
# ## Stamp exact bytes and write them to S3
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

    collection_prefix = f"{S3_PREFIX}/{collection.cid}"
    object_cids = []
    random_generator = random.Random(1234)

    for period in range(N_TIME_PERIODS):
        sentiment = {
            "AAPL": round(random_generator.random() * 100),
            "MSFT": round(random_generator.random() * 100),
            "TSLA": round(random_generator.random() * 100),
        }
        record_bytes = json.dumps(
            sentiment,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        object_cid = get_cid_for_bytes(record_bytes)
        object_key = write_s3_object(
            s3_client,
            bucket_name,
            collection_prefix,
            f"record_{period:02d}.json",
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

        object_cids.append(object_cid)
        print(f"{object_key}: {object_cid}")

    wait_for_stamps(
        client,
        object_cids,
        collection.cid,
        user_address=owner_address,
    )

    print(f"Sentiment history: s3://{bucket_name}/{collection_prefix}/")
    print(f"Collection name: {collection.name}")
    print(f"Collection CID: {collection.cid}")
    print(f"Owner address: {owner_address}")
    print("Every stored sentiment record has a matching vBase stamp.")
