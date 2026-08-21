"""Retrieve an IBKR portfolio, stamp its exact CSV bytes, and save it to S3."""

from datetime import datetime, timezone
import os

from dotenv import load_dotenv
import pandas as pd
import requests

from aws_utils import create_s3_client_from_env, write_s3_object
from utils import (
    create_vbase_client_from_env,
    get_cid_for_bytes,
    get_env_var_or_fail,
    get_or_create_collection,
    wait_for_stamp,
)

load_dotenv(verbose=True, override=False)

IB_ACCOUNT_ID = get_env_var_or_fail("IB_ACCOUNT_ID")
COLLECTION_NAME = get_env_var_or_fail("VBASE_COLLECTION_NAME")
S3_PREFIX = "vbase-samples/broker-portfolios"
IB_GATEWAY_BASE_URL = "https://localhost:5000/v1/api"


ib_ca_cert_path = os.getenv("IB_CA_CERT_PATH")
tls_verification = ib_ca_cert_path if ib_ca_cert_path else False
if not ib_ca_cert_path:
    print(
        "IB_CA_CERT_PATH is not set. TLS verification is disabled only for the "
        "local IB Client Portal Gateway request."
    )

request_options = {"verify": tls_verification, "timeout": 30}
accounts_response = requests.get(
    f"{IB_GATEWAY_BASE_URL}/portfolio/accounts",
    **request_options,
)
accounts_response.raise_for_status()
accessible_account_ids = {
    account_id
    for account in accounts_response.json()
    for account_id in (account.get("id"), account.get("accountId"))
    if account_id
}
if IB_ACCOUNT_ID not in accessible_account_ids:
    raise RuntimeError(
        f"IB_ACCOUNT_ID {IB_ACCOUNT_ID} is not available in the non-tiered "
        "gateway account list."
    )

raw_positions = []
for page_id in range(100):
    positions_response = requests.get(
        f"{IB_GATEWAY_BASE_URL}/portfolio/{IB_ACCOUNT_ID}/positions/{page_id}",
        **request_options,
    )
    positions_response.raise_for_status()
    page = positions_response.json()
    raw_positions.extend(page)
    if len(page) < 100:
        break
else:
    raise RuntimeError("The Interactive Brokers position history exceeded 100 pages.")

positions = [
    {
        "sym": position["contractDesc"],
        "value": float(position["mktValue"]),
        "currency": position["currency"],
    }
    for position in raw_positions
    if position["assetClass"] == "STK"
]
if not positions:
    raise RuntimeError("No equity positions were returned by Interactive Brokers.")

portfolio_currencies = {position["currency"] for position in positions}
if len(portfolio_currencies) != 1:
    raise RuntimeError(
        "This sample requires all Interactive Brokers equity positions to use "
        "one currency; convert mixed-currency values before calculating weights."
    )

total_value = sum(position["value"] for position in positions)
if total_value == 0:
    raise RuntimeError("The Interactive Brokers equity portfolio has zero total value.")

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
        "Portfolio records imported from Interactive Brokers.",
    )
    owner_address = client.get_current_user().last_address
    if not owner_address:
        raise RuntimeError("The current vBase account does not have an owner address.")

    stamp = client.create_stamp(
        data_cid=object_cid,
        collection_cid=collection.cid,
        store_stamped_file=False,
        idempotent=False,
    )
    if stamp.commitment_receipt.object_cid.lower() != object_cid.lower():
        raise RuntimeError("vBase returned a different CID than the portfolio bytes.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    object_key = write_s3_object(
        s3_client,
        bucket_name,
        f"{S3_PREFIX}/{collection.cid}",
        f"ibkr_portfolio_{timestamp}_{object_cid}.csv",
        portfolio_bytes,
    )
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
    print("The Interactive Brokers portfolio was stored and verified successfully.")
