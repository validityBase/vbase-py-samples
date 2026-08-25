"""Behavior checks for the asynchronous vBase sample."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples"
sys.path.insert(0, str(SAMPLES_DIR))

import add_string_dataset_record_async as async_sample  # noqa: E402


class AsyncSampleTests(unittest.TestCase):
    """Verify that the worker returns the receipt it actually verified."""

    def test_worker_returns_verified_receipt_for_created_transaction(self):
        collection = SimpleNamespace(cid="0xcollection")
        created_receipt = SimpleNamespace(
            object_cid="0xobject",
            transaction_hash="0xcreated",
            timestamp=None,
        )
        verified_receipt = SimpleNamespace(
            object_cid="0xobject",
            transaction_hash="0xcreated",
            timestamp="2026-08-23T12:00:00Z",
        )
        client = MagicMock()
        client.__enter__.return_value = client
        client.create_stamp.return_value = SimpleNamespace(
            commitment_receipt=created_receipt
        )

        with patch.object(
            async_sample,
            "create_vbase_client_from_env",
            return_value=client,
        ), patch.object(
            async_sample,
            "get_or_create_collection",
            return_value=collection,
        ), patch.object(
            async_sample,
            "wait_for_stamp",
            return_value=verified_receipt,
        ) as wait_for_stamp:
            returned_collection, returned_receipt = (
                async_sample.stamp_and_verify_record("record")
            )

        self.assertIs(returned_collection, collection)
        self.assertIs(returned_receipt, verified_receipt)
        wait_for_stamp.assert_called_once_with(
            client,
            created_receipt.object_cid,
            collection.cid,
            filter_by_user=True,
            transaction_hash=created_receipt.transaction_hash,
        )


if __name__ == "__main__":
    unittest.main()
