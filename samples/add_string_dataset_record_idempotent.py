# # add_string_dataset_record

"""This sample creates a dataset comprising string records
if one does not exist and adds a record to the dataset in an idempotent way.

This sample expands the simple record addition to show
how one can check for existing commitments for a record.
"""

import pprint

from vbase import (
    VBaseClient,
    VBaseDataset,
    VBaseStringObject,
)


# Name for the test dataset to create.
DATASET_NAME = "TestDataset"
# Test record data.
RECORD_DATA = "TestRecord"


# Initialize vBase using environment variables.
vbc = VBaseClient.create_instance_from_env()

# Create the dataset of strings, if necessary.
# The constructor will not make a duplicate dataset commitment if one already exists.
ds = VBaseDataset(vbc, DATASET_NAME, VBaseStringObject)

# Idempotent record addition that will ignore duplicates.
# You can rerun this section of code without adding duplicate records.
if any(
    r["objectCid"] == VBaseStringObject.get_cid_for_data(RECORD_DATA)
    for r in ds.get_commitment_receipts()
):
    print("Record exists.")
else:
    print("Record does not exist.")
    receipt = ds.add_record(RECORD_DATA)
    print(f"add_record() receipt:\n{pprint.pformat(receipt)}")

# Validate the dataset commitments.
assert ds.verify_commitments()[0]

# Print dataset commitment receipts.
receipts = ds.get_commitment_receipts()
print(f"receipts = {pprint.pformat(receipts)}")
