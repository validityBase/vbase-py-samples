"""
This sample creates a dataset comprising string records
if one does not exist and adds a record to the dataset.
The sample uses async methods to commit dataset and records
and illustrates async operation using asyncio.

The sample demonstrates the higher order vBase dataset and string record abstractions
that hide the details of object and record content id (CID) calculation (hashing).
This example builds on the create_set.py code and omits redundant comments.
"""

import asyncio
import pprint
import time

from vbase import (
    VBaseClient,
    VBaseDatasetAsync,
    VBaseStringObject,
)


# Name for the test set to create.
SET_NAME = "TestDataset"


async def main():
    """
    Create the dataset and add records asynchronously.
    """

    # Initialize vBase using environment variables.
    vbc = VBaseClient.create_instance_from_env(".env")

    # Create the dataset object, if necessary.
    # Call the async VBaseDatasetAsync.create() factory method
    # to start dataset creation.
    start_time = time.time()
    task = asyncio.create_task(
        VBaseDatasetAsync.create(vbc, name=SET_NAME, record_type=VBaseStringObject)
    )
    elapsed_time = time.time() - start_time
    print(f"VBaseDatasetAsync.create(): create_task took {elapsed_time} seconds.")
    # Await for dataset creation.
    start_time = time.time()
    ds = await task
    elapsed_time = time.time() - start_time
    print(f"VBaseDatasetAsync.create(): await took {elapsed_time} seconds.")

    # Add a record to the dataset.
    # Call the async add_record_async() method
    # to start record creation.
    start_time = time.time()
    task = asyncio.create_task(ds.add_record_async("TestRecord"))
    elapsed_time = time.time() - start_time
    print(f"ds.add_record_async(record_data) create_task took {elapsed_time} seconds.")
    # Await for record creation.
    start_time = time.time()
    receipt = await task
    elapsed_time = time.time() - start_time
    print(f"ds.add_record_async(record_data) await took {elapsed_time} seconds.")
    print(f"add_record_async() receipt:\n{pprint.pformat(receipt)}")

    # Validate the dataset commitments.
    assert ds.verify_commitments()


asyncio.run(main())
