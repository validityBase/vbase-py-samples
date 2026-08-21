# %% [markdown]
# # Stamp and Verify Trades
#
# Create a collection of JSON trades and verify every resulting stamp.
# %%

from datetime import datetime, timezone
import pprint
import time
from uuid import uuid4

import pandas as pd

from utils import create_vbase_client_from_env, wait_for_stamps

N_TRADES = 10
RUN_ID = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"
COLLECTION_NAME = f"Python Trades Sample {RUN_ID}"
COLLECTION_DESCRIPTION = "A verifiable sequence of sample JSON trades."


# %% [markdown]
# ## Stamp, verify, and analyze the trades
# %%
with create_vbase_client_from_env() as client:
    collection = client.create_collection(
        name=COLLECTION_NAME,
        description=COLLECTION_DESCRIPTION,
    )
    owner_address = client.get_current_user().last_address
    if not owner_address:
        raise RuntimeError("The current vBase account does not have an owner address.")

    trades = []
    stamp_receipts = []
    start_time = time.monotonic()
    for trade_id in range(N_TRADES):
        trade = {
            "trade_id": trade_id,
            "symbol": "ETHUSD",
            "size": 1 if trade_id % 2 == 0 else -1,
        }
        stamp = client.create_stamp(
            data=trade,
            file_name=f"trade_{trade_id:02d}.json",
            collection_cid=collection.cid,
            idempotent=True,
            idempotency_window=0,
        )
        trades.append(trade)
        stamp_receipts.append(stamp.commitment_receipt)
        print(f"Posted trade: {pprint.pformat(trade)}")

    elapsed_seconds = time.monotonic() - start_time
    receipts_by_cid = wait_for_stamps(
        client,
        [receipt.object_cid for receipt in stamp_receipts],
        collection.cid,
        user_address=owner_address,
    )

    timestamps = [
        receipts_by_cid[receipt.object_cid.lower()].timestamp
        for receipt in stamp_receipts
    ]
    trades_frame = pd.DataFrame(
        trades,
        index=pd.to_datetime(timestamps, utc=True),
    )
    trades_frame.index.name = "timestamp"

    print(f"Collection: {collection.name} ({collection.cid})")
    print(f"Verified trades: {len(receipts_by_cid)}")
    print(f"Elapsed seconds: {elapsed_seconds:.2f}")
    print(f"Trades per second: {N_TRADES / elapsed_seconds:.2f}")
    print(trades_frame)

    trades_frame["weight"] = trades_frame["size"].cumsum()
    returns = [0.01, -0.02, 0.03, -0.01, 0.02, -0.03, 0.015, -0.01, 0.025, -0.02]
    (1 + trades_frame["weight"] * returns).cumprod().plot()
