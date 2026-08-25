"""Tests for shared AWS S3 sample helpers."""

import sys
import unittest
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples"
sys.path.insert(0, str(SAMPLES_DIR))

from aws_utils import (  # noqa: E402
    copy_s3_prefix,
    read_s3_objects,
    validate_s3_object_keys,
    write_s3_object,
)


class FakeBody:
    """Track whether an S3 response body is closed."""

    def __init__(self, data):
        self.data = data
        self.closed = False

    def read(self):
        return self.data

    def close(self):
        self.closed = True


class FakePaginator:
    """Return configured S3 listing pages."""

    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def paginate(self, **kwargs):
        self.calls.append(kwargs)
        return self.pages


class FakeS3Client:
    """Provide the S3 methods used by the helpers."""

    def __init__(self):
        self.paginator = FakePaginator(
            [
                {"Contents": [{"Key": "records/b.json"}]},
                {"Contents": [{"Key": "records/a.json"}]},
            ]
        )
        self.payloads = {
            "records/a.json": b"a",
            "records/b.json": b"b",
        }
        self.bodies = []
        self.put_calls = []
        self.copy_calls = []

    def get_paginator(self, operation_name):
        if operation_name != "list_objects_v2":
            raise AssertionError(f"Unexpected operation: {operation_name}")
        return self.paginator

    def get_object(self, *, Bucket, Key):
        del Bucket
        body = FakeBody(self.payloads[Key])
        self.bodies.append(body)
        return {"Body": body}

    def put_object(self, **kwargs):
        self.put_calls.append(kwargs)

    def copy(self, *args):
        self.copy_calls.append(args)


class AWSUtilsTests(unittest.TestCase):
    """Verify exact-byte reads/writes, pagination, and prefix copying."""

    def test_write_and_read_exact_bytes_in_stable_order(self):
        client = FakeS3Client()

        object_key = write_s3_object(
            client,
            "sample-bucket",
            "records/",
            "c.json",
            b"c",
        )
        objects = read_s3_objects(client, "sample-bucket", "records")

        self.assertEqual(object_key, "records/c.json")
        self.assertEqual(
            client.put_calls,
            [
                {
                    "Bucket": "sample-bucket",
                    "Key": "records/c.json",
                    "Body": b"c",
                }
            ],
        )
        self.assertEqual(objects, [("records/a.json", b"a"), ("records/b.json", b"b")])
        self.assertTrue(all(body.closed for body in client.bodies))

    def test_copy_s3_prefix_preserves_relative_keys(self):
        client = FakeS3Client()

        destination_keys = copy_s3_prefix(
            client,
            "source-bucket",
            "records",
            "destination-bucket",
            "copied",
        )

        self.assertEqual(destination_keys, ["copied/a.json", "copied/b.json"])
        self.assertEqual(
            client.copy_calls,
            [
                (
                    {"Bucket": "source-bucket", "Key": "records/a.json"},
                    "destination-bucket",
                    "copied/a.json",
                ),
                (
                    {"Bucket": "source-bucket", "Key": "records/b.json"},
                    "destination-bucket",
                    "copied/b.json",
                ),
            ],
        )

    def test_validate_s3_object_keys_rejects_missing_and_unexpected_files(self):
        with self.assertRaisesRegex(
            RuntimeError, "Missing.*b.json.*unexpected.*c.json"
        ):
            validate_s3_object_keys(
                [("records/a.json", b"a"), ("records/c.json", b"c")],
                ["records/a.json", "records/b.json"],
                "record history",
            )


if __name__ == "__main__":
    unittest.main()
