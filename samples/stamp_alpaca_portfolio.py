"""Retrieve an Alpaca portfolio, stamp its exact CSV bytes, and save it to S3."""

from datetime import datetime, timezone
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass
from dotenv import load_dotenv
import pandas as pd

from aws_utils import create_s3_client_from_env, write_s3_object
from utils import (
    create_vbase_client_from_env,
    get_cid_for_bytes,
    get_env_var_or_fail,
    get_or_create_collection,
    wait_for_stamp,
)

load_dotenv(verbose=True, override=False)

ALPACA_API_KEY = get_env_var_or_fail("ALPACA_API_KEY")
ALPACA_API_SECRET = get_env_var_or_fail("ALPACA_API_SECRET")
COLLECTION_NAME = get_env_var_or_fail("VBASE_COLLECTION_NAME")
S3_PREFIX = "vbase-samples/broker-portfolios"


paper_value = os.getenv("ALPACA_PAPER", "true").strip().lower()
if paper_value not in {"true", "false"}:
    raise RuntimeError("ALPACA_PAPER must be either true or false.")

alpaca_client = TradingClient(
    ALPACA_API_KEY,
    ALPACA_API_SECRET,
    paper=paper_value == "true",
)
positions = [
    {"sym": position.symbol, "value": float(position.market_value)}
    for position in alpaca_client.get_all_positions()
    if position.asset_class == AssetClass.US_EQUITY
]
if not positions:
    raise RuntimeError("No equity positions were returned by Alpaca.")

total_value = sum(position["value"] for position in positions)
if total_value == 0:
    raise RuntimeError("The Alpaca equity portfolio has zero total market value.")

portfolio_frame = pd.DataFrame(
    [
        {"sym": position["sym"], "wt": position["value"] / total_value}
        for position in positions
    ]
)
print("The following portfolio will be stamped:")
print(portfolio_frame)
if input("Stamp this portfolio? (yes/no) [y]: ").lower() not in ["yes", "y", ""]:
    raise SystemExit("Portfolio stamping cancelled.")

portfolio_bytes = portfolio_frame.to_csv(
    index=False,
    lineterminator="\n",
).encode("utf-8")
object_cid = get_cid_for_bytes(portfolio_bytes)

s3_client = create_s3_client_from_env()
bucket_name = get_env_var_or_fail("AWS_S3_BUCKET")

with create_vbase_client_from_env() as client:
    collection = get_or_create_collection(
        client,
        COLLECTION_NAME,
        "Portfolio records imported from Alpaca.",
    )
    owner_address = client.get_current_user().last_address
    if not owner_address:
        raise RuntimeError("The current vBase account does not have an owner address.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    object_key = write_s3_object(
        s3_client,
        bucket_name,
        f"{S3_PREFIX}/{collection.cid}",
        f"alpaca_portfolio_{timestamp}_{object_cid}.csv",
        portfolio_bytes,
    )
    stamp = client.create_stamp(
        data_cid=object_cid,
        collection_cid=collection.cid,
        store_stamped_file=False,
        idempotent=False,
    )
    if stamp.commitment_receipt.object_cid.lower() != object_cid.lower():
        raise RuntimeError("vBase returned a different CID than the portfolio bytes.")

    verified_receipt = wait_for_stamp(
        client,
        object_cid,
        collection.cid,
        user_address=owner_address,
        transaction_hash=stamp.commitment_receipt.transaction_hash,
    )

    print(f"Saved portfolio: s3://{bucket_name}/{object_key}")
    print(f"Collection: {collection.name} ({collection.cid})")
    print(f"Object CID: {object_cid}")
    print(f"Stamp timestamp: {verified_receipt.timestamp}")
    print("The Alpaca portfolio was stored and verified successfully.")
