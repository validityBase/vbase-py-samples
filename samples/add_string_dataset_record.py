# # add_string_dataset_record

"""This sample creates a dataset comprising string records
if one does not exist and adds a record to the dataset.

The sample demonstrates the higher order vBase dataset and string record abstractions
that hide the details of object and record content id (CID) calculation (hashing).
This example builds on the create_set.py code and omits redundant comments.
"""

import pprint

from vbase import (
    VBaseClient,
    VBaseDataset,
    VBaseStringObject,
)


# Name for the test set to create.
SET_NAME = "TestDataset1"


# Initialize vBase using environment variables.
vbc = VBaseClient.create_instance_from_env()

# Create the dataset object, if necessary.
ds = VBaseDataset(vbc, SET_NAME, VBaseStringObject)

# Add a record to the dataset.
receipt = ds.add_record("TestRecord")
print(f"add_record() receipt:\n{pprint.pformat(receipt)}")

# Validate the dataset commitments.
assert ds.verify_commitments()[0]
