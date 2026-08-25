"""AWS S3 helpers shared by the storage-backed samples."""

from typing import Any, List, Tuple


def create_s3_client_from_env() -> Any:
    """Create an S3 client using boto3's standard credential resolution."""
    from dotenv import load_dotenv
    import boto3

    load_dotenv(verbose=True, override=False)
    return boto3.client("s3")


def list_s3_objects(
    s3_client: Any,
    bucket_name: str,
    prefix: str,
) -> List[dict]:
    """List every object below an S3 prefix in stable key order."""
    normalized_prefix = prefix.rstrip("/") + "/"
    paginator = s3_client.get_paginator("list_objects_v2")
    objects = []
    for page in paginator.paginate(Bucket=bucket_name, Prefix=normalized_prefix):
        objects.extend(page.get("Contents", []))
    return sorted(objects, key=lambda item: item["Key"])


def print_s3_objects(s3_client: Any, bucket_name: str, prefix: str) -> None:
    """Print object keys and storage timestamps below a prefix."""
    objects = list_s3_objects(s3_client, bucket_name, prefix)
    if not objects:
        print("No objects found.")
        return
    for item in objects:
        print(f"{item['Key']}: {item['LastModified']}")


def write_s3_object(
    s3_client: Any,
    bucket_name: str,
    prefix: str,
    file_name: str,
    data: bytes,
) -> str:
    """Write exact bytes to S3 and return the object key."""
    object_key = f"{prefix.rstrip('/')}/{file_name}"
    s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=data)
    return object_key


def read_s3_object(s3_client: Any, bucket_name: str, object_key: str) -> bytes:
    """Read exact bytes from one S3 object."""
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    body = response["Body"]
    try:
        return body.read()
    finally:
        close = getattr(body, "close", None)
        if close is not None:
            close()


def read_s3_objects(
    s3_client: Any,
    bucket_name: str,
    prefix: str,
) -> List[Tuple[str, bytes]]:
    """Read every object below a prefix in stable key order."""
    return [
        (item["Key"], read_s3_object(s3_client, bucket_name, item["Key"]))
        for item in list_s3_objects(s3_client, bucket_name, prefix)
    ]


def validate_s3_object_keys(
    objects: List[Tuple[str, bytes]],
    expected_keys: List[str],
    history_name: str,
) -> None:
    """Require an S3 history to contain exactly the expected object keys."""
    actual = {key for key, _ in objects}
    expected = set(expected_keys)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        raise RuntimeError(
            f"The S3 {history_name} does not match the expected sample files. "
            f"Missing: {missing or 'none'}; unexpected: {unexpected or 'none'}."
        )


def copy_s3_prefix(
    s3_client: Any,
    source_bucket_name: str,
    source_prefix: str,
    destination_bucket_name: str,
    destination_prefix: str,
) -> List[str]:
    """Copy every object below one S3 prefix to another prefix."""
    normalized_source = source_prefix.rstrip("/") + "/"
    normalized_destination = destination_prefix.rstrip("/") + "/"
    destination_keys = []

    for item in list_s3_objects(s3_client, source_bucket_name, source_prefix):
        relative_key = item["Key"][len(normalized_source) :]
        destination_key = normalized_destination + relative_key
        s3_client.copy(
            {"Bucket": source_bucket_name, "Key": item["Key"]},
            destination_bucket_name,
            destination_key,
        )
        destination_keys.append(destination_key)

    return destination_keys
