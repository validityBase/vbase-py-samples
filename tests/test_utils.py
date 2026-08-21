"""Tests for shared vBase sample helpers."""

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples"
sys.path.insert(0, str(SAMPLES_DIR))

from utils import (  # noqa: E402
    get_cid_for_bytes,
    get_collection_by_cid,
    get_env_var_or_fail,
    get_or_create_collection,
    wait_for_stamps,
)


class FakeVBaseClient:
    """Provide the vBase methods exercised by the helpers."""

    def __init__(self, collections=None, receipts=None):
        self.collections = collections or []
        self.receipts = receipts or []
        self.create_calls = []
        self.verify_calls = []

    def get_collections(self, user_address=None):
        del user_address
        return self.collections

    def create_collection(self, **kwargs):
        self.create_calls.append(kwargs)
        return SimpleNamespace(**kwargs, cid="0xcreated")

    def verify_stamps(self, cids, filter_by_user=False):
        self.verify_calls.append((cids, filter_by_user))
        return SimpleNamespace(stamp_list=self.receipts)


class UtilsTests(unittest.TestCase):
    """Verify collection, environment, hashing, and receipt behavior."""

    def test_get_env_var_or_fail_rejects_missing_or_blank_values(self):
        for value in (None, "", "   "):
            environment = {} if value is None else {"REQUIRED_VALUE": value}
            with self.subTest(value=value), patch.dict(
                os.environ, environment, clear=True
            ):
                with self.assertRaisesRegex(RuntimeError, "REQUIRED_VALUE"):
                    get_env_var_or_fail("REQUIRED_VALUE")

    def test_get_cid_for_bytes_uses_sha3_256(self):
        self.assertEqual(
            get_cid_for_bytes(b"hello"),
            "0x3338be694f50c5f338814986cdf0686453a888b84f424d792af4b9202398f392",
        )

    def test_get_or_create_collection_reuses_name_case_insensitively(self):
        existing = SimpleNamespace(name="Sample Collection", cid="0xexisting")
        client = FakeVBaseClient(collections=[existing])

        collection = get_or_create_collection(
            client,
            "sample collection",
            "Description",
        )

        self.assertIs(collection, existing)
        self.assertEqual(client.create_calls, [])

    def test_get_or_create_collection_creates_missing_collection(self):
        client = FakeVBaseClient()

        collection = get_or_create_collection(client, "New", "Description")

        self.assertEqual(collection.cid, "0xcreated")
        self.assertEqual(
            client.create_calls,
            [
                {
                    "name": "New",
                    "description": "Description",
                    "is_pinned": True,
                }
            ],
        )

    def test_get_collection_by_cid_matches_case_insensitively(self):
        expected = SimpleNamespace(name="Collection", cid="0xAbC")
        client = FakeVBaseClient(collections=[expected])

        collection = get_collection_by_cid(client, "0xaBc", "0xowner")

        self.assertIs(collection, expected)

    def test_get_collection_by_cid_rejects_unknown_collection(self):
        client = FakeVBaseClient()
        with self.assertRaisesRegex(RuntimeError, "was not found"):
            get_collection_by_cid(client, "0xmissing", "0xowner")

    def test_wait_for_stamps_requires_collection_and_owner(self):
        receipts = [
            SimpleNamespace(
                object_cid="0xaaa",
                set_cid="0xwrong",
                user_address="0xowner",
            ),
            SimpleNamespace(
                object_cid="0xaaa",
                set_cid="0xcollection",
                user_address="0xowner",
            ),
            SimpleNamespace(
                object_cid="0xbbb",
                set_cid="0xcollection",
                user_address="0xwrong",
            ),
            SimpleNamespace(
                object_cid="0xbbb",
                set_cid="0xcollection",
                user_address="0xowner",
            ),
        ]
        client = FakeVBaseClient(receipts=receipts)

        matches = wait_for_stamps(
            client,
            ["0xaaa", "0xbbb"],
            "0xcollection",
            user_address="0xowner",
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.assertEqual(set(matches), {"0xaaa", "0xbbb"})
        self.assertEqual(client.verify_calls, [(["0xaaa", "0xbbb"], False)])

    def test_wait_for_stamps_rejects_duplicate_cids(self):
        client = FakeVBaseClient()
        with self.assertRaisesRegex(ValueError, "unique"):
            wait_for_stamps(client, ["0xaaa", "0xAAA"], "0xcollection")

    def test_wait_for_stamps_matches_the_expected_transaction(self):
        receipts = [
            SimpleNamespace(
                object_cid="0xaaa",
                set_cid="0xcollection",
                user_address="0xowner",
                transaction_hash="0xold",
            ),
            SimpleNamespace(
                object_cid="0xaaa",
                set_cid="0xcollection",
                user_address="0xowner",
                transaction_hash="0xnew",
            ),
        ]
        client = FakeVBaseClient(receipts=receipts)

        matches = wait_for_stamps(
            client,
            ["0xaaa"],
            "0xcollection",
            user_address="0xowner",
            transaction_hashes_by_cid={"0xaaa": "0xnew"},
            timeout_seconds=1,
            poll_interval_seconds=0,
        )

        self.assertEqual(matches["0xaaa"].transaction_hash, "0xnew")


if __name__ == "__main__":
    unittest.main()
