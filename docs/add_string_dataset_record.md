# Add and Verify a String Record

<!-- omit in toc -->

This sample stamps a text record in a collection and verifies the resulting Content ID (CID), collection, and authenticated owner.

Implementation: [`samples/add_string_dataset_record.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/add_string_dataset_record.py)

## Before you run it <a href="#before-you-run-it" id="before-you-run-it"></a>

Complete the [Quickstart](quickstart.md) and set `VBASE_API_KEY`.

## Stamp the record <a href="#stamp-the-record" id="stamp-the-record"></a>

The sample creates or retrieves its collection and calls the recommended API client directly:

```python
stamp = client.create_stamp(
    data=RECORD,
    file_name="text-record.txt",
    collection_cid=collection.cid,
)
```

Because `store_stamped_file` is not overridden, vBase stores the sample text with the stamp. Storage-backed examples instead calculate the CID locally and keep the exact data in Amazon S3.

## Verify the record <a href="#verify-the-record" id="verify-the-record"></a>

New stamps may take a short time to appear through verification. The sample polls `verify_stamps()` and accepts only a receipt with the expected object CID and collection. `filter_by_user=True` limits the result to the authenticated owner.

```bash
python samples/add_string_dataset_record.py
```

A successful run prints the object CID, timestamp, and transaction hash.
