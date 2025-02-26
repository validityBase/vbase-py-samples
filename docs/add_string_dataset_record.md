----
title: Add a String Record to a Dataset
----

<!-- omit in toc -->
# Add a String Record to a Dataset

This sample creates a dataset comprising string records
if one does not exist and adds a record to the dataset.

You can find the implementation in [`add_string_dataset_record.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/add_string_dataset_record.py).

## Summary<a href="#summary" id="summary"></a>

A set is a collection of objects.
A named set of data records is a dataset.
Such datasets can implement any point-in-time (PIT) or bitemporal data
and prove this provenance to third parties.
The sample demonstrates the higher-order vBase dataset and string record abstractions
that hide the details of the object and record content id (CID) calculation (hashing).
This example builds on the `create_set.py` code and omits redundant comments.

## Detailed Description<a href="#detailed-description" id="detailed-description"></a>

- Create a vBase object using a Web3 HTTP commitment service.
The commitment service is a smart contract running on a blockchain.
The initialization uses connection parameters specified in environment variables:
    ```python
    vbc = VBaseClient.create_instance_from_env()
    ```

- Create the test dataset.
If this is a new dataset,
this operation records that the user with the above VBASE_COMMITMENT_SERVICE_PRIVATE_KEY
has created the named dataset.
Dataset creation is idempotent.
If this is an existing dataset, the call is ignored.
Such commitments are used to validate that a given collection of user datasets is complete
and mitigates Sybil attacks (https://en.wikipedia.org/wiki/Sybil_attack).
    ```python
    ds = VBaseDataset(vbc, SET_NAME, VBaseStringObject)
    ```

- Add string record to the dataset.
Records an object commitment for a set record.
A set record commitment establishes that a dataset record with a given CID
has existed at a given time for a given set.
    ```python
    receipt = ds.add_record("TestRecord")
    ```

- Verify that a given set commitment exists for a given user.
This will typically be called by the data consumer to verify
a producer's claims about dataset provenance:
    ```python
    assert ds.verify_commitments()[0]
    ```
