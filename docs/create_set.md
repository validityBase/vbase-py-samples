# Create a Collection

<!-- omit in toc -->

This sample creates or retrieves a vBase collection for the authenticated account and confirms that the collection is available through the API.

Implementation: [`samples/create_set.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/create_set.py)

## Before you run it <a href="#before-you-run-it" id="before-you-run-it"></a>

Complete the [Quickstart](quickstart.md) and set `VBASE_API_KEY`.

## How it works <a href="#how-it-works" id="how-it-works"></a>

The shared helper constructs `VBaseAPIClient` from the API key. The sample checks the current user's collections by name and calls `create_collection()` only when needed:

```python
collection = get_or_create_collection(
    client,
    COLLECTION_NAME,
    COLLECTION_DESCRIPTION,
)
```

It then retrieves collections for the account owner and requires an exact CID match. A successful run prints the collection name, CID, and owner address.

```bash
python samples/create_set.py
```

Collections group related stamps into one independently identifiable history. Creating or retrieving a collection does not require a blockchain private key in the local environment; authentication uses the vBase account API key.
