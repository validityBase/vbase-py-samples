"""Behavior checks for the parallel trades sample."""

import io
import runpy
import sys
import threading
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "samples"
sys.path.insert(0, str(SAMPLES_DIR))


class FakeVBaseClient:
    """Reject concurrent account mutations like the live service."""

    collection_count = 0
    stamp_call_lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        del args

    def create_collection(self, **kwargs):
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("collection creation must be serialized")
        type(self).collection_count += 1
        return SimpleNamespace(
            name=kwargs["name"],
            cid=f"0xcollection{self.collection_count}",
        )

    def get_current_user(self):
        return SimpleNamespace(last_address="0xowner")

    def create_stamp(self, *, data, **kwargs):
        del kwargs
        if not type(self).stamp_call_lock.acquire(blocking=False):
            raise RuntimeError("account stamp creation must be serialized")
        try:
            time.sleep(0.001)
            object_cid = f"0x{data['strategy_id']:02d}{data['trade_id']:02d}"
            return SimpleNamespace(
                commitment_receipt=SimpleNamespace(object_cid=object_cid)
            )
        finally:
            type(self).stamp_call_lock.release()


def fake_wait_for_stamps(client, object_cids, collection_cid, **kwargs):
    """Return one fake verified receipt for every requested CID."""
    del client, collection_cid, kwargs
    return {
        object_cid.lower(): SimpleNamespace(object_cid=object_cid)
        for object_cid in object_cids
    }


class ParallelSampleTests(unittest.TestCase):
    """Keep account mutations outside the parallel worker section."""

    def test_account_mutations_are_serialized_across_workers(self):
        FakeVBaseClient.collection_count = 0

        with patch(
            "utils.create_vbase_client_from_env", FakeVBaseClient
        ), patch(
            "utils.wait_for_stamps", fake_wait_for_stamps
        ), redirect_stdout(
            io.StringIO()
        ) as output:
            runpy.run_path(
                str(SAMPLES_DIR / "add_trades_parallel.py"),
                run_name="__main__",
            )

        self.assertEqual(FakeVBaseClient.collection_count, 5)
        self.assertIn("Total trades: 50", output.getvalue())


if __name__ == "__main__":
    unittest.main()
