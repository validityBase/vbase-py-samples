# create_set.py
This sample creates and validates a vBase set.

## Summary
A set is a collection of objects.
A named set of data records is a dataset.
Such datasets can implement any point-in-time (PIT) or bitemporal data
and prove this provenance to third parties.
The sample illustrates low-level vBase set operations.
Low-level set operations expose all vBase features and provide the most control
without the benefit of simplifying higher-level abstractions.

## Detailed Description:

```python
vbc = VBaseClient.create_instance_from_env(".env")
```
Create a vBase object using a Web3 HTTP commitment service.
The commitment service is a smart contract running on a blockchain.
The initialization uses connection parameters specified in environment variables.

```python
receipt = vbc.add_named_set(SET_NAME)
print("add_named_set() receipt:\n%s", pprint.pformat(receipt))
```
Create the test set commitment.
This operation records that the user with the above PRIVATE_KEY
has created the named dataset.
Such commitments are used to validate that a given collection of user datasets is complete
and mitigates Sybil attacks (https://en.wikipedia.org/wiki/Sybil_attack).
Set creation is idempotent.
Multiple creations will log multiple events, but a single set commitment will be recorded.
The returned receipt contains information on the set commitment.
It can be optionally retained to simplify subsequent validation.
All receipts are also available via vBase indexing services.
Since add_set() calls are idempotent,
duplicate calls will be no-ops and will return empty receipts.

```python
assert vbc.user_named_set_exists(vbc.get_default_user(), SET_NAME)
```
Verify that a given set commitment exists for a given user.
This will typically be called by the data consumer to verify
a producer's claims about dataset provenance.
