# %% [markdown]
# # Add a String Record
#
# Create, stamp, and verify a text record in a vBase collection.
# %%

from utils import (
    create_vbase_client_from_env,
    get_or_create_collection,
    wait_for_stamp,
)

COLLECTION_NAME = "Python Text Sample"
COLLECTION_DESCRIPTION = "Text records created by the vBase Python samples."
RECORD = "A verifiable text record"


# %% [markdown]
# ## Stamp and verify the record
# %%
with create_vbase_client_from_env() as client:
    collection = get_or_create_collection(
        client,
        COLLECTION_NAME,
        COLLECTION_DESCRIPTION,
    )
    stamp = client.create_stamp(
        data=RECORD,
        file_name="text-record.txt",
        collection_cid=collection.cid,
    )
    receipt = stamp.commitment_receipt
    verified_receipt = wait_for_stamp(
        client,
        receipt.object_cid,
        collection.cid,
        filter_by_user=True,
    )

    print(f"Collection: {collection.name} ({collection.cid})")
    print(f"Stamped CID: {receipt.object_cid}")
    print(f"Timestamp: {verified_receipt.timestamp}")
    print(f"Transaction: {verified_receipt.transaction_hash}")
    print("The text record was verified successfully.")
