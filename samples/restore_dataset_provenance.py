# # restore_dataset_provenance

"""This sample illustrates how a dataset producer can create a dataset
and how the provenance of the dataset can be restored
after loss during copying or other transformations.
"""

from datetime import datetime
import pprint

from vbase import (
    VBaseClient,
    VBaseDataset,
    VBaseIntObject,
)

from aws_utils import (
    create_s3_client_from_env,
    copy_s3_bucket,
    init_vbase_dataset_from_s3_objects,
    print_s3_objects,
)


# ## Configuration

# S3 bucket for the tests.
BUCKET_NAME = "vbase-test"

# Name for the test set to create.
# Use a test dataset name that is unique and will not collide with other tests.
SET_NAME = "restore_dataset_provenance_set_" + datetime.now().strftime("%Y%m%d%H%M%S")

# Name of the source S3 folder for the dataset records.
FOLDER_NAME = "restore_dataset_provenance/" + SET_NAME
COPY_FOLDER_NAME = FOLDER_NAME + "_copy"


# ## Setup

# Initialize vBase using environment variables.
vbc = VBaseClient.create_instance_from_env()

# Create an AWS client using environment variables.
boto_client = create_s3_client_from_env()


# ## Source dataset

# Create the vBase dataset object.
vb_ds = VBaseDataset(vbc, SET_NAME, VBaseIntObject)
print(f"Created dataset {SET_NAME}")

# Create an integer sequence from 1 to 5.
seq = range(1, 6)
# Create integer dataset objects in the S3 bucket
# and the corresponding dataset objects.
for i in seq:
    s3_obj_name = f"{FOLDER_NAME}/obj_{i}.txt"
    vbase_receipt = vb_ds.add_record(i)
    print(f"Created dataset record {i}, receipt:\n{pprint.pformat(vbase_receipt)}")
    # Store the object after the commitment has been made
    # to ensure that the commitment timestamp precedes the object timestamp.
    s3_receipt = boto_client.put_object(
        Bucket=BUCKET_NAME, Key=s3_obj_name, Body=str(i)
    )
    print(f"Created S3 object {i}, receipt:\n{pprint.pformat(s3_receipt)}")

# Validate the dataset commitments.
assert vb_ds.verify_commitments()[0]

# We have the dataset and its objects created.
print("S3 objects:")
print_s3_objects(boto_client, BUCKET_NAME, FOLDER_NAME)
print("vBase dataset:")
print(vb_ds.to_pd_object())


# ## Dataset copy

# Copy the bucket to another bucket, losing the timestamps.
copy_s3_bucket(
    boto_client=boto_client,
    source_bucket_name=BUCKET_NAME,
    source_folder_name=FOLDER_NAME,
    destination_bucket_name=BUCKET_NAME,
    destination_folder_name=COPY_FOLDER_NAME,
)

# Display the copy objects as a time series.
print("Copy S3 objects:")
print_s3_objects(boto_client, BUCKET_NAME, COPY_FOLDER_NAME)


# ## Copy validation

# Create a vBase dataset from the copy S3 objects.
ds_copy = VBaseDataset(vbc, SET_NAME, VBaseIntObject)
# Load all objects into the dataset.
ds_copy = init_vbase_dataset_from_s3_objects(
    ds_copy, boto_client, BUCKET_NAME, COPY_FOLDER_NAME
)
print("Dataset loaded:")
pprint.pprint(ds_copy.to_pd_object())

# Verify the records.
success, l_log = ds_copy.verify_commitments()
assert not success
print("Verification log:")
for log in l_log:
    print(log)


# ## Metadata restoration

# Fix the timestamps.
assert ds_copy.try_restore_timestamps_from_index()[0]

print("Dataset fixed:")
pprint.pprint(ds_copy.to_pd_object())

# Verify the records again.
assert ds_copy.verify_commitments()[0]
