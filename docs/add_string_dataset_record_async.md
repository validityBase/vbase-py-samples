# Use the vBase API Client from Async Code

This sample runs the complete synchronous stamping and verification workflow without blocking an application's `asyncio` event loop.

Implementation: [`samples/add_string_dataset_record_async.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/add_string_dataset_record_async.py)

## Why a worker thread is used <a href="#why-a-worker-thread-is-used" id="why-a-worker-thread-is-used"></a>

`VBaseAPIClient` provides a synchronous interface. Async applications can move the blocking network workflow to an executor:

```python
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(None, operation)
```

The worker creates and closes its own API client. Client sessions are not shared across threads.

## Run the sample <a href="#run-the-sample" id="run-the-sample"></a>

Complete the [Quickstart](quickstart.md), then run:

```bash
python samples/add_string_dataset_record_async.py
```

The matching notebook uses top-level `await` but is generated from the same Python source. A successful run prints the collection CID, object CID, and verified timestamp.
