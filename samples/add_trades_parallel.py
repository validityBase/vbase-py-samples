# %% [markdown]
# # Stamp Trades in Parallel
#
# Stamp several independent trade histories concurrently for one account.
# Each worker creates its own client from the same account API key. Modeling
# separate owners would require a separate user-owned API key for each owner.
# %%

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import random
import time
from uuid import uuid4

from utils import create_vbase_client_from_env, wait_for_stamps

N_STRATEGIES = 5
N_TRADES = 10
RUN_ID = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"


# %% [markdown]
# ## Define one worker-owned stamping workflow
# %%
def stamp_strategy(strategy_index):
    """Create and verify one strategy using a worker-owned API client."""
    with create_vbase_client_from_env() as client:
        collection = client.create_collection(
            name=f"Python Parallel Trades {RUN_ID} Strategy {strategy_index}",
            description="A strategy created by the parallel trades sample.",
        )
        owner_address = client.get_current_user().last_address
        if not owner_address:
            raise RuntimeError(
                "The current vBase account does not have an owner address."
            )

        random_generator = random.Random(strategy_index)
        trades = []
        stamp_receipts = []
        for trade_id in range(N_TRADES):
            trade = {
                "strategy_id": strategy_index,
                "trade_id": trade_id,
                "symbol": "ETHUSD",
                "size": round(random_generator.random() * 2 - 1, 2),
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

        verified_receipts = wait_for_stamps(
            client,
            [receipt.object_cid for receipt in stamp_receipts],
            collection.cid,
            user_address=owner_address,
        )
        return collection, trades, verified_receipts


# %% [markdown]
# ## Run the strategy workflows concurrently
# %%
start_time = time.monotonic()
with ThreadPoolExecutor(max_workers=N_STRATEGIES) as executor:
    results = list(executor.map(stamp_strategy, range(N_STRATEGIES)))
elapsed_seconds = time.monotonic() - start_time

for result_collection, result_trades, result_receipts in results:
    print(
        f"{result_collection.name}: stamped {len(result_trades)} trades and "
        f"verified {len(result_receipts)} receipts."
    )

total_trades = N_STRATEGIES * N_TRADES
print(f"Total trades: {total_trades}")
print(f"Elapsed seconds: {elapsed_seconds:.2f}")
print(f"Trades per minute: {total_trades / elapsed_seconds * 60:.2f}")
