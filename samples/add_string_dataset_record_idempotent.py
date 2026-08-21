# # Add a String Record Idempotently

"""Show that repeated idempotent requests return the same text stamp."""

from utils import (
    create_vbase_client_from_env,
    get_or_create_collection,
    wait_for_stamp,
)

COLLECTION_NAME = "Python Idempotency Sample"
COLLECTION_DESCRIPTION = "Idempotent records created by the vBase Python samples."
RECORD = "A record that should have one unlimited-window stamp"


with create_vbase_client_from_env() as client:
    collection = get_or_create_collection(
        client,
        COLLECTION_NAME,
        COLLECTION_DESCRIPTION,
    )
    request = {
        "data": RECORD,
        "file_name": "idempotent-record.txt",
        "collection_cid": collection.cid,
        "idempotent": True,
        "idempotency_window": 0,
    }
    first_stamp = client.create_stamp(**request)
    second_stamp = client.create_stamp(**request)
    first_receipt = first_stamp.commitment_receipt
    second_receipt = second_stamp.commitment_receipt

    if first_receipt.object_cid.lower() != second_receipt.object_cid.lower():
        raise RuntimeError("The repeated requests returned different object CIDs.")
    if (
        first_receipt.transaction_hash.lower()
        != second_receipt.transaction_hash.lower()
    ):
        raise RuntimeError("The repeated requests created different transactions.")

    wait_for_stamp(
        client,
        first_receipt.object_cid,
        collection.cid,
        filter_by_user=True,
    )

    print(f"Collection: {collection.name} ({collection.cid})")
    print(f"Object CID: {first_receipt.object_cid}")
    print(f"Transaction: {first_receipt.transaction_hash}")
    print("The repeated idempotent request returned the original stamp.")
