# Restore Dataset Provenance after an S3 Copy

This sample demonstrates how vBase stamp receipts recover trusted record timestamps after Amazon S3 copy metadata has changed.

Implementation: [`samples/restore_dataset_provenance.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/restore_dataset_provenance.py)

## Before you run it <a href="#before-you-run-it" id="before-you-run-it"></a>

Configure `VBASE_API_KEY` and the AWS variables from the [Quickstart](quickstart.md). The AWS identity needs list, read, write, and copy access for the configured bucket.

## Workflow <a href="#workflow" id="workflow"></a>

1. Create a unique vBase collection.
2. Encode each record to exact UTF-8 bytes and calculate its SHA3-256 CID locally.
3. Stamp each CID with `store_stamped_file=False`, so record contents are not uploaded to vBase.
4. Write the exact bytes to an S3 source prefix.
5. Copy the objects to a new prefix. S3 storage timestamps may change, but the bytes and CIDs must remain identical.
6. Recalculate every copied object's CID and match it to a receipt with the expected collection and owner.
7. Build a provenance table containing both the copied object's S3 timestamp and its trusted vBase stamp timestamp.

Copying an object does not invalidate its contents. The sample therefore does not claim that the copied record fails cryptographic verification; it shows that storage metadata and provenance timestamps are different concepts.

```bash
python samples/restore_dataset_provenance.py
```

A successful run prints the restored provenance table, collection CID, and owner address.
