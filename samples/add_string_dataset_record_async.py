# %% [markdown]
# # Use the vBase API Client from Async Code
#
# Run the synchronous vBase API workflow without blocking the event loop.
# %%

import asyncio
from functools import partial

from utils import (
    create_vbase_client_from_env,
    get_or_create_collection,
    wait_for_stamp,
)

COLLECTION_NAME = "Python Async Sample"
COLLECTION_DESCRIPTION = "Records created from asynchronous Python code."
RECORD = "A record stamped without blocking the event loop"


# %% [markdown]
# ## Define the worker workflow
# %%
def stamp_and_verify_record(record):
    """Run one complete workflow in a worker-owned client session."""
    with create_vbase_client_from_env() as client:
        collection = get_or_create_collection(
            client,
            COLLECTION_NAME,
            COLLECTION_DESCRIPTION,
        )
        stamp = client.create_stamp(
            data=record,
            file_name="async-text-record.txt",
            collection_cid=collection.cid,
        )
        receipt = stamp.commitment_receipt
        wait_for_stamp(
            client,
            receipt.object_cid,
            collection.cid,
            filter_by_user=True,
        )
        return collection, receipt


async def stamp_record_without_blocking(record):
    """Move the synchronous network work to the default executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(stamp_and_verify_record, record))


# %% [markdown]
# ## Run without blocking the event loop
# %%
async def main():
    """Stamp a record while allowing the event loop to remain responsive."""
    collection, receipt = await stamp_record_without_blocking(RECORD)
    print(f"Collection: {collection.name} ({collection.cid})")
    print(f"Stamped CID: {receipt.object_cid}")
    print(f"Timestamp: {receipt.timestamp}")
    print(
        "The worker completed and verified the stamp without blocking the event loop."
    )


# NOTEBOOK_ONLY: await main()
# SCRIPT_ONLY_BEGIN
if __name__ == "__main__":
    asyncio.run(main())
# SCRIPT_ONLY_END
