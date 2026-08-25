# vBase Python Samples

Public Python and Jupyter examples for creating and verifying data provenance with the [`vbase-api`](https://pypi.org/project/vbase-api/) client.

- Python 3.8+ for the core samples
- vBase REST API authentication with one API key
- Apache 2.0 license

## Quick start

1. Copy your API key from [vBase Account Settings](https://app.vbase.com/profile/#account_settings).
2. Clone and install the samples:

   ```bash
   git clone https://github.com/validityBase/vbase-py-samples.git
   cd vbase-py-samples
   python -m venv venv
   source venv/bin/activate
   python -m pip install -r requirements.txt
   cp .env.example .env
   ```

3. Set `VBASE_API_KEY` in `.env`, then run a first sample:

   ```bash
   python samples/create_set.py
   python samples/add_string_dataset_record.py
   ```

See the [Quickstart](docs/quickstart.md) for Windows commands, S3 configuration, and verification steps.

## Sample catalog

| Area                   | Samples                                                                           | What they demonstrate                                                                                     |
| ---------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Basics                 | `create_set`, `add_string_dataset_record`, `add_string_dataset_record_idempotent` | Collection creation, stamping, verification, and unlimited-window idempotency                             |
| Async and concurrency  | `add_string_dataset_record_async`, `add_trades_parallel`                          | Worker-owned clients, nonblocking orchestration, and serialized writes per vBase account                  |
| Trades                 | `add_trades`                                                                      | JSON stamping, batch verification, receipt timestamps, and simple analytics                               |
| Amazon S3              | Portfolio CSV/JSON and sentiment producer/verifier pairs                          | Private CID stamping, exact-byte S3 storage, verified history reconstruction, and deterministic analytics |
| Provenance restoration | `restore_dataset_provenance`                                                      | Recovering trusted stamp timestamps after S3 copy metadata changes                                        |
| Broker integrations    | Alpaca and Interactive Brokers                                                    | Normalizing portfolio weights, private CID stamping, and S3 storage                                       |
| QuantConnect           | `quantconnect_custom_signal_export`                                               | QuantConnect's native `VBaseSignalExport` provider                                                        |

The optional Alpaca sample uses the current `alpaca-py` SDK and requires Python 3.10 or newer.

Every paired `.py` and `.ipynb` sample is generated from the same source. Run `python scripts/sync_notebooks.py` after changing a paired Python sample.

## S3 samples

The S3 workflows require `AWS_S3_BUCKET`. The helpers use boto3's standard credential and region resolution, including shared profiles, AWS IAM Identity Center (SSO), environment variables, and IAM roles.

When using environment credentials, set:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION` when the region is not configured elsewhere
- `AWS_SESSION_TOKEN` only for temporary credentials

The credentials need `s3:PutObject`, `s3:GetObject`, and `s3:ListBucket` for the configured bucket and sample prefixes. The provenance-restoration sample also copies objects.

Each producer creates a unique collection and prints its collection CID and owner address. To run the matching verifier, set:

```bash
VBASE_COLLECTION_CID="0x..."
VBASE_OWNER_ADDRESS="0x..."
```

The owner is optional when the verifier uses the producer's own vBase account. Verification requires the exact stored bytes; changing whitespace, encoding, or line endings changes the CID.

## Validation

Run the local checks with:

```bash
python -m unittest discover -s tests -v
```

Live vBase, AWS, brokerage, and QuantConnect samples require the corresponding user-owned credentials and services.

## References

- [vBase documentation](https://docs.vbase.com/)
- [`vbase-api-py`](https://github.com/validityBase/vbase-api-py)
- [vBase Swagger UI](https://app.vbase.com/swagger/)
- [Contributing](CONTRIBUTING.md)
