----
title: Add a String Record to a Dataset Asynchronously
----

<!-- omit in toc -->
# Add a String Record to a Dataset Asynchronously

This sample creates a dataset comprising string records if one does not exist and adds a record to the dataset. The sample uses async methods to commit a dataset and records
and illustrates async operation using asyncio.

You can find the implementation in [`add_string_dataset_record_async.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/add_string_dataset_record_async.py).

## Summary<a href="#summary" id="summary"></a>

A set is a collection of objects. A named set of data records is a dataset. Such datasets can implement any point-in-time (PIT) or bitemporal data and prove this provenance to third parties. 

The sample demonstrates the higher-order async vBase dataset and string record abstractions that hide the details of the object and record content id (CID) calculation (hashing). This example builds on the add_string_dataset_record.py code and illustrates async methods.

## Detailed Description<a href="#detailed-description" id="detailed-description"></a>

- Create a vBase object using a Web3 HTTP commitment service.
The commitment service is a smart contract running on a blockchain. The initialization uses connection parameters specified in environment variables:
    ```python
    vbc = VBaseClient.create_instance_from_env()
    ```

- Create the test dataset asynchronously.
This factory method constructs a `VBaseDatasetAsync` object using the `asyncio` event loop. Arguments and mechanics are similar to those of `VBaseDataset` object creation.
    ```python
    VBaseDatasetAsync.create(vbc, name=SET_NAME, record_type=VBaseStringObject)
    ```

- Add string record to the dataset asynchronously.
This method makes an object commitment using the `asyncio` event loop. Arguments and mechanics are similar to those of `ds.add_record()` call:
    ```python
    ds.add_record_async("TestRecord")
    ```

- Verify that a given set commitment exists for a given user.
This will typically be called by the data consumer to verify a producer's claims about dataset provenance:
    ```python
    assert ds.verify_commitments()[0]
    ```
