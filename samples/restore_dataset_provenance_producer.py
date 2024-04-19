"""
This sample illustrates how a dataset producer can create a dataset
and how the provenance of the dataset can be restored
after loss during copying or other transformations.
"""

import boto3
from datetime import datetime
from dotenv import load_dotenv
import os
import pandas as pd
import pprint

from vbase import (
    VBaseClient,
    VBaseDataset,
    VBaseIntObject,
    Web3HTTPIndexingService,
)


# S3 bucket for the tests.
BUCKET_NAME = "vbase-test"

# Name for the test set to create.
# Use a test dataset name that is unique and will not collide with other tests.
SET_NAME = "restore_dataset_provenance_set_" + datetime.now().strftime("%Y%m%d%H%M%S")

# Setup

# Initialize vBase using environment variables.
vbc = VBaseClient.create_instance_from_env()

# Create the dataset object.
vb_ds = VBaseDataset(vbc, SET_NAME, VBaseIntObject)
print(f"Created dataset {SET_NAME}")

# Initialize the AWS session and the S3 client.
load_dotenv(verbose=True, override=True)
aws_session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
# Create an S3 client
s3 = aws_session.client("s3")

# Create an integer sequence from 1 to 5.
seq = range(1, 6)

# Source dataset

# Create integer dataset objects in the S3 bucket
# and the corresponding dataset objects.
folder_name = "restore_dataset_provenance/" + SET_NAME
for i in seq:
    s3_obj_name = f"{folder_name}/obj_{i}.txt"
    receipt = vb_ds.add_record(i)
    print(f"Created dataset record {i}, receipt:")
    pprint.pprint(receipt)
    # It is helpful to store the object
    # after the commitment has been made
    # to ensure that the commitment timestamp precedes
    # the object store timestamp.
    receipt = s3.put_object(Bucket=BUCKET_NAME, Key=s3_obj_name, Body=str(i))
    print(f"Created S3 object {i}, receipt:")
    pprint.pprint(receipt)

# Validate the dataset commitments.
success, l_log = vb_ds.verify_commitments()
assert success

# We have the dataset and its objects created.
# Display the dataset as a time series.
print("Dataset created:")
print(vb_ds.to_pd_object())
# Display the objects as a time series.
objects_receipt = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_name + "/")
print("S3 objects created:")
pprint.pprint(
    [{"obj": r["Key"], "t": r["LastModified"]} for r in objects_receipt["Contents"]]
)

# Dataset copy

# Copy the bucket to another bucket, losing the timestamps.
copy_folder_name = folder_name + "_copy"
for i in reversed(seq):
    copy_source = {"Bucket": BUCKET_NAME, "Key": f"{folder_name}/obj_{i}.txt"}
    s3_dest_obj_name = f"{copy_folder_name}/obj_{i}.txt"
    s3.copy(copy_source, BUCKET_NAME, s3_dest_obj_name)
    print(f"Copied {copy_source} to {s3_dest_obj_name}")

# Display the copy objects as a time series.
objects_receipt = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=copy_folder_name + "/")
print("S3 objects copied:")
pprint.pprint(
    [{"obj": r["Key"], "t": r["LastModified"]} for r in objects_receipt["Contents"]]
)

# Copy validation

# Create a vBase dataset from the copy S3 objects.
vb_ds_copy = VBaseDataset(vbc, SET_NAME, VBaseIntObject)
# Load all objects into the dataset.
for r in objects_receipt["Contents"]:
    response = s3.get_object(Bucket=BUCKET_NAME, Key=r["Key"])
    data = response["Body"].read()
    vb_ds_copy.records.append(VBaseIntObject(int(data)))
    vb_ds_copy.timestamps.append(
        str(pd.Timestamp(response["LastModified"]).tz_convert("UTC"))
    )

print("Dataset loaded:")
pprint.pprint(vb_ds_copy.to_pd_object())

# Verify the records.
success, l_log = vb_ds_copy.verify_commitments()
print("Verification log:")
for log in l_log:
    print(log)

# Metadata restoration

# Fix the timestamps.
# Create the indexing service.
indexing_service = Web3HTTPIndexingService.create_instance_from_commitment_service(
    vbc.commitment_service
)
# Find the commitment receipts for the set.
commitment_receipts = indexing_service.find_user_set_objects(
    user=vb_ds_copy.owner, set_cid=vb_ds_copy.cid
)
# Fix the timestamps using the commitment receipts.
for i, vb_ds_record in enumerate(vb_ds_copy.records):
    # Find the matching receipt and update the corresponding timestamp.
    obj_cid = vb_ds_record.get_cid()
    matches = [r["objectCid"] == obj_cid for r in commitment_receipts]
    i_match = next((i for i, v in enumerate(matches) if v), -1)
    vb_ds_copy.timestamps[i] = commitment_receipts[i_match]["timestamp"]

print("Dataset fixed:")
pprint.pprint(vb_ds_copy.to_pd_object())

# Verify the records again.
success, l_log = vb_ds_copy.verify_commitments()
assert success
