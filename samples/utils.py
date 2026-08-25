"""Shared helpers for the vBase Python samples."""

import hashlib
import os
import time
from typing import Any, Dict, Iterable, Optional


def get_env_var_or_fail(env_var_name: str) -> str:
    """Return a required environment variable or raise a helpful error."""
    value = os.getenv(env_var_name)
    if value is None or not value.strip():
        raise RuntimeError(f"{env_var_name} environment variable is not set.")
    return value


def create_vbase_client_from_env() -> Any:
    """Create a vBase API client from ``VBASE_API_KEY``."""
    from dotenv import load_dotenv
    from vbase_api import VBaseAPIClient

    load_dotenv(verbose=True, override=False)
    return VBaseAPIClient(api_key=get_env_var_or_fail("VBASE_API_KEY"))


def get_or_create_collection(
    client: Any,
    name: str,
    description: str,
    *,
    is_pinned: bool = True,
) -> Any:
    """Return the current user's named collection, creating it if needed."""
    collection = next(
        (
            item
            for item in client.get_collections()
            if item.name.casefold() == name.casefold()
        ),
        None,
    )
    if collection is not None:
        return collection

    return client.create_collection(
        name=name,
        description=description,
        is_pinned=is_pinned,
    )


def get_collection_by_cid(client: Any, collection_cid: str, owner_address: str) -> Any:
    """Return an owner's collection by CID or raise a helpful error."""
    collection = next(
        (
            item
            for item in client.get_collections(user_address=owner_address)
            if item.cid.lower() == collection_cid.lower()
        ),
        None,
    )
    if collection is None:
        raise RuntimeError(
            f"Collection {collection_cid} was not found for {owner_address}."
        )
    return collection


def get_cid_for_bytes(data: bytes) -> str:
    """Return the vBase Content ID for an exact byte sequence."""
    return "0x" + hashlib.sha3_256(data).hexdigest()


def wait_for_stamp(
    client: Any,
    object_cid: str,
    collection_cid: str,
    *,
    filter_by_user: bool = False,
    user_address: Optional[str] = None,
    transaction_hash: Optional[str] = None,
    timeout_seconds: int = 120,
    poll_interval_seconds: int = 5,
) -> Any:
    """Wait for one matching stamp to become available for verification."""
    receipts = wait_for_stamps(
        client,
        [object_cid],
        collection_cid,
        filter_by_user=filter_by_user,
        user_address=user_address,
        transaction_hashes_by_cid=(
            {object_cid: transaction_hash} if transaction_hash else None
        ),
        timeout_seconds=timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )
    return receipts[object_cid.lower()]


def wait_for_stamps(
    client: Any,
    object_cids: Iterable[str],
    collection_cid: str,
    *,
    filter_by_user: bool = False,
    user_address: Optional[str] = None,
    transaction_hashes_by_cid: Optional[Dict[str, str]] = None,
    timeout_seconds: int = 120,
    poll_interval_seconds: int = 5,
) -> Dict[str, Any]:
    """Wait for stamps matching every CID and collection.

    When an owner address is supplied, confirm the collection through the
    owner-filtered collections API before polling. Verification receipts may
    represent their owner by account name instead of blockchain address.
    """
    requested_cids = list(object_cids)
    remaining = {object_cid.lower(): object_cid for object_cid in requested_cids}
    if len(remaining) != len(requested_cids):
        raise ValueError("Object CIDs must be unique.")

    expected_transactions = {
        object_cid.lower(): transaction_hash.lower()
        for object_cid, transaction_hash in (transaction_hashes_by_cid or {}).items()
    }
    unknown_transaction_cids = set(expected_transactions) - set(remaining)
    if unknown_transaction_cids:
        raise ValueError(
            "Transaction hashes were supplied for unrequested object CIDs: "
            + ", ".join(sorted(unknown_transaction_cids))
        )

    if user_address is not None:
        get_collection_by_cid(client, collection_cid, user_address)

    deadline = time.monotonic() + timeout_seconds
    receipts: Dict[str, Any] = {}

    while remaining and time.monotonic() < deadline:
        result = client.verify_stamps(
            list(remaining.values()),
            filter_by_user=filter_by_user,
        )
        for receipt in result.stamp_list:
            normalized_cid = receipt.object_cid.lower()
            matches_collection = receipt.set_cid.lower() == collection_cid.lower()
            expected_transaction = expected_transactions.get(normalized_cid)
            matches_transaction = (
                expected_transaction is None
                or receipt.transaction_hash.lower() == expected_transaction
            )
            if (
                normalized_cid in remaining
                and matches_collection
                and matches_transaction
            ):
                receipts[normalized_cid] = receipt
                remaining.pop(normalized_cid)

        if remaining:
            time.sleep(poll_interval_seconds)

    if remaining:
        raise TimeoutError(
            "Timed out waiting for matching vBase stamps: "
            + ", ".join(remaining.values())
        )
    return receipts
