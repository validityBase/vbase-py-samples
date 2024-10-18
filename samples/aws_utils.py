"""
AWS utilities
"""

import json
import os
import pprint
from typing import List, Union
import boto3
from dotenv import load_dotenv
import pandas as pd

from vbase import VBaseDataset


def create_s3_client_from_env() -> boto3.client:
    """
    Create a boto3.client object using the environment variables.

    :return: The boto3.client object.
    """
    load_dotenv(verbose=True, override=True)
    # Initialize the AWS session and the S3 client.
    aws_session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    # Create an S3 client
    boto3_client = aws_session.client("s3")
    return boto3_client


def get_s3_objects(
    boto_client: boto3.client, bucket_name: str, folder_name: str
) -> Union[List[dict], None]:
    """
    Get S3 objects.

    :param boto_client: The boto3.client object.
    :param bucket_name: The bucket name.
    :param folder_name: The folder name within the bucket.
    """
    # Ensure the folder names end with a "/".
    if not folder_name.endswith("/"):
        folder_name += "/"
    # Note that this assumes small datasets and does not implement paging.
    s3_objs = boto_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    if "Contents" in s3_objs:
        return s3_objs["Contents"]
    return None


def print_s3_objects(boto_client: boto3.client, bucket_name: str, folder_name: str):
    """
    Print S3 objects.

    :param boto_client: The boto3.client object.
    :param bucket_name: The bucket name.
    :param folder_name: The folder name within the bucket.
    """
    s3_objs = get_s3_objects(boto_client, bucket_name, folder_name)
    if s3_objs is None:
        print("No objects")
    else:
        pprint.pprint(
            [
                {"object": s3_obj["Key"], "timestamp": str(s3_obj["LastModified"])}
                for s3_obj in s3_objs
            ]
        )


def copy_s3_bucket(
    boto_client: boto3.client,
    source_bucket_name: str,
    source_folder_name: str,
    destination_bucket_name: str,
    destination_folder_name: str,
):
    """
    Copy an S3 bucket.

    :param boto_client: The boto3.client object.
    :param source_bucket_name: The source bucket name.
    :param source_folder_name: The folder name within the source bucket.
    :param destination_bucket_name: The destination bucket name.
    :param destination_folder_name: The folder name within the destination bucket.
    """
    # Ensure the folder names end with a "/".
    if not source_folder_name.endswith("/"):
        source_folder_name += "/"
    if not destination_folder_name.endswith("/"):
        destination_folder_name += "/"

    # Let exceptions propagate to the caller.
    # Create a paginator to handle pagination.
    paginator = boto_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(
        Bucket=source_bucket_name, Prefix=source_folder_name
    ):
        # See if any contents were returned for the page.
        if "Contents" in page:
            for obj in page["Contents"]:
                # Adjust the destination key to include the destination folder
                destination_key = obj["Key"].replace(
                    source_folder_name, destination_folder_name, 1
                )
                copy_source = {"Bucket": source_bucket_name, "Key": obj["Key"]}
                # Copy the object to the new destination key in the destination bucket.
                boto_client.copy(copy_source, destination_bucket_name, destination_key)
                print(
                    f"Copied {obj['Key']} from {source_bucket_name} to "
                    f"{destination_bucket_name}/{destination_key}"
                )


def init_vbase_dataset_from_s3_objects(
    ds: VBaseDataset, boto_client: boto3.client, bucket_name: str, folder_name: str
) -> VBaseDataset:
    """
    Get S3 objects and add them to a dataset.

    :param ds: The vBaseDataset object to initialize.
    :param boto_client: The boto3.client object.
    :param bucket_name: The bucket name.
    :param folder_name: The folder name within the bucket.
    """
    # Get all the objects to add to the dataset.
    # Note that this assumes small datasets and does not implement paging.
    s3_objs = get_s3_objects(boto_client, bucket_name, folder_name)
    if s3_objs is None:
        print("No objects")
        return ds
    # Append object data and records to the dataset.
    ds.records = []
    ds.timestamps = []
    for s3_obj in s3_objs:
        response = boto_client.get_object(Bucket=bucket_name, Key=s3_obj["Key"])
        str_data = response["Body"].read().decode("utf-8")
        ds.records.append(ds.record_type(str_data))
        ds.timestamps.append(
            str(pd.Timestamp(response["LastModified"]).tz_convert("UTC"))
        )
    return ds


def create_s3_objects_from_dataset(
    ds: VBaseDataset, boto_client: boto3.client, bucket_name: str, folder_name: str
) -> dict:
    """
    Create S3 objects for dataset records.

    :param ds: The vBaseDataset object.
    :param boto_client: The boto3.client object.
    :param bucket_name: The bucket name.
    :param folder_name: The folder name within the bucket.
    :return: The operation receipts.
    """
    if not folder_name.endswith("/"):
        folder_name += "/"
    # Append dataset name to folder name, if necessary.
    if not folder_name.endswith(f"{ds.name}/"):
        folder_name += f"{ds.name}/"

    # Loop over the dataset records,
    # creating S3 objects for them.
    l_s3_receipts = []
    for i, record in enumerate(ds.records):
        record_json = json.dumps(record.get_dict())
        s3_obj_name = f"{folder_name}obj_{i}.json"
        s3_receipt = boto_client.put_object(
            Bucket=bucket_name, Key=s3_obj_name, Body=record_json
        )
        print(f"Created S3 object: {s3_obj_name}")
        l_s3_receipts.append(s3_receipt)
    return l_s3_receipts


def write_s3_object(
    boto_client: boto3.client,
    bucket_name: str,
    folder_name: str,
    file_name: str,
    data: str,
) -> dict:
    """
    Create S3 objects for dataset records.

    :param ds: The vBaseDataset object.
    :param boto_client: The boto3.client object.
    :param bucket_name: The bucket name.
    :param folder_name: The folder name within the bucket.
    :return: The operation receipt.
    """
    if not folder_name.endswith("/"):
        folder_name += "/"
    # Append dataset name to folder name, if necessary.
    if not folder_name.endswith("/"):
        folder_name += "/"

    s3_obj_name = folder_name + file_name

    # Loop over the dataset records,
    # creating S3 objects for them.
    s3_receipt = boto_client.put_object(Bucket=bucket_name, Key=s3_obj_name, Body=data)
    print(f"Created S3 object: {s3_obj_name}")
    return s3_receipt
