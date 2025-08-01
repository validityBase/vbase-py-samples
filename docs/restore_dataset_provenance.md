# Restore Dataset Provenance

This sample illustrates how a dataset producer can create a dataset and how the provenance of the dataset can be restored after loss during copying or other transformations.

You can find the implementation in [`restore_dataset_provenance.py`](https://github.com/validityBase/vbase-py-samples/blob/main/samples/restore_dataset_provenance.py).

## Summary<a href="#summary" id="summary"></a>

When digital objects are copied across physical media, across cloud environments, and within a cloud environment, they typically lose provenance information such as last modified time. This can lead to severe problems in cases where the timestamps are critical provenance metadata.

For example:
- When security logs are copied, modifications and tampering may not be detectable.
- When financial datasets are copied, their revision timestamps are lost.
- Point-in-time and bitemporal data lose the revision timestamps.

This sample illustrates how such timestamps can be restored for vBase datasets after the underlying digital objects are copied to a new AWS S3 bucket.

## Detailed Description<a href="#detailed-description" id="detailed-description"></a>

- A `.env` file defines the following environment variables for accessing AWS S3 service and vBase services:
    ```shell
    # Forwarder config
    # vBase test forwarder URL
    VBASE_FORWARDER_URL="https://test.api.vbase.com/forwarder/"
    # vBaseTest API key
    VBASE_API_KEY="YOUR_VBASE_API_KEY"

      ```shell
      # Forwarder config
      # vBase test forwarder URL
      VBASE_FORWARDER_URL="https://test.api.vbase.com/forwarder/"
      # vBaseTest API key
      VBASE_API_KEY="YOUR_VBASE_API_KEY"

      # Private key for making commitments
      VBASE_COMMITMENT_SERVICE_PRIVATE_KEY="YOUR_VBASE_COMMITMENT_SERVICE_PRIVATE_KEY"

      # AWS Configuration
      AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
      AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
      ```

- Create a vBase client object using connection parameters specified in environment variables:

  ```python
  vbc = VBaseClient.create_instance_from_env()
  ```

- Create an AWS S3 client object using connection parameters specified in environment variables:

- Create the test dataset.
If this is a new dataset, this operation records that the user with the above VBASE_COMMITMENT_SERVICE_PRIVATE_KEY has created the named dataset. Dataset creation is idempotent. If this is an existing dataset, the call is ignored. Such commitments are used to validate that a given collection of user datasets is complete and mitigates Sybil attacks (https://en.wikipedia.org/wiki/Sybil_attack).
    ```python
    ds = VBaseDataset(vbc, SET_NAME, VBaseIntObject)
    ```

- Add a record to the dataset.
Records an object commitment for a set record. A set record commitment establishes that a dataset record with a given CID has existed at a given time for a given set.
    ```python
    vbase_receipt = ds.add_record(i)
    ```

- Verify that a given set commitment exists for a given user.
This will typically be called by the data consumer to verify a producer's claims about dataset provenance.
    ```python
    assert ds.verify_commitments()[0]
    ```

- Copy a folder to another folder.
This could also be a copy to a different bucket, or a different storage.
    ```python
    copy_s3_bucket(
        boto_client=boto_client,
        source_bucket_name=BUCKET_NAME,
        source_folder_name=FOLDER_NAME,
        destination_bucket_name=BUCKET_NAME,
        destination_folder_name=COPY_FOLDER_NAME,
    )
    ```

      ```python
      vbase_receipt = ds.add_record(i)
      ```

- Attempt to verify the copied objects.
Since these have lost the timestamps and the original provenance information, the checks will fail:
    ```python
    success, l_log = ds_copy.verify_commitments()
    assert not success
    print("Verification log:")
    for log in l_log:
        print(log)
    ```

- Fix the record timestamps using the vBase commitment information and verify the corrected provenance data:
    ```python
    # Fix the timestamps.
    assert ds_copy.try_restore_timestamps_from_index()[0]

- Copy a folder to another folder. This could also be a copy to a different bucket, or a different storage.

      ```python
      copy_s3_bucket(
          boto_client=boto_client,
          source_bucket_name=BUCKET_NAME,
          source_folder_name=FOLDER_NAME,
          destination_bucket_name=BUCKET_NAME,
          destination_folder_name=COPY_FOLDER_NAME,
      )
      ```

- Create a vBase dataset using the copied objects. These objects have lost the original timestamps.

      ```python
      ds_copy = VBaseDataset(vbc, SET_NAME, VBaseIntObject)
      # Load all objects into the dataset.
      ds_copy = init_vbase_dataset_from_s3_objects(
          ds_copy, boto_client, BUCKET_NAME, COPY_FOLDER_NAME
      )
      ```

- Attempt to verify the copied objects. Since these have lost the timestamps and the original provenance information, the checks will fail:

      ```python
      success, l_log = ds_copy.verify_commitments()
      assert not success
      print("Verification log:")
      for log in l_log:
          print(log)
      ```

- Fix the record timestamps using the vBase commitment information and verify the corrected provenance data:

      ```python
      # Fix the timestamps.
      assert ds_copy.try_restore_timestamps_from_index()[0]

      print("Dataset fixed:")
      pprint.pprint(ds_copy.to_pd_object())

      # Verify the records again.
      assert ds_copy.verify_commitments()[0]
      ```
