# Stamp an Interactive Brokers Portfolio

This sample retrieves current positions from the Interactive Brokers Client Portal API, converts them to portfolio weights, and creates a private vBase stamp for the exact CSV bytes stored in Amazon S3.

Implementation: [`samples/stamp_interactive_brokers_portfolio.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/stamp_interactive_brokers_portfolio.py)

## Prerequisites

Complete the [quickstart](quickstart.md), configure an S3 bucket where your AWS identity can write objects, and start an authenticated Client Portal Gateway session on `https://localhost:5000`.

This focused example supports a non-tiered IBKR account whose equity positions all use one currency. Advisor, broker, and other tiered account structures require the documented subaccount endpoints. Mixed-currency portfolios require currency conversion before their market values can be normalized into meaningful weights.

Add these values to `.env`:

```ini
VBASE_API_KEY=your-vbase-api-key
VBASE_COLLECTION_NAME=Interactive Brokers Portfolio History

AWS_S3_BUCKET=your-s3-bucket
# AWS_DEFAULT_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-aws-access-key-id
# AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
# AWS_SESSION_TOKEN=your-session-token

IB_ACCOUNT_ID=your-interactive-brokers-account-id
# IB_CA_CERT_PATH=/path/to/a/trusted/ca-certificate.pem
```

Set `IB_CA_CERT_PATH` to a trusted certificate bundle when your gateway uses a locally trusted certificate. If it is omitted, the sample prints a warning and disables certificate verification only for its loopback gateway request.

## Run the sample

```bash
python samples/stamp_interactive_brokers_portfolio.py
```

The script:

1. Initializes access to the configured portfolio account and retrieves all position pages from the local Client Portal Gateway.
2. Normalizes position market values into portfolio weights.
3. Shows the portfolio and asks for confirmation.
4. Serializes the portfolio to deterministic CSV bytes and calculates their CID locally.
5. Writes the exact bytes to S3, creates a private stamp for their CID, and verifies the resulting receipt.

The S3 object key contains the collection CID and stamped data CID, so repeated snapshots do not overwrite one another. Never commit broker, AWS, or vBase credentials.

See the Interactive Brokers documentation for the [Client Portal Gateway](https://www.interactivebrokers.com/docs/web-api/v1/endpoints/introduction) and [portfolio positions endpoint](https://www.interactivebrokers.com/docs/web-api/v1/endpoints/portfolio/positions).
