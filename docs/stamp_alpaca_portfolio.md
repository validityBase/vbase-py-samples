# Stamp an Alpaca Portfolio

This sample retrieves current US equity positions from Alpaca, converts them to portfolio weights, and creates a private vBase stamp for the exact CSV bytes stored in Amazon S3.

Implementation: [`samples/stamp_alpaca_portfolio.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/stamp_alpaca_portfolio.py)

## Prerequisites

Complete the [quickstart](quickstart.md), configure an S3 bucket where your AWS identity can write objects, and create Alpaca API credentials. The official `alpaca-py` SDK requires Python 3.10 or newer.

Install the optional broker dependency:

```bash
python -m pip install alpaca-py
```

Add these values to `.env`:

```ini
VBASE_API_KEY=your-vbase-api-key
VBASE_COLLECTION_NAME=Alpaca Portfolio History

AWS_S3_BUCKET=your-s3-bucket
# AWS_DEFAULT_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-aws-access-key-id
# AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
# AWS_SESSION_TOKEN=your-session-token

ALPACA_API_KEY=your-alpaca-api-key
ALPACA_API_SECRET=your-alpaca-api-secret
ALPACA_PAPER=true
```

Use `ALPACA_PAPER=false` only when the credentials belong to a live account. Never commit real credentials.

## Run the sample

```bash
python samples/stamp_alpaca_portfolio.py
```

The script:

1. Retrieves all current positions with Alpaca's `TradingClient`.
2. Keeps US equity positions and normalizes their market values into weights.
3. Shows the portfolio and asks for confirmation.
4. Serializes the portfolio to deterministic CSV bytes and calculates their CID locally.
5. Writes the exact bytes to S3, creates a private stamp for their CID, and verifies the resulting receipt.

The S3 object key contains the collection CID and stamped data CID, so repeated snapshots do not overwrite one another.

See Alpaca's official guides for [working with positions](https://docs.alpaca.markets/docs/working-with-positions) and [Python SDKs](https://docs.alpaca.markets/docs/sdks-and-tools).
